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
        self.variables = ["moyennes générales", "appréciations générales"]
        self.donnees = Donnees("")
        self.modele_ia = ModeleIA("")
        self.chargement = Chargement()
        
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
        # Récupération des données
        self.chargement.progession = 0
        self.chargement.est_fini = False
        self.chargement.status = "Récupération des données"
        
        nb_total_donnees = self.donnees.get_nb_total_donnees()
        print("Nombre d'elements : ", nb_total_donnees)
        annees_scolaire = self.donnees.get_annees_scolaire()
        trimestres = []
        resultats = dict()
        for annee_scolaire in annees_scolaire:
            for trimestre in self.donnees.get_trimestres(annee_scolaire):
                trimestres.append(trimestre)

                # Obtenir les moyennes générales
                self.chargement.status = "Récupération de la moyenne générale du " + trimestre + " de l'année scolaire " + annee_scolaire
                
                if not resultats.get("moyennes générales"):
                    resultats["moyennes générales"] = []
                mg = self.donnees.get_moyenne(annee_scolaire, trimestre)
                resultats["moyennes générales"].append(mg)
                
                self.chargement.progession += 1 * 80 / nb_total_donnees

                # Obtenir les appréciations générales
                self.chargement.status = "Récupération de l'appréciation générale du " + trimestre + " de l'année scolaire " + annee_scolaire
                if not resultats.get("appréciations générales"):
                    resultats["appréciations générales"] = [] # Les scores des l'appréciations
                    resultats["appreciations_generales_text"] = [] # Les textes des l'appréciations
                if self.donnees.get_appreciation(annee_scolaire, trimestre) == None or self.donnees.get_appreciation(annee_scolaire, trimestre) == "": # Si il n'y a pas l'appréciation
                    score = None
                elif self.donnees.score_existe(annee_scolaire, trimestre, self.modele_ia.nom_modele): # Si le score avec le modele choisi existe alors on prend le score
                    score = self.donnees.get_score_appreciation(annee_scolaire, trimestre, self.modele_ia.nom_modele)
                else: # Sinon on fait le score et on le stocke dans le JSON
                    ag = self.donnees.get_appreciation(annee_scolaire, trimestre)
                    score = self.modele_ia.analyser(ag)
                    self.donnees.set_score_appreciation(annee_scolaire, trimestre, self.modele_ia.nom_modele, score)
                resultats["appréciations générales"].append(score)
                resultats["appreciations_generales_text"].append(self.donnees.get_appreciation(annee_scolaire, trimestre))

                self.chargement.progession += 1 * 80 / nb_total_donnees

                print(self.chargement.progession)
        
        # Création du graphique
        self.chargement.status = "Création du graphique"
        
        data = go.Figure(layout_yaxis_range=[0,20])
        for nom, valeurs in resultats.items():
            match nom:
                case "moyennes générales":
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                              mode='lines+markers',
                                              name=nom,
                                              hovertemplate="%{y}"
                                            ))

                case "appréciations générales":
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                              customdata=resultats["appreciations_generales_text"],
                                              mode='lines+markers',
                                              name=nom,
                                              hovertemplate="%{customdata}<br>score : %{y}"
                                            ))

                case "appreciations_generales_text":
                    pass

        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        self.chargement.progession = 100
        self.chargement.est_fini = True

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
        """Permet d'avoir toute les années scolaire enregistré dans le fichier

        Returns:
            list[str]: Les années scolaire dans le fichier
        """
        annees = []
        for annee in self.donnees.get("annees_scolaire"):
            annees.append(annee)
        return annees
    
    def get_trimestres(self, annee_scolaire:str) -> list[str]:
        """Permet d'avoir tout les trimestre enregistré d'une année scolaire

        Args:
            annee_scolaire (str): l'année scolaire ou prendre les trimestres

        Returns:
            list[str]: Tout les trimestres enregistré d'une année scolaire
        """
        trimestres = []
        for trimestre in self.donnees["annees_scolaire"][annee_scolaire]["trimestres"]:
            trimestres.append(trimestre)
        return trimestres
    
    def get_moyenne(self, annee_scolaire:str, trimestre:str, matiere:str=None) -> float:
        """Permet d'obtenir la moyenne à partir de l'année scolaire et du trimestre sélectionné. Si aucune matière n'est sélectionné, on choisi la moyenne générale sinon on choisi la moyenne de la matière

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi
            matiere (str, optional): La matière sélectionné. Si aucune, prendre la moyenne générale. none par défault.

        Returns:
            float: La moyenne
        """
        if matiere:
            return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere]["moyenne"]
        return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["moyenne_generale"]
    
    def get_appreciation(self, annee_scolaire:str, trimestre:str, matiere:str = None) -> str:
        """Permet d'obtenir l'appréciation à partir de l'année scolaire et du trimestre sélectionné. Si aucune matière n'est sélectionné, on choisi l'appréciation générale sinon on choisi la moyenne de l'appréciation

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi
            matiere (str, optional): La matière sélectionné. Si aucune, prendre l'appréciation générale. none par défault.

        Returns:
            str: L'appréciation
        """
        if matiere:
            return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere]["appreciation"]
        return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["appreciation_generale"]
    
    def get_score_appreciation(self, annee_scolaire:str, trimestre:str, modele_ia:str, matiere:str = None) -> float:
        """Permet d'obtenir le score d'une appreciation à partir de l'année scolaire et du trimestre sélectionné. Si aucune matière n'est sélectionné, on choisi le score de l'appréciation générale sinon on choisi le score de l'appréciation de la matière choisi

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi
            modele_ia (str): Le modèle d'ia à utiliser
            matiere (str, optional): La matière sélectionné. Si aucune, prendre l'appréciation générale. none par défault.

        Returns:
            float: Le score stocké dans le JSON
        """
        if matiere:
            return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere]["appreciation_score_" + modele_ia]
        return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["appreciation_generale_score_" + modele_ia]
    
    def score_existe(self, annee_scolaire:str, trimestre:str, modele_ia:str, matiere:str = None) -> bool:
        """Permet de savoir si le score d'une appréciation à déjà été calculé

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi
            modele_ia (str): Le modèle d'ia utilisé pour calculer le score
            matiere (str, optional): La matière sélectionné. Si aucune, prendre l'appréciation générale. none par défault.

        Returns:
            bool: Retourne True si le score calculé par l'ia choisi existe, Sinon False
        """
        if matiere:
            return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere].get("appreciation_score_" + modele_ia) != None
        else:
            return self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre].get("appreciation_generale_score_" + modele_ia) != None
            
    
    def set_score_appreciation(self, annee_scolaire:str, trimestre:str, modele_ia:str, score:float, matiere:str = None):
        """Ajoute le score dans le JSON

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi
            modele_ia (str): Le modèle d'ia utilisé pour calculer le score
            score (float): Le score à mettre dans le JSON
            matiere (str, optional): La matière sélectionné. Si aucune, prendre l'appréciation générale. none par défault.
        """
        if matiere:
            self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere]["appreciation_score_" + modele_ia] = score
        else:
            self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["appreciation_generale_score_" + modele_ia] = score
        with open(self.fichier, 'r+') as f:
            f.seek(0)
            json.dump(self.donnees, f, indent=4)
            f.truncate()
    
    def get_nb_total_donnees(self) -> int:
        total = 0
        for annee_scolaire in self.donnees["annees_scolaire"]:
            for trimestre in self.donnees["annees_scolaire"][annee_scolaire]["trimestres"]:
                # On va prendre toute les "feuilles" dans un trimestre on enleve juste 
                # les feuilles "score" (car je considère que score et appréciation représente 
                # la même données) et "matiere" puis on prend tout les matières et on les 
                # multiplies par deux car il y a deux données par matière 
                total += (len(self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]) - 2) + len(self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"]) * 2
        
        return total
    
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
        """Analyse et donne un score /20 à un texte à partir du modele d'IA sélectionné

        Args:
            texte (str): Le texte à analyser

        Returns:
            float: Le score /20 attribué au texte
        """
        pipe = pipeline("text-classification", model=self.nom_modele, top_k=None)
        res = pipe(texte)
        for scores in res[0]:
            if scores["label"].upper() == "POSITIVE":
                return scores["score"] *20
            
class Chargement:
    def __init__(self):
        self.progession = 0
        self.est_fini = False
        self.status = ""