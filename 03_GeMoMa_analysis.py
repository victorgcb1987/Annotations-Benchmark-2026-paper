import yaml

from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT
from src.timetree import query_timetree


                

def main():
    # GeMoMA_metadata_2026_02_2.yaml
    metadata = yaml.safe_load(open(argv[1], "r"))
            

    





if __name__ == "__main__":
    main()





