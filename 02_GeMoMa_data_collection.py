import json
import pandas as pd
import yaml

from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT
from src.timetree import query_timetree
from src.metadata import get_taxonomic_data

PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"
PROTOCOL_GeMoMA_PROTOCOL_ATTEMPT = "protocol_GeMoMaPipeline_{}.txt"
GEMOMA_REFERENCE_TABLE = "reference_gene_table.tabular"
GEMOMA_REFERENCE_TABLE_ATTEMPT = "reference_gene_table_{}.tabular"
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
            if method == "tax_classification":
                continue
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
                if not reference.is_file():
                    found = False
                    start = 1
                    while not found or start > 10:
                        reference = Path(metadata["report"]).parents[1] / GEMOMA_REFERENCE_TABLE_ATTEMPT.format(start)
                        if reference.is_file():
                            found = True
                        else:
                            start += 1
                    if not found:
                        print("Not found", reference)
                metadata["ref_table"] = str(reference)
                if species not in gemoma_annnots:
                    if species == "Vitis vinifera NCBI":
                        species = "Vitis vinifera"
                    gemoma_annnots[species] = {method: metadata}
                    gemoma_annnots[species]["tax_classification"] = get_taxonomic_data(species)
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
            if method == "tax_classification":
                continue
            divergences = {}
            for species_b in features["species_involved"]:
                print(species_a, species_b)
                divergences.update({species_b: species_divergence[" ".join(species_a.split("_"))][species_b]})
            features["divergence_times"] = divergences


def update_contribution_percentage(gemoma_benchmarks, source_annot_stats):
    with open(source_annot_stats) as fhand:
        number_of_genes_source = {line.split()[0]: int(line.split([1])) for line in fhand if not line.starstwith("Species")}
    for species_a, benchmark in gemoma_benchmarks.items():
        number_of_genes_annotated_by_species = number_of_genes_source[" ".join(species_a.split("_"))]
        for method, features in benchmark.items():
            if method == "tax_classification":
                continue
            ref_table = pd.read_csv(features["ref_table"], delimiter="\t")
            species_colunnames = [name for name in ref_table.keys().tolist() if name.startswith("reference_species")]
            number_of_genes_annotated = ref_table.shape[0]
            col_count = 0
            for colname in species_colunnames:
                other_cols = [other_colname for other_colname in species_colunnames if other_colname != colname]
                mask_empty = ref_table.isnull()  |  (ref_table == "")
                unique_annots = int((~mask_empty[colname] & mask_empty[[c for c in other_cols if c != colname]].all(axis=1)).sum())
                common_annotated = int(~mask_empty[species_colunnames].all(axis=1).sum()) 

                features["species_involved"][col_count] = {"species": features["species_involved"][col_count],
                                                           "number_of_genes_annotated (N)": number_of_genes_annotated_by_species,
                                                           "number_of_genes_annotated (%)": (number_of_genes_annotated_by_species/number_of_genes_annotated) * 100,
                                                           "number_of_unique_genes_annotated (N)": unique_annots,
                                                           "number_of_unique_genes_annotated (%)": (unique_annots/number_of_genes_annotated) * 100,
                                                           "number_of_common_genes_annotated (N)": common_annotated,
                                                           "number_of_common_genes_annotated (%)": (common_annotated /number_of_genes_annotated)*100,
                                                           "tax_classification": get_taxonomic_data(features["species_involved"][col_count])}
                col_count += 1


def main():
    metadata = yaml.safe_load(open(argv[1], "r"))
    species_divergence = load_species_divergences(open(argv[2]))
    gemoma_benchmarks = get_gemoma_benchmarks(metadata)
    add_species_contribution(gemoma_benchmarks)
    update_species_divergence_times(gemoma_benchmarks, species_divergence)
    update_contribution_percentage(gemoma_benchmarks)
    with open('GeMoMA_metadata_2026_02_12.yaml', 'w') as outfile:
        yaml.dump(gemoma_benchmarks, outfile, default_flow_style=False, sort_keys=False)     




if __name__ == "__main__":
    main()





