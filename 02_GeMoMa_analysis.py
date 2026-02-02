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
    contributions = {"species_involved": []}
    for line in pipeline_fhand:
        if CONTRIBUTION_LINE in line:
            contribution = line.rstrip().split()[-1]
            if "GenomicData" in contribution:
                contribution = contribution.split("/")[0].replace("GenomicData_", "").replace("_", " ")
                if contribution == "Vitis vinifera NCBI":
                    contribution = "Vitis vinifera"
            else:
                contribution = SPECIES_BY_ANNOT[contribution.rstrip().split("/")[-1]]
            contributions["species_involved"].append(contribution)
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
            divergence = json.loads(line)
            for species_a, species_b in divergence.items():
                if species_a not in divergences:
                    divergences[species_a] = species_b
                else:
                    divergences[species_a][list(species_b.keys())[0]] = species_b.values()
    return divergences                


def update_species_divergence_times(gemoma_benchmarks, species_divergence):
    print(species_divergence)
    for species_a, benchmark in gemoma_benchmarks.items():
        print(benchmark)
        for methods, metadata in gemoma_benchmarks.items():
           for method, features in metadata.items():
            divergences = {}
            print(features["species_involved"])
            for species_b in features["species_involved"]:
                print(species_a, species_b)
                divergences.update({species_b: species_divergence[" ".join(species_a.split("_"))][species_b]})
            features["divergence_times"] = divergences
                

def main():
    divergence_times = []
    metadata = yaml.safe_load(open(argv[1], "r"))
    species_divergence = load_species_divergences(open(argv[2]))
    gemoma_benchmarks = get_gemoma_benchmarks(metadata)
    add_species_contribution(gemoma_benchmarks)
    update_species_divergence_times(gemoma_benchmarks, species_divergence)
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





