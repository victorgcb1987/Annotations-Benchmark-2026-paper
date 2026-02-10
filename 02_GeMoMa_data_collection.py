import json
import pandas as pd
import yaml

from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT
from src.timetree import query_timetree

PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"
PROTOCOL_GeMoMA_PROTOCOL_ATTEMPT = "protocol_GeMoMaPipeline_{}.txt"
GEMOMA_REFERENCE_TABLE = "reference_gene_table.tabular"
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
                reference = Path(metadata["report"]).parents[1] / GEMOMA_REFERENCE_TABLE
                metadata["ref_table"] = str(reference)
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
                print(species_a, species_b)
                for name, times in species_b.items():
                    if species_a not in divergences:
                        divergences[species_a] = {name: {key: (float(value) if value != "NA" else "NA") for key, value in times.items()}}
                    else:
                        divergences[species_a][name] = {name: {key: (float(value) if value != "NA" else "NA") for key, value in times.items()}}
    return divergences


def update_species_divergence_times(gemoma_benchmarks, species_divergence):
    for species_a, benchmark in gemoma_benchmarks.items():
        for method, features in benchmark.items():
            divergences = {}
            for species_b in features["species_involved"]:
                print(species_a, species_b)
                divergences.update({species_b: species_divergence[" ".join(species_a.split("_"))][species_b]})
            features["divergence_times"] = divergences


def  update_contribution_percentage(gemoma_benchmarks):
    for species_a, benchmark in gemoma_benchmarks.items():
        for method, features in benchmark.items():
            ref_table = pd.read_csv(benchmark["ref_table"])
            species_colunnames = [name for name in ref_table.keys().tolist() if name.startswith("reference_species")]
            number_of_genes_annotated = ref_table.shape[0]
            col_count = 0
            for colname in species_colunnames:
                filter = ref_table[ref_table[colname].isnull() == False]
                number_of_genes_annotated_by_species = filter.shape[0]
                features["species_involved"][col_count] = {"species": features["species_involved"][col_count],
                                                           "number_of_genes_annotated (N)": number_of_genes_annotated_by_species,
                                                           "number_of_genes_annotated (%)": number_of_genes_annotated_by_species/number_of_genes_annotated}
                col_count += 1




def main():
    if argv[1] == "get_data":
        metadata = yaml.safe_load(open(argv[3], "r"))
        species_divergence = load_species_divergences(open(argv[3]))
        gemoma_benchmarks = get_gemoma_benchmarks(metadata)
        add_species_contribution(gemoma_benchmarks)
        update_species_divergence_times(gemoma_benchmarks, species_divergence)
        update_contribution_percentage(gemoma_benchmarks)
        with open('GeMoMA_metadata_2026_02_2.yaml', 'w') as outfile:
            yaml.dump(gemoma_benchmarks, outfile, default_flow_style=False)     
    if argv[1] == "load_data":
        metadata = yaml.safe_load(open(argv[2], "r"))
        update_contribution_percentage(gemoma_benchmarks)
        print(gemoma_benchmarks)
        #with open('GeMoMA_metadata_2026_02_10.yaml', 'w') as outfile:
        #    yaml.dump(gemoma_benchmarks, outfile, default_flow_style=False)

        



    





if __name__ == "__main__":
    main()





