import json
import plotly
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from huggingface_hub import repo_exists
from transformers import pipeline
from datasets import load_dataset
import time
import textwrap
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SelectField
from wtforms.validators import DataRequired, ValidationError
from .constantes import COULEURS, MOT_MOYENNES, MOT_APPRECIATIONS

class Graphique:
    def __init__(self):
        """Le contructeur de la classe Graphique
        """
        self.donnees = Donnees()
        self.modele_choisi = ModeleDB()
        self.chargement = Chargement()

    def modifier_donnees(self, fichier:str):
        """Modifier le fichier utilisé pour afficher les données dans un graphique. Le fichier doit être un fichier JSON qui doit respecter une architecture.

        Args:
            fichier (str): Le nouveau fichier utilisé
        """
        self.donnees.modfier_fichier(fichier)

    def modifier_modele(self, id_modele:int):
        """Modifier le modèle d'IA utilisé pour donner un score au appréciations

        Args:
            modele (str): Le nouveau modèle d'IA
        """
        self.modele_choisi = get_modele(id_modele)

    def generer(self) -> str:
        """Génère un graphique à partir des données, variables et modèle d'IA

        Returns:
            str: Le graphique généré
        """
        start_time = time.time()

        # Récupération des données
        self.chargement.to_start()
        
        # Chargement du modèle si pas chargé
        self.chargement.status = "Chargement du modèle d'IA choisi"
        if self.modele_choisi.pipeline == None:
            self.modele_choisi.pipeline = pipeline("text-classification", model=self.modele_choisi.nom, top_k=None) 
        self.chargement.update_progression(5)

        self.chargement.status = "Récupération des données"
        
        nb_total_donnees = self.donnees.get_nb_total_donnees()

        annees_scolaire = self.donnees.get_annees_scolaire()
        matieres = self.donnees.get_all_matieres()
        trimestres = []
        resultats = dict()
        for annee_scolaire in annees_scolaire:
            for trimestre in self.donnees.get_trimestres(annee_scolaire):
                trimestres.append(trimestre + " année " + annee_scolaire)

                # Obtenir les moyennes générales
                if resultats.get("moyennes générales") == None:
                    resultats["moyennes générales"] = []
                mg = self.donnees.get_moyenne(annee_scolaire, trimestre)
                resultats["moyennes générales"].append(mg)
                self.chargement.update_progression(1 * 80 / nb_total_donnees)

                # Obtenir les appréciations générales
                appreciation = self.donnees.get_appreciation(annee_scolaire, trimestre)
                if resultats.get("appréciations générales") == None:
                    resultats["appréciations générales"] = {"textes": [], "scores": []}
                resultats["appréciations générales"]["textes"].append(appreciation)
                self.chargement.update_progression(1 * 80 / nb_total_donnees)

                for matiere in matieres:
                    # Obtenir les moyennes de la matière
                    if resultats.get(MOT_MOYENNES + matiere) == None:
                        resultats[MOT_MOYENNES + matiere] = []
                    moyenne = self.donnees.get_moyenne(annee_scolaire, trimestre, matiere) if self.donnees.matiere_existe(annee_scolaire, trimestre, matiere) else None
                    resultats[MOT_MOYENNES + matiere].append(moyenne)
                    
                    self.chargement.update_progression(1 * 80 / nb_total_donnees)

                    # Obtenir les appréciations de la matière
                    if resultats.get(MOT_APPRECIATIONS + matiere) == None:
                        resultats[MOT_APPRECIATIONS + matiere] = {"textes": [], "scores": []}
                    appreciation = self.donnees.get_appreciation(annee_scolaire, trimestre, matiere) if self.donnees.matiere_existe(annee_scolaire, trimestre, matiere) else None
                    resultats[MOT_APPRECIATIONS + matiere]["textes"].append(appreciation)
                    
                    self.chargement.update_progression(1 * 80 / nb_total_donnees)

                # Obtenir les retards
                retard = self.donnees.get_nb_retards(annee_scolaire, trimestre)
                if resultats.get("retard") == None:
                    resultats["retard"] = []
                resultats["retard"].append(retard)
                self.chargement.update_progression(1 * 80 / nb_total_donnees)

                # Obtenir les absences justifiées
                absence_just = self.donnees.get_nb_absences_justifie(annee_scolaire, trimestre)
                if resultats.get("absences justifiées") == None:
                    resultats["absences justifiées"] = []
                resultats["absences justifiées"].append(absence_just)
                self.chargement.update_progression(1 * 80 / nb_total_donnees)

                # Obtenir les absences non justifiées
                absence_non_just = self.donnees.get_nb_absences_non_justifie(annee_scolaire, trimestre)
                if resultats.get("absences non justifiées") == None:
                    resultats["absences non justifiées"] = []
                resultats["absences non justifiées"].append(absence_non_just)
                self.chargement.update_progression(1 * 80 / nb_total_donnees)

                print(self.chargement.progression)

        # Récupération des scores
        for resultat in resultats.keys():
            if resultat.startswith(MOT_APPRECIATIONS):
                nom = resultat[len(MOT_APPRECIATIONS):]

                # On récupère les textes pour les analyser et les mettres dans scores
                vals_existes = [] # Les valeurs qui ne sont pas à None
                ind_val_existe = [] # L'indice des valeurs qui ne sont pas à None
                result = [None] * len(resultats[resultat]["textes"]) # Ce qui va être utilisé pour afficher le graphique
                for i in range(len(resultats[resultat]["textes"])):
                    if resultats[resultat]["textes"][i] != None:
                        ind_val_existe.append(i)
                        vals_existes.append(resultats[resultat]["textes"][i])
                scores = self.modele_choisi.analyser(vals_existes)

                # Mettre les données manquante dans la liste
                j = 0
                for i in range(len(result)):
                    if i in ind_val_existe:
                        result[i] = scores[j]
                        j += 1

                resultats["appréciations " + nom]["scores"] = result

        end_time = time.time()

        print("TIME : ", end_time-start_time)

        # Création du graphique
        self.chargement.status = "Création du graphique"

        data = go.Figure(layout_yaxis_range=[0,20])
        data.update_layout(
            title=dict(
                text="Progression scolaire de " + self.donnees.get_nom_eleve()
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.3,
                xanchor="center",
                x=0.5,
                traceorder="normal",
                itemwidth=30
            ),
            height=800
        )

        ind_couleur = 0
        for nom, valeurs in resultats.items():
            couleur = COULEURS[ind_couleur % len(COULEURS)]
            ind_couleur += 1
            match nom:
                case "moyennes générales":
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                              mode="lines",
                                              name=nom + " (donnée(s) manquante(s))",
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              showlegend=False,
                                              hoverinfo="skip",
                                              line=dict(dash= "longdash", color=couleur),
                                              connectgaps=True
                                            ))
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                              mode='lines+markers',
                                              name=nom,
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              hovertemplate="%{y}",
                                              line=dict(color=couleur)
                                            ))

                case "appréciations générales":
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs["scores"],
                                              mode="lines",
                                              name=nom + " (donnée(s) manquante(s))",
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              showlegend=False,
                                              hoverinfo="skip",
                                              line=dict(dash= "longdash", color=couleur),
                                              connectgaps=True
                                            ))
                    data.add_trace(go.Scatter(x=trimestres, y=valeurs["scores"],
                                              customdata=resultats[nom]["textes"],
                                              mode='lines+markers',
                                              name=nom,
                                              legendgroup=nom,
                                              legendgrouptitle={'text': nom},
                                              hovertemplate="%{customdata}<br>note IA : %{y}",
                                              line=dict(color=couleur)
                                            ))

                case _:
                    if nom.startswith(MOT_MOYENNES) or nom == "retard" or nom == "absences justifiées" or nom == "absences non justifiées":
                        data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                                  mode="lines",
                                                  name=nom + " (donnée(s) manquante(s))",
                                                  legendgroup=nom,
                                                  legendgrouptitle={'text': nom},
                                                  showlegend=False,
                                                  hoverinfo="skip",
                                                  visible="legendonly",
                                                  line=dict(dash= "longdash", color=couleur),
                                                  connectgaps=True
                                                ))
                        data.add_trace(go.Scatter(x=trimestres, y=valeurs,
                                                  mode='lines+markers',
                                                  name=nom,
                                                  legendgroup=nom,
                                                  legendgrouptitle={'text': nom},
                                                  visible="legendonly",
                                                  hovertemplate="%{y}",
                                                  line=dict(color=couleur)
                                                ))

                    elif nom.startswith(MOT_APPRECIATIONS):
                        data.add_trace(go.Scatter(x=trimestres, y=valeurs["scores"],
                                                  mode="lines",
                                                  name=nom + " (donnée(s) manquante(s))",
                                                  legendgroup=nom,
                                                  legendgrouptitle={'text': nom},
                                                  showlegend=False,
                                                  hoverinfo="skip",
                                                  visible="legendonly",
                                                  line=dict(dash= "longdash", color=couleur),
                                                  connectgaps=True
                                                ))
                        data.add_trace(go.Scatter(x=trimestres, y=valeurs["scores"],
                                                  customdata=resultats[nom]["textes"],
                                                  mode='lines+markers',
                                                  name=nom,
                                                  legendgroup=nom,
                                                  legendgrouptitle={'text': nom},
                                                  visible="legendonly",
                                                  hovertemplate="%{customdata}<br>note IA : %{y}",
                                                  line=dict(color=couleur)
                                                ))
            if nom == "appréciations générales":
                for i in range(len(trimestres)):
                            data.add_annotation(
                                x=trimestres[i], y=valeurs["scores"][i],
                                xref="x",
                                yref="y",
                                text=f"{self.wrap(resultats[nom]["textes"][i])}",
                                clicktoshow="onoff",
                                visible=False,
                                font=dict(
                                    family="Courier New, monospace",
                                    size=11,
                                    color="#ffffff"
                                    ),
                                align="center",
                                arrowhead=4,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor="#636363",
                                ax=0,
                                ay=-30,
                                bordercolor="#c7c7c7",
                                borderwidth=2,
                                borderpad=4,
                                bgcolor=couleur,
                                opacity=0.8
                            )

        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        self.chargement.to_end()

        return graphJSON

    def wrap(self, text):
        if (text == None):
            return None
        wrap = textwrap.wrap(text, width=32)
        texte = ""
        for text_part in wrap:
            texte += text_part + "<br>"
        return texte

class Donnees:
    def __init__(self):
        """Le constructeur de la classe Donnees

        Args:
            fichier (str): Le fichier à charger
        """
        self.fichier = None
        self.donnees = None
        self.eleve_selectionne = None
        self.donnees_eleve = None

    def modfier_fichier(self, new_fichier:str) -> bool:
        """Modifier les donnée utilisé par l'application à partir d'un fichier JSON. Le JSON doit respecter une architecture et renverra False si l'architecture n'est pas correcte ou si le fichier n'est pas un JSON

        Args:
            new_fichier (str): Le nouveau fichier avec les données à utiliser.

        Returns:
            bool: Renvoi True si les données ont été modifiées. Sinon False.
        """
        self.fichier = new_fichier
        self.eleve_selectionne = None
        self.donnees_eleve = None
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
    
    def modifier_eleve(self, ine_eleve:str):
        """Modifie les données utilisé

        Args:
            ine_eleve (str): l'INE de l'élève à qui prendre les données
        """
        if ine_eleve == "":
            self.eleve_selectionne = None
        elif self.donnees != None:
            for eleve in self.donnees:
                if eleve["INE"] == ine_eleve:
                    self.donnees_eleve = eleve
                    eleve_selectionne = {"nom": eleve["nom"], "prenom": eleve["prenom"], "INE": eleve["INE"]}
                    self.eleve_selectionne = eleve_selectionne

    def get_eleves(self):
        """Permet d'avoir tout les élèves qui se trouve dans les données
        """
        res = []
        if self.donnees != None:
            for eleve in self.donnees:
                res.append({"nom": eleve["nom"], "prenom": eleve["prenom"], "INE": eleve["INE"]})
        return res
    
    def get_nom_eleve(self):
        return (self.donnees_eleve.get("prenom") + " " + self.donnees_eleve.get("nom"))

    def get_annees_scolaire(self) -> list[str]:
        """Permet d'avoir toute les années scolaire enregistré dans le fichier

        Returns:
            list[str]: Les années scolaire dans le fichier
        """
        annees = []
        for annee in self.donnees_eleve.get("annees_scolaire"):
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
        for trimestre in self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"]:
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
            return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere]["moyenne"]
        return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["moyenne_generale"]

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
            return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere]["appreciation"]
        return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["appreciation_generale"]

    def get_matieres(self, annee_scolaire:str, trimestre:str) -> set[str]:
        """Permet d'obtenir toute les matières à partir de l'année dcolaire et du trimestre selectionné

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi

        Returns:
            set[str]: Les matières du trimestre choisi de l'année scolaire choisi
        """
        return set(self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"].keys())
    
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

    def get_nb_absences_justifie(self, annee_scolaire:str, trimestre:str) -> int:
        return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["heures_absence_justifie"]
    
    def get_nb_absences_non_justifie(self, annee_scolaire:str, trimestre:str) -> int:
        return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["heures_absence_non_justifie"]

    def get_nb_retards(self, annee_scolaire:str, trimestre:str) -> int:
        return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["total_retards"]

    def matiere_existe(self, annee_scolaire:str, trimestre:str, matiere:str) -> bool:
        """Permet de savoir si la matière existe au trimestre de l'année sélectionné

        Args:
            annee_scolaire (str): L'année scolaire choisi
            trimestre (str): Le trimestre de l'année scolaire choisi
            matiere (str): La matière

        Returns:
            bool: Return True si la matière existe dans le trimestre de l'année scolaire choisi sinon return False
        """
        return matiere in self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"].keys()

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
            return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere].get("appreciation_score_" + modele_ia) != None
        else:
            return self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre].get("appreciation_generale_score_" + modele_ia) != None

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
            self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"][matiere]["appreciation_score_" + modele_ia] = score
        else:
            self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["appreciation_generale_score_" + modele_ia] = score
        with open(self.fichier, 'r+') as f:
            f.seek(0)
            json.dump(self.donnees_eleve, f, indent=4)
            f.truncate()

    def get_nb_total_donnees(self) -> int:
        total = 0
        for annee_scolaire in self.donnees_eleve["annees_scolaire"]:
            for trimestre in self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"]:
                # On va prendre toute les "feuilles" dans un trimestre on enleve juste 
                # les feuilles "score" (car je considère que score et appréciation représente 
                # la même données) et "matiere" puis on prend tout les matières et on les 
                # multiplies par deux car il y a deux données par matière 
                total += (len(self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]) - 2) + len(self.donnees_eleve["annees_scolaire"][annee_scolaire]["trimestres"][trimestre]["matiere"]) * 2
        
        return total

class Chargement:
    def __init__(self):
        self.temp_prog = 0
        self.progression = 0
        self.est_fini = False
        self.status = ""
    
    def to_start(self):
        self.temp_prog = 0
        self.progression = 0
        self.est_fini = False
        
    def to_end(self):
        self.temp_prog = 100
        self.progression = 100
        self.est_fini = True
        
    def update_progression(self, added_progression):
        self.temp_prog += added_progression
        self.progression = round(self.temp_prog)

from .app import db
class ModeleDB(db.Model):
    __tablename__ = "modele"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nom = db.Column(db.String, nullable=False)
    correlation = db.Column(db.Float)
    label_positif = db.Column(db.String, nullable=False)
    pipeline = None
    
    def __repr__(self):
        return f"<Modele {self.id, self.nom, self.correlation, self.label_positif}>"
    
    def analyser(self, textes:list[str]) ->list[float]:
        """Analyse et donne un score /20 à un texte à partir du modele d'IA sélectionné

        Args:
            textes (list[str]): Les textes à analyser
            modele (str, optional): Le modèle à utiliser. Si aucun, prendre modele_choisi dans la classe. None par défault.

        Returns:
            list[float]: Les scores /20 attribué aux textes
        """
        res = []
        if self.pipeline == None:
            self.pipeline = pipeline("text-classification", model=self.nom, top_k=None) 
        scores = self.pipeline(textes)
        for score in scores:
            for score in score:
                if score["label"].upper() == self.label_positif.upper():
                    res.append(round(score["score"] * 20, 2))
        return res

    def noter(self) -> float:
        """Permet de noter automatiquement un modèle d'IA. Pour cela on va prendre le dataset eltorio/appreciation sur HuggingFace 
        qui est utilisé pour lister des appréciations et leur donner un score sur 10 sur 3 catégories : le comportement, la participation et 
        le travail. Ensuite on va donner ces appréciations aux modèles d'IA qui vont nous donner une liste de scores sur 20 puis on va mettres 
        les 3 notes en une notes sur 20. Pour finir on va calculer le coefficient de correlation en les scores que nous ont donné les IA.

        Returns:
            float: Le taux de précision.
        """
        #dstrain = load_dataset("eltorio/appreciation", split="train")
        dsvalid = load_dataset("eltorio/appreciation", split="validation")
        
        # commentaires = dstrain["commentaire"] + dsvalid["commentaire"]
        # comportements = dstrain["comportement 0-10"] + dsvalid["comportement 0-10"]
        # participations = dstrain["participation 0-10"] + dsvalid["participation 0-10"]
        # travails = dstrain["travail 0-10"] + dsvalid["travail 0-10"]
        commentaires = dsvalid["commentaire"]
        comportements = dsvalid["comportement 0-10"]
        participations = dsvalid["participation 0-10"]
        travails = dsvalid["travail 0-10"]

        scores = self.analyser(commentaires)

        notes = []
        for i in range(len(comportements)):
            total = comportements[i] + participations[i] + travails[i] # Le total vaut au maximum 30
            # Mettre le résultat sur 20
            note = total * 20 / 30
            notes.append(round(note, 2))

        x = pd.Series(scores)
        y = pd.Series(notes)
        return round(float(x.corr(y)), 2)

# Validators
def valider_label_positif_modele(form, field):
    if repo_exists(form.nom.data):
        from transformers import AutoModelForSequenceClassification
        modele = AutoModelForSequenceClassification.from_pretrained(form.nom.data)
        if field.data.upper() not in modele.config.label2id.keys():
            raise ValidationError("Ce label n'existe pas parmi les labels du modèle")
    else:
        raise ValidationError("Ce modèle n'existe pas sur HuggingFace.")

# Formulaires
class ModeleForm(FlaskForm):
    id = HiddenField('id')
    nom = StringField("Nom du modèle provenant de HuggingFace", validators=[DataRequired()], id='field_nom')
    label_positif = SelectField('Nom du label positif du modèle:', validators=[DataRequired()], id='select_label')

def get_labels_of_model(nom:str) -> list[str]:
    from transformers import AutoModelForSequenceClassification
    if repo_exists(nom):
        modele = AutoModelForSequenceClassification.from_pretrained(nom)
        return modele.config.label2id.keys()
    else:
        return ["-- Aucun modèle sélectionné --"]

def get_modeles():
    return ModeleDB.query.all()

def get_modele_from_nom(nom:str):
    return ModeleDB.query.filter_by(nom=nom).first()

def get_modele(id_modele):
    return ModeleDB.query.get_or_404(id_modele)

def get_last_modele_id():
    last_model = ModeleDB.query.order_by(ModeleDB.id.desc()).first()
    if last_model:
        return last_model.id