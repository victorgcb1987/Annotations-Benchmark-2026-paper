from pathlib import Path


from src.metadata import Species



SERVER_RESULTS_FPATH = Path("/data/shared_space/bombarely_lab/AnnotationBenchmarkProject/BySpecies")
GAQET_prefix = "AnnotationQC_"


FOLDER_TRANSLATE = {""}


def main():
    for filename in SERVER_RESULTS_FPATH.rglob("GAQET.log.txt"):
        species = str(filename).split("/")[6]
        method = str(filename).split("/")[8]
        print(species, method)
        



if __name__ == "__main__":
    main()


