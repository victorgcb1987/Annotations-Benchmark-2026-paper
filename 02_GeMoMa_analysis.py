import yaml

from sys import argv

from src.docs import SPECIES_TRANSLATION

PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"


def main():
    metadata = yaml.safe_load(open(argv[1], "r"))
    print(metadata)



if __name__ == "__main__":
    main()





