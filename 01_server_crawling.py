import os
import re


from pathlib import Path


from src.metadata import Species



SERVER_RESULTS_FPATH = Path("/data/shared_space/bombarely_lab/AnnotationBenchmarkProject/BySpecies")
GAQET_prefix = "AnnotationQC_"


FOLDER_TRANSLATE = {""}


def main():
    annots = {}
    gaqet_logs = list(SERVER_RESULTS_FPATH.rglob("GAQET.log.txt"))
    gaqet_logs.sort(key=os.path.getmtime, reverse=True)
    for filename in gaqet_logs:
        species = str(filename).split("/")[6]
        if species not in annots:
            annots[species] = {}
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
                annots[species][method] = {"report": filename, 
                                          "gaqet_results": list(filename.parent.glob("*.stats.tsv"))[0]}
            except IndexError:
                print(filename)

    print(annots)
        



if __name__ == "__main__":
    main()


