import json
import plotly
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from transformers import pipeline

class Graphique:
    def __init__(self):
        """Le contructeur de la classe Graphique
        """
        self.nom = ""
        self.variables = []
        self.donnees = Donnees("")
        self.modele_ia = ModeleIA("")
        
    def ajouter_variable(self, var:str):
        """Ajouter une varible parmis les variables qui seront affiché dans le graphique

        Args:
            var (str): La variable à ajouter
        """
        self.variables.append(var)
        
    def supprimer_variable(self, var:str):
        """Supprimer une varibles parmis les variables qui seront affiché sur le graphique

        Args:
            var (str): La variable à supprimer
        """
        self.variables.remove(var)

    def modifier_donnees(self, fichier:str):
        """Modifier le fichier utilisé pour afficher les données dans un graphique. Le fichier doit être un fichier JSON qui doit respecter une architecture.

        Args:
            fichier (str): Le nouveau fichier utilisé
        """
        self.donnees.modfier_fichier(fichier)
        
    def modifier_modele(self, modele:str):
        """Modifier le modèle d'IA utilisé pour donner un score au appréciations

        Args:
            modele (str): Le nouveau modèle d'IA
        """
        self.modele_ia.modifier_modele(modele)
    
    def generer(self) -> str:
        """Génère un graphique à partir des données, variables et modèle d'IA

        Returns:
            str: Le graphique généré
        """
        N = len(self.donnees.get_trimestres())
        x = [t for t in self.donnees.get_trimestres()]
        y = self.donnees.get_moyennes_generales()
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe

        data = [
            go.Line(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]

        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON
        
    
class Donnees:
    def __init__(self, fichier:str):
        """Le constructeur de la classe Donnees

        Args:
            fichier (str): Le fichier à charger
        """
        self.modfier_fichier(fichier)

    def modfier_fichier(self, new_fichier:str) -> bool:
        """Modifier les donnée utilisé par l'application à partir d'un fichier JSON. Le JSON doit respecter une architecture et renverra False si l'architecture n'est pas correcte ou si le fichier n'est pas un JSON

        Args:
            new_fichier (str): Le nouveau fichier avec les données à utiliser.

        Returns:
            bool: Renvoi True si les données ont été modifiées. Sinon False.
        """
        self.fichier = new_fichier
        if (self.fichier != ""):
            with open(self.fichier, 'r') as file:
                data = json.load(file)
                if (self.verifier_contenu(data)):
                    self.donnees = data
            
    def verifier_contenu(self, donnee:any) -> bool:
        """Vérifie si l'architecture du JSON correspond à celui attendu par l'application

        Args:
            donnee (any): Les données du fichier JSON

        Returns:
            bool: Renvoi True si l'architecture est respectée. Sinon False.
        """
        # TODO Faire la vérification du contenu du fichier
        return True
    
    def get_annees_scolaire(self) -> list[str]:
        annees = []
        for annee in self.donnees.get("annees_scolaire"):
            annees.append(annees)
        return annees
    
    def get_trimestres(self) -> list[str]:
        trimestres = []
        for annee in self.donnees.get("annees_scolaire"):
            for trimestre in self.donnees["annees_scolaire"][annee]["trimestres"]:
                trimestres.append(trimestre)
        return trimestres
    
    def get_moyennes_generales(self) -> list[float]:
        """Permet d'obtenir toute les moyennes générales à partir du fichier séléctionné 

        Returns:
            list[float]: Les moyennes générales
        """
        moyennes = []
        for annee in self.donnees.get("annees_scolaire"):
            if (annee != "No data"):        
                for trimestre in self.donnees["annees_scolaire"][annee]["trimestres"]:
                    moyenne = self.donnees["annees_scolaire"][annee]["trimestres"][trimestre]["moyenne_generale"]
                    moyennes.append(moyenne)
        return moyennes
    
    
class ModeleIA:
    def __init__(self, type_score:str):
        """Le constructeur de la classe ModeleIA

        Args:
            type_score (str): Le modele d'IA
        """
        self.nom_modele = type_score
        
    def modifier_modele(self, new_nom_modele:str):
        """Modifier le modèle d'IA utilisé par l'application

        Args:
            new_nom_modele (str): Le nouveau modèle d'IA utilisé
        """
        self.nom_modele = new_nom_modele
    
    def analyser(self, texte:str) -> float:
        """Analyse et donne un score à un texte à partir du modele d'IA sélectionné

        Args:
            texte (str): Le texte à analyser

        Returns:
            float: Le score attribué au texte
        """
        pipe = pipeline("text-classification", model=self.nom_modele)
        res = pipe(texte)
        return res[0]["score"]