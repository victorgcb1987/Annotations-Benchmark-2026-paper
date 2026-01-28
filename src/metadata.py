import json
from subprocess import run




# class Species:

#     def __init__(self):
#         self.species = None
#         self.genus = None
#         self.familiy = None
#         self.tax_class = None
#         self.annot_Refseq = None
#         self.annot_Community = None
#         self.annot_StringTie = None
#         self.annot_Transdecoder = None
#         self.annot_GeMoMA = None
#         self.Helixer = None
#         self.Braker3 = None
#         self.Maker = None
#         self.Eviann = None
#         self.Egap_user = None
#         self.Annevo = None


def get_taxonomic_data(species):    
    cmd = "datasets summary taxonomy taxon \"{}\"".format(species).replace("_", " ")
    metadata = run(cmd, shell=True, capture_output=True)
        
    if metadata.returncode == 0:
        metadata = json.loads(metadata.stdout)
        tax_metadata = metadata["reports"][0]["taxonomy"]["classification"]
        species = tax_metadata["species"]["name"]
        genus = tax_metadata["genus"]["name"]
        family = tax_metadata["family"]["name"]
        tax_class = tax_metadata["class"]["name"]
        return {"species": species, "genus": genus, "family": family,
                "class": tax_class}






        



    

