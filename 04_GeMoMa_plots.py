import matplotlib.pyplot as plt
import pandas as pd
import yaml

import seaborn as sns


from pathlib import Path
from sys import argv

from src.docs import SPECIES_BY_ANNOT
from src.timetree import query_timetree

NO_TIMETREE = ["Lathyrus oleraceus"]



def get_divergence_time_and_contribution(gemoma_benchmarks):
    contributions = {"AnnotatedSpecies": [], "AnnotatingSpecies":[], 
                     "AnnotatedClass": [], "AnnotatingClass": [],
                     "AnnotatedFamily": [], "AnnotatingFamily": [],
                     "AnnotatedGenus": [], "AnnotatingGenus": [],  
                     "DivergenceTime": [], "Contribution": []}

    for species_a, benchmarks in gemoma_benchmarks.items():
        for benchmark, features in benchmarks.items():
            if benchmark == "tax_classification":
                continue
            for species in features["species_involved"]:
                contr_species = species["tax_classification"]["species"]
                if contr_species in NO_TIMETREE:
                    continue

                contributions["AnnotatedSpecies"].append(species_a)
                contributions["AnnotatingSpecies"].append(species["tax_classification"]["species"])

                contributions["AnnotatedClass"].append(benchmarks["tax_classification"]["class"])
                contributions["AnnotatingClass"].append(species["tax_classification"]["class"])

                contributions["AnnotatedFamily"].append(benchmarks["tax_classification"]["family"])
                contributions["AnnotatingFamily"].append(species["tax_classification"]["family"])

                contributions["AnnotatedGenus"].append(benchmarks["tax_classification"]["genus"])
                contributions["AnnotatingGenus"].append(species["tax_classification"]["genus"])
                print("XXXXX")
                print(species_a, contr_species)
                print(features["divergence_times"])
                print("XXXXXX")
                try:
                    contributions["DivergenceTime"].append(features["divergence_times"][contr_species][contr_species]["median_time"])
                except KeyError:
                    contributions["DivergenceTime"].append(features["divergence_times"][contr_species]["median_time"])

                contributions["Contribution"].append(species["number_of_genes_annotated (%)"])


    return pd.DataFrame.from_dict(contributions) 

def main():
    # GeMoMA_metadata_2026_02_11.yaml
    gemoma_benchmarks = yaml.safe_load(open(argv[1], "r"))
    dataframe = get_divergence_time_and_contribution(gemoma_benchmarks)
    dataframe.to_csv("test.tsv", sep="\t", index=False)
    colours = {True: "#44bd32", False: "#273c75"}

    dataframe["Same Family"] = dataframe["AnnotatedFamily"] == dataframe["AnnotatingFamily"]
    sns.set_theme()
    g = sns.lmplot(data=dataframe,
    y="Contribution", x="DivergenceTime", hue="AnnotatedSpecies",
    height=5, ci=None
)

    # print(dataframe)
    # fig, ax = plt.subplots()
    # y = dataframe["Contribution"]
    # x = dataframe["DivergenceTime"]
    # ax.scatter(x, y, alpha=0.3, color=dataframe['Same Family'].replace(colours), edgecolors='none')
    
    # ax.legend()
    # ax.grid(False)
    plt.ylim(0, 110)
    plt.show()

    
            

    





if __name__ == "__main__":
    main()





