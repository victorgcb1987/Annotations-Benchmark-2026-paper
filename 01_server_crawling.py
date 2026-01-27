import os

from pathlib import Path


from src.metadata import Species



SERVER_RESULTS_FPATH = Path("/data/shared_space/bombarely_lab/AnnotationBenchmarkProject/BySpecies")
GAQET_prefix = "AnnotationQC_"


FOLDER_TRANSLATE = {""}


def main():
    gaqet_logs = list(SERVER_RESULTS_FPATH.rglob("GAQET.log.txt"))
    gaqet_logs.sort(key=os.path.getmtime)
    for filename in gaqet_logs:
        species = str(filename).split("/")[6]
        method = str(filename).split("/")[8]
        print(species, method, filename)
        



if __name__ == "__main__":
    main()


