import json
import yaml



from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT
from src.metadata import get_taxonomic_data



SERVER_RESULTS_FPATH = Path("/data/shared_space/bombarely_lab/AnnotationBenchmarkProject/BySpecies")
GAQET_prefix = "AnnotationQC_"


FOLDER_TRANSLATE = {""}

NAME_FIX = {"Alisma_plantagoaquatica": "Alisma_plantago-aquatica",
            "Adiantum_capillusveneris": "Adiantum_capillus-veneris"}

CONTRIBUTION_LINE = "annotation (Reference annotation file (GFF or GTF), which contains gene models annotated in the reference genome"

def load_species_divergences(fhand):
    divergences = {}
    for line in fhand:
        if line:
            line = line.rstrip().replace(" MYA", "")
            divergence = json.loads(line)
            for species_a, species_b in divergence.items():
                for name, times in species_b.items():
                    if species_a not in divergences:
                        divergences[species_a] = {name: {key: (float(value) if value != "NA" else "NA") for key, value in times.items()}}
                    else:
                        divergences[species_a][name] = {name: {key: (float(value) if value != "NA" else "NA") for key, value in times.items()}}
    return divergences


def get_contributions(pipeline_fhand):
    contributions = []
    for line in pipeline_fhand:
        if CONTRIBUTION_LINE in line:
            contribution = line.rstrip().split()[-1]
            if "GenomicData" in contribution:
                contribution = contribution.split("/")[0].replace("GenomicData_", "").replace("_", " ")
                if contribution == "Vitis vinifera NCBI":
                    contribution = "Vitis vinifera"
            else:
                contribution = SPECIES_BY_ANNOT[contribution.rstrip().split("/")[-1]]
            contributions.append(contribution)
    return contributions



def main():
    annots = {}
    species_divergence = load_species_divergences(open(argv[1]))
    gemoma_annotations = list(SERVER_RESULTS_FPATH.rglob("final_annotation*.gff"))
    for filename in gemoma_annotations:
        filename = Path(filename)
        species_a = str(filename).split("/")[6]
        if species_a not in annots:
            species_a = NAME_FIX.get(species_a, species_a)
            annots[species_a] = {}
        print(filename)
        pipeline =  str(sorted(list(filename.parent.glob("*GeMoMaPipeline*")),reverse=True)[0])
        with open(pipeline) as pipeline_fhand:
            contributions = get_contributions(pipeline_fhand)
            if len(contributions) == 1:
                species_b = contributions[0]
            else:
                species_b = "comb_"+ "_".join(contributions)
        print(filename)
        print(filename.parent)
        print(filename.parent.glob("*.tabular"))
        print(species_a, species_b)
        annots[species_a][species_b] = {"pipeline_log": pipeline,
                                        "ref_table": str(sorted(list(filename.parent.glob("*tabular")),reverse=True)[0]), 
                                        "annot_file": str(sorted(list(filename.parent.glob("final_annotation*.gff")),reverse=True)[0]),
                                        }
        if "comb_" not in species_b:
            annots[species_a][species_b]["divergence_time"] = species_divergence[species_a][species_b]


    with open('GeMoMA_metadata_2026_03_03.yaml', 'w') as outfile:
        yaml.dump(annots, outfile, default_flow_style=False, sort_keys=False)
        


if __name__ == "__main__":
    main()


