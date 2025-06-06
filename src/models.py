import json
from transformers import pipeline

class Graphique:
    def __init__(self):
        self.nom = ""
        self.type_score = ""
        self.variables = []
        self.donnees = Donnees("")
        self.modele_ia = ModeleIA("")
        
    def ajouter_variable(self, var:str):
        self.variables.append(var)
        
    def supprimer_variable(self, var:str):
        self.variables.remove(var)
        
    def modifier_typer_score(self, type:str):
        self.type_score = type

    def modifier_donnees(self, fichier):
        self.donnees = Donnees(fichier)
    
    def generer():
        pass
    
class Donnees:
    def __init__(self, fichier:str):
        self.fichier = fichier
        if (fichier != ""):
            # TODO Faire la vérification du contenu du fichier
            with open(fichier, 'r') as file:
                data = json.load(file)
            self.donnees = data
    
class ModeleIA:
    def __init__(self, type_score:str):
        self.nom_modele = type_score
    
    def analyser(self, texte:str):
        pipe = pipeline("text-classification", model=self.nom_modele)
        res = pipe(texte)
        return res[0]["score"]