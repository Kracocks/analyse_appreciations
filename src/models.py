import json
import plotly
import plotly.graph_objs as go
import numpy as np
import pandas as pd
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
        self.donnees.modfier_fichier(fichier)
        
    def modifier_modele(self, modele):
        self.modele_ia.modifier_modele(modele)
    
    def generer(self):
        N = 40
        x = np.linspace(0, 1, N)
        y = np.random.randn(N)
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe

        data = [
            go.Bar(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]

        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON
        
    
class Donnees:
    def __init__(self, fichier:str):
        self.modfier_fichier(fichier)

    def modfier_fichier(self, new_fichier:str):
        self.fichier = new_fichier
        if (self.fichier != ""):
            with open(self.fichier, 'r') as file:
                data = json.load(file)
                if self.verifier_contenu(data):
                    self.donnees = data
            
    def verifier_contenu(self, donnee) -> bool:
        # TODO Faire la vérification du contenu du fichier
        return True
    
class ModeleIA:
    def __init__(self, type_score:str):
        self.nom_modele = type_score
        
    def modifier_modele(self, new_nom_modele:str):
        self.nom_modele = new_nom_modele
    
    def analyser(self, texte:str):
        pipe = pipeline("text-classification", model=self.nom_modele)
        res = pipe(texte)
        return res[0]["score"]