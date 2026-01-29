import yaml

from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT

PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"
PROTOCOL_GeMoMA_PROTOCOL_ATTEMPT = "protocol_GeMoMaPipeline_{}.txt"
CONTRIBUTION_LINE = "annotation (Reference annotation file (GFF or GTF), which contains gene models annotated in the reference genome"


def get_contributions(pipeline_fhand):
    contributions = {}
    for line in pipeline_fhand:
        if CONTRIBUTION_LINE in line:
            contribution = line.rstrip().split()[-1]
            if "GenomicData" in contribution:
                contribution = contribution.split("/")[0].replace("GenomicData_", "").replace("_", " ")
                contributions[contribution] = {"distance": 0}
            else:
                contribution = SPECIES_BY_ANNOT[contribution.rstrip().split("/")[-1]]
                contributions[contribution] = {"distance": 0}
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
            print(root_path)
            path = get_correct_pipeline_path(root_path)
            print(path)
            contributions = get_contributions(open(path))
            print(contributions)
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
    add_species_contribution(helixer_benchmarks)
    print(helixer_benchmarks)


if __name__ == "__main__":
    main()





