import json
import plotly
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from transformers import pipeline
from datasets import load_dataset
from math import sqrt
import time

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

        start_time = time.time()

        nb_total_donnees = self.donnees.get_nb_total_donnees()
        print("Nombre d'elements : ", nb_total_donnees)
        annees_scolaire = self.donnees.get_annees_scolaire()
        matieres = self.donnees.get_all_matieres()
        trimestres = []
        resultats = dict()
        for annee_scolaire in annees_scolaire:
            for trimestre in self.donnees.get_trimestres(annee_scolaire):
                trimestres.append(trimestre + " année " + annee_scolaire)

                # Obtenir les moyennes générales
                self.chargement.status = "Récupération de la moyenne générale du " + trimestre + " de l'année scolaire " + annee_scolaire

                if resultats.get("moyennes générales") == None:
                    resultats["moyennes générales"] = []
                mg = self.donnees.get_moyenne(annee_scolaire, trimestre)
                resultats["moyennes générales"].append(mg)

                self.chargement.progession += 1 * 80 / nb_total_donnees

                # Obtenir les appréciations générales
                self.chargement.status = "Récupération de l'appréciation générale du " + trimestre + " de l'année scolaire " + annee_scolaire
                appreciation = self.donnees.get_appreciation(annee_scolaire, trimestre)
                if resultats.get("appréciations générales") == None:
                    resultats["appréciations générales"] = {"textes": [], "scores": []}
                resultats["appréciations générales"]["textes"].append(appreciation)

                self.chargement.progession += 1 * 80 / nb_total_donnees
                
                for matiere in matieres:
                    # Obtenir les moyennes de la matière
                    if resultats.get("moyennes " + matiere) == None:
                        resultats["moyennes " + matiere] = []
                    moyenne = self.donnees.get_moyenne(annee_scolaire, trimestre, matiere) if self.donnees.matiere_existe(annee_scolaire, trimestre, matiere) else None
                    resultats["moyennes " + matiere].append(moyenne)

                    # Obtenir les appréciations de la matière
                    if resultats.get("appréciations " + matiere) == None:
                        resultats["appréciations " + matiere] = {"textes": [], "scores": []}
                    appreciation = self.donnees.get_appreciation(annee_scolaire, trimestre, matiere) if self.donnees.matiere_existe(annee_scolaire, trimestre, matiere) else None
                    resultats["appréciations " + matiere]["textes"].append(appreciation)

                print(self.chargement.progession)

        # Récupération des scores
        for resultat in resultats.keys():
            if resultat.startswith("appréciations "):
                nom = resultat[len("appréciations "):]

                # On récupère les textes pour les analyser et les mettres dans scores
                vals_existes = [] # Les valeurs qui ne sont pas à None
                ind_val_existe = [] # L'indice des valeurs qui ne sont pas à None
                result = [None] * len(resultats[resultat]["textes"]) # Ce qui va être utilisé pour afficher le graphique
                for i in range(len(resultats[resultat]["textes"])):
                    if resultats[resultat]["textes"][i] != None:
                        ind_val_existe.append(i)
                        vals_existes.append(resultats[resultat]["textes"][i])
                scores = self.modele_ia.analyser(vals_existes)

                # Mettre les données manquante dans la liste
                j = 0
                for i in range(len(result)):
                    if i in ind_val_existe:
                        result[i] = scores[j]
                        j += 1

                resultats["appréciations " + nom]["scores"] = result

        end_time = time.time()

        print("TIME : ", end_time-start_time)

        # Récupération des données manquante qui vont être une autre ligne du graphique pour compléter les trous
        donnees_manquantes = dict()
        i = 0
        while i < len(trimestres):
            for resultat in resultats:
                est_appreciation = resultat.startswith("appréciations ")
                if est_appreciation:
                    valeur = resultats[resultat]["textes"][i]
                else:
                    valeur = resultats[resultat][i]
                    
                if (valeur == "données manquantes"):
                    j = i
                    
                    if est_appreciation:
                        valeur_prochaine = resultats[resultat]["textes"][j]
                    else:
                        valeur_prochaine = resultats[resultat][j]

                    while j < len(trimestres)-1 and valeur_prochaine == "données manquantes":
                        if est_appreciation:
                            resultats[resultat]["textes"][j] = None
                            resultats[resultat]["scores"][j] = None
                            valeur_prochaine = resultats[resultat]["textes"][j + 1]
                        else:
                            resultats[resultat][j] = None
                            valeur_prochaine = resultats[resultat][j + 1]
                        j += 1

                    if (valeur_prochaine != "données manquantes"):
                        if (not donnees_manquantes.get(resultat)):
                            donnees_manquantes[resultat] = {"trimestres": [], "valeurs": []}
                        # Début des données manquantes
                        if (i > 0): # Si on est pas au début
                            if est_appreciation:
                                valeur_prec = resultats[resultat]["scores"][i-1]
                            else:
                                valeur_prec = resultats[resultat][i-1]
                            donnees_manquantes[resultat]["valeurs"].append(valeur_prec)
                            donnees_manquantes[resultat]["trimestres"].append(trimestres[i-1])
                        else:
                            if est_appreciation:
                                valeur = resultats[resultat]["scores"][i]
                            donnees_manquantes[resultat]["valeurs"].append(valeur)
                            donnees_manquantes[resultat]["trimestres"].append(trimestres[i])
                        # Fin des données manquantes
                        if est_appreciation:
                                valeur_prochaine = resultats[resultat]["scores"][j]
                        donnees_manquantes[resultat]["valeurs"].append(valeur_prochaine)
                        donnees_manquantes[resultat]["trimestres"].append(trimestres[j])

            i += 1

        print(resultats)
        # Création du graphique
        self.chargement.status = "Création du graphique"

        data = go.Figure(layout_yaxis_range=[0,20])
        for nom, valeurs in resultats.items():
            match nom:
                case "moyennes générales":
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                              mode='lines+markers',
                                              name=nom,
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              hovertemplate="%{y}"
                                            ))

                case "appréciations générales":
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs["scores"],
                                              customdata=resultats[nom]["textes"],
                                              mode='lines+markers',
                                              name=nom,
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              hovertemplate="%{customdata}<br>score : %{y}"
                                            ))
                
                case _:
                    if nom.startswith("moyennes "):
                        data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                              mode='lines+markers',
                                              name=nom,
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              visible="legendonly",
                                              hovertemplate="%{y}"
                                            ))
                    elif nom.startswith("appréciations "):
                        data.add_trace(go.Scatter(x=trimestres, y=valeurs["scores"],
                                              customdata=resultats[nom]["textes"],
                                              mode='lines+markers',
                                              name=nom,
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              visible="legendonly",
                                              hovertemplate="%{customdata}<br>score : %{y}"
                                            ))

        #Affichage ligne pour données manquantes     
        for nom, valeurs in donnees_manquantes.items():
            if nom == "appréciations générales" or nom == "moyennes générales":
                data.add_trace(go.Scatter(
                    x=valeurs["trimestres"], y=valeurs["valeurs"],
                    mode="lines",
                    name=nom + " (donnée(s) manquante(s))",
                    legendgroup=nom,
                    legendgrouptitle={'text': nom},
                    hoverinfo="skip",
                    line=dict(dash= "longdash")
                ))
            else:
                data.add_trace(go.Scatter(
                    x=valeurs["trimestres"], y=valeurs["valeurs"],
                    mode="lines",
                    name=nom + " (donnée(s) manquante(s))",
                    legendgroup=nom,
                    legendgrouptitle={'text': nom},
                    visible="legendonly",
                    hoverinfo="skip",
                    line=dict(dash= "longdash")
                ))

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

    def get_matieres(self, annee_scolaire:str, trimestre:str) -> set[str]:
        """Permet d'obtenir toute les matières à partir de l'année dcolaire et du trimestre selectionné

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi

        Returns:
            set[str]: Les matières du trimestre choisi de l'année scolaire choisi
        """
        return set(self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"].keys())
    
    def get_all_matieres(self) -> set[str]:
        """Permet d'obtenir toute les matières présente dans le fichier

        Returns:
            set[str]: Toute les matières présente
        """
        res = set()
        for annee_scolaire in self.get_annees_scolaire():
            for trimestre in self.get_trimestres(annee_scolaire):
                res.update(self.get_matieres(annee_scolaire, trimestre))
        return res

    def matiere_existe(self, annee_scolaire:str, trimestre:str, matiere:str) -> bool:
        """Permet de savoir si la matière existe au trimestre de l'année sélectionné

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi
            matiere (str): La matière

        Returns:
            bool: Return True si la matière existe dans le trimestre de l'année scolaire choisi sinon return False
        """
        return matiere in self.donnees["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"].keys()

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
    def __init__(self, modele_choisi:str):
        """Le constructeur de la classe ModeleIA

        Args:
            modele_choisi (str): Le modele d'IA
        """
        self.modele_choisi = modele_choisi
        self.modeles_disponibles = {"Peed911/french_sentiment_analysis": pipeline("text-classification", model="Peed911/french_sentiment_analysis", top_k=None),
                                    "ac0hik/Sentiment_Analysis_French" : pipeline("text-classification", model="ac0hik/Sentiment_Analysis_French", top_k=None)}
        self.notes = self.noter()

    def modifier_modele(self, new_nom_modele:str):
        """Modifier le modèle d'IA utilisé par l'application

        Args:
            new_nom_modele (str): Le nouveau modèle d'IA utilisé
        """
        self.modele_choisi = new_nom_modele
    
    def analyser(self, textes:list[str], modele:str = None) -> list[float]:
        """Analyse et donne un score /20 à un texte à partir du modele d'IA sélectionné

        Args:
            textes (list[str]): Les textes à analyser
            modele (str, optional): Le modèle à utiliser. Si aucun, prendre modele_choisi dans la classe. None par défault.

        Returns:
            list[float]: Les scores /20 attribué aux textes
        """
        res = []
        pipe = self.modeles_disponibles[modele if modele != None else self.modele_choisi]
        scores = pipe(textes)
        for score in scores:
            for score in score:
                if score["label"].upper() == "POSITIVE":
                    res.append((score["score"] * 20))
        return res

    def noter(self) -> float:
        """Permet de noter automatiquement un modèle d'IA. Pour cela on va prendre le dataset eltorio/appreciation sur HuggingFace 
        qui est utilisé pour lister des appréciations et leur donner un score sur 10 sur 3 catégories : le comportement, la participation et 
        le travail. Ensuite on va donner ces appréciations aux modèles d'IA qui vont nous donner une liste de scores sur 20 puis on va mettres 
        les 3 notes en une notes sur 20. Pour finir on va calculer le coefficient de correlation en les scores que nous ont donné les IA.

        Returns:
            float: Le taux de précision.
        """
        dstrain = load_dataset("eltorio/appreciation", split="train")
        dsvalid = load_dataset("eltorio/appreciation", split="validation")
        
        commentaires = dstrain["commentaire"] + dsvalid["commentaire"]
        comportements = dstrain["comportement 0-10"] + dsvalid["comportement 0-10"]
        participations = dstrain["participation 0-10"] + dsvalid["participation 0-10"]
        travails = dstrain["travail 0-10"] + dsvalid["travail 0-10"]

        resultats = dict()
        for modele in self.modeles_disponibles.keys():
            scores = self.analyser(commentaires, modele)

            notes = []
            for i in range(len(comportements)):
                total = comportements[i] + participations[i] + travails[i] # Le total vaut au maximum 30
                # Mettre le résultat sur 20
                note = total * 20 / 30
                notes.append(note)

            x = pd.Series(scores)
            y = pd.Series(notes)
            resultats[modele] = format(float(x.corr(y)), '5g')
        return resultats

class Chargement:
    def __init__(self):
        self.progession = 0
        self.est_fini = False
        self.status = ""
