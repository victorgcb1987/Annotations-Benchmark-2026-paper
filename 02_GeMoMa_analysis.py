import yaml

from sys import argv

from src.docs import SPECIES_BY_ANNOT

PROTOCOL_GeMoMA_PROTOCOL = "protocol_GeMoMaPipeline.txt"

def get_species_annotated_with_helixer(yaml_fhand):
    helixer_annnots = {}
    for species, annot in yaml_fhand.items():
        for method, metadata in annot.items():
            if "HELIXER" in method:
                if species not in helixer_annnots:
                    helixer_annnots[species] = {method: metadata}
                else:
                    helixer_annnots[species][method] = metadata
    return helixer_annnots



def main():
    metadata = yaml.safe_load(open(argv[1], "r"))
    helixer_annots = get_species_annotated_with_helixer(metadata)
    print(helixer_annots)


if __name__ == "__main__":
    main()





