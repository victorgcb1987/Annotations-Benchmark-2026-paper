import yaml

from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT

PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"
PROTOCOL_GeMoMA_PROTOCOL_1 = "protocol_GeMoMaPipeline_1.txt"
CONTRIBUTION_LINE = "annotation (Reference annotation file (GFF or GTF), which contains gene models annotated in the reference genome"


def get_contributions(pipeline_fhand):
    contributions = {}
    for line in pipeline_fhand:
        if CONTRIBUTION_LINE in line:
            contribution = line.rstrip().split()[-1]
            if "GenomicData" in contribution:
                contribution = contribution.split("/")[0].replace("GenomicData_", "").replace("_", " ")
            else:
                contribution = SPECIES_BY_ANNOT[contribution.rstrip().split("/")[-1]]
                contributions[contribution] = {"distance": 0}
    return contributions


def add_species_contribution(benchmarks):
    for species, benchmark in benchmarks.items():
        for method, metadata in benchmark.items():
            try:
                contribution_fhand = open(Path(metadata["report"]).parents[1] / PROTOCOL_GeMoMA_PROTOCOL)
            except FileNotFoundError:
                contribution_fhand = open(Path(metadata["report"]).parents[1] / PROTOCOL_GeMoMA_PROTOCOL_1)
            contributions = get_contributions(contribution_fhand)
            metadata.update(contributions)



def get_helixer_benchmarks(yaml_fhand):
    helixer_annnots = {}
    for species, annot in yaml_fhand.items():
        for method, metadata in annot.items():
            if "GeMoMa" in method:
                if species not in helixer_annnots:
                    helixer_annnots[species] = {method: metadata}
                else:
                    helixer_annnots[species][method] = metadata
    return helixer_annnots



def main():
    metadata = yaml.safe_load(open(argv[1], "r"))
    helixer_benchmarks = get_helixer_benchmarks(metadata)
    helixer_benchmarks = add_species_contribution(helixer_benchmarks)
    print(helixer_benchmarks)


if __name__ == "__main__":
    main()





