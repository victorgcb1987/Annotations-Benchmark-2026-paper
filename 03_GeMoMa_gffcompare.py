import json
import pandas as pd
import yaml

from pathlib import Path
from sys import argv

from src.docs import SOURCE_ANNOTS_FOR_GEMOMA
from src.timetree import query_timetree
from src.metadata import get_taxonomic_data
from src.gffcompare import run_gffcompare


PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"
PROTOCOL_GeMoMA_PROTOCOL_ATTEMPT = "protocol_GeMoMaPipeline_{}.txt"
GEMOMA_REFERENCE_TABLE = "reference_gene_table.tabular"
GEMOMA_REFERENCE_TABLE_ATTEMPT = "reference_gene_table_{}.tabular"
GEMOMA_ANNOT = "final_annotation.gff"
GEMOMA_ANNOT_ATTEMPT = "final_annotation_{}.gff"
CONTRIBUTION_LINE = "annotation (Reference annotation file (GFF or GTF), which contains gene models annotated in the reference genome"


#run_gffcompare(outbase, source_annotation, target_annotation)
def add_gffcompare_results(benchmarks, outbase):
    for species_a, benchmark in benchmarks.items():
        for annotation, annotation_features in benchmark.items():
            if annotation == "tax_classification":
                continue
            name = "GeMoMa_{}-{}".format(species_a, annotation)
            results = run_gffcompare(outbase, SOURCE_ANNOTS_FOR_GEMOMA[species_a], Path(annotation_features["annot_file"]), name)
            print(results)



def main():
    gemoma_benchmarks = yaml.safe_load(open(argv[1], "r"))
    out_base = Path(argv[2])
    add_gffcompare_results(gemoma_benchmarks, out_base)
    #with open('GeMoMA_metadata_2026_02_27.yaml', 'w') as outfile:
    #    yaml.dump(gemoma_benchmarks, outfile, default_flow_style=False, sort_keys=False)
    



if __name__ == "__main__":
    main()





