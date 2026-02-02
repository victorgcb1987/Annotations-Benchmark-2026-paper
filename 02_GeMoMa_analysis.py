import json
import pickle
import yaml

from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT
from src.timetree import query_timetree

PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"
PROTOCOL_GeMoMA_PROTOCOL_ATTEMPT = "protocol_GeMoMaPipeline_{}.txt"
CONTRIBUTION_LINE = "annotation (Reference annotation file (GFF or GTF), which contains gene models annotated in the reference genome"


def get_contributions(pipeline_fhand):
    contributions = {"species_involved": {}}
    for line in pipeline_fhand:
        if CONTRIBUTION_LINE in line:
            contribution = line.rstrip().split()[-1]
            if "GenomicData" in contribution:
                contribution = contribution.split("/")[0].replace("GenomicData_", "").replace("_", " ")
                if contribution == "Vitis vinifera NCBI":
                    contribution = "Vitis vinifera"
                contributions["species_involved"][contribution] = {"distance": 0}
            else:
                contribution = SPECIES_BY_ANNOT[contribution.rstrip().split("/")[-1]]
                contributions["species_involved"][contribution] = {"distance": 0}
    return contributions


def get_correct_pipeline_path(root_path):
    pipeline_path = root_path / PROTOCOL_GeMoMA_PROTOCOL
    if pipeline_path.is_file():
        return pipeline_path
    else:
        found = False
        start = 1
        while not found or start > 10:
            pipeline_path = root_path / PROTOCOL_GeMoMA_PROTOCOL_ATTEMPT.format(start)
            if pipeline_path.is_file():
                found = True
            else:
                start += 1
        if not found:
            print("Not found", root_path)
            return None
        else:
            return pipeline_path


def add_species_contribution(benchmarks):
    for species, benchmark in benchmarks.items():
        for method, metadata in benchmark.items():
            root_path = Path(metadata["report"]).parents[1]
            path = get_correct_pipeline_path(root_path)
            contributions = get_contributions(open(path))
            metadata.update(contributions)



def get_gemoma_benchmarks(yaml_fhand):
    gemoma_annnots = {}
    for species, annot in yaml_fhand.items():
        for method, metadata in annot.items():
            if "GeMoMa" in method:
                if species not in gemoma_annnots:
                    if species == "Vitis vinifera NCBI":
                        species = "Vitis vinifera"
                    gemoma_annnots[species] = {method: metadata}
                else:
                    gemoma_annnots[species][method] = metadata
    return gemoma_annnots


def get_all_species_combinations(gemoma_benchmarks):
    combinations = []
    for species, methods in gemoma_benchmarks.items():
        for method, features in methods.items():
            contributions = features.get("species_involved", None)
            if contributions == None:
                print("This method is broken", species, method)
                continue
            else:
                for species_involved in contributions:
                    combinations.append((" ".join(species.split("_")), species_involved))
    return set(combinations)


def load_species_divergences(fhand):
    divergences = {}
    for line in fhand:
        if line:
            line = line.rstrip().replace(" MYA", "")
            print(line)
            divergence = json.loads(line)
            for species_a, species_b in divergence.items():
                if species_a not in divergences:
                    divergences[species_a] = species_b
                else:
                    divergences[species_a][list(species_b.keys())[0]] = species_b.values()
    return divergences                




def main():
    divergence_times = []
    metadata = yaml.safe_load(open(argv[1], "r"))
    species_divergence = load_species_divergences(open(argv[2]))
    print(species_divergence)
    gemoma_benchmarks = get_gemoma_benchmarks(metadata)
    add_species_contribution(gemoma_benchmarks)
    print(gemoma_benchmarks)
    # #species_combinations = get_all_species_combinations(gemoma_benchmarks)
    # with open(argv[2], "rb") as fhand:
    #     check_load = pickle.load(fhand)
    # for comb in check_load:
    #     divergence_time = query_timetree(comb[0], comb[1])
    #     if not divergence_time is None:
    #         divergence_times.append(divergence_time)
    #     print(divergence_time)
    # with open("divergence_times.pkl", "wb") as fhand:
    #     pickle.dump(divergence_times, fhand)




if __name__ == "__main__":
    main()





