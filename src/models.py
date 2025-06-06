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
        self.donnees = Donnees(fichier)
        
    def modifier_modele(self, modele):
        self.modele_ia = ModeleIA(modele)
    
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