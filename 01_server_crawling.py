from pathlib import Path


from src.metadata import Species



SERVER_RESULTS_FPATH = Path("/data/shared_space/bombarely_lab/AnnotationBenchmarkProject/BySpecies")
GAQET_prefix = "AnnotationQC_"


def main():
    for filename in SERVER_RESULTS_FPATH.rglob("GAQET.log.txt"):
        print(filename)



if __name__ == "__main__":
    main()


