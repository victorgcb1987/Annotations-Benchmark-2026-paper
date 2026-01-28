import yaml
import os
import re


from pathlib import Path


from src.metadata import get_taxonomic_data



SERVER_RESULTS_FPATH = Path("/data/shared_space/bombarely_lab/AnnotationBenchmarkProject/BySpecies")
GAQET_prefix = "AnnotationQC_"


FOLDER_TRANSLATE = {""}

NAME_FIX = {"Alisma_plantagoaquatica": "Alisma_plantago-aquatica",
            "Adiantum_capillusveneris": "Adiantum_capillus-veneris"}

def main():
    annots = {}
    gaqet_logs = list(SERVER_RESULTS_FPATH.rglob("GAQET.log.txt"))
    gaqet_logs.sort(key=os.path.getmtime, reverse=True)
    for filename in gaqet_logs:
        species = str(filename).split("/")[6]
        if species not in annots:
            species = NAME_FIX.get(species, species)
            annots[species] = get_taxonomic_data(species)
            print(species, annots[species])

        method = str(filename).split("/")[8]
        if method == "01_BRAKER3":
            method = str(filename).split("/")[9]
            method = "_".join(method.split("_")[1:])
        if "GeMoMa_" in method:
            method = re.search(r'([^_]+_[^_]+)$', method)
            method = method.group(1)
        if "NCBI_GCF" in method:
            method =  "NCBI_RefSeq"
        if "NCBI_GCA" in method:
            method = "NCBI_UserSubmitted"
        if "HELIX" in method:
            method = "_".join(method.split("_")[1:])
        if method not in annots[species]:
            try:
                annots[species][method] = {"report": str(filename), 
                                          "gaqet_results": str(list(filename.parent.glob("*.stats.tsv"))[0])}
            except IndexError:
                print(filename)

    with open('annotations_metada_2026_01_27.yml', 'w') as outfile:
        yaml.dump(annots, outfile, default_flow_style=False)
        



if __name__ == "__main__":
    main()


