import pandas as pd
import yaml

from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT
from src.timetree import query_timetree



def get_divergence_time_and_contribution(gemoma_benchmarks):
    contributions = {"divergence_time":[], "contribution":[],
                     "species_annotated": [], "species_annotating": [],
                     "unique_contribution": }

    for species_a, benchmark in gemoma_benchmarks.items():
        for method, features in benchmark.items():
            for species in features["species_involved"]:
                contributions["contribution"].append(species['number_of_genes_annotated (%)'])





                

def main():
    # GeMoMA_metadata_2026_02_11.yaml
    gemoma_benchmarks = yaml.safe_load(open(argv[1], "r"))
    get_divergence_time_and_contribution(gemoma_benchmarks)

    
            

    





if __name__ == "__main__":
    main()





