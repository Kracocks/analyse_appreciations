from .app import app, db, modeles_disponibles
from .models import Graphique, ModeleForm, ModeleDB, get_last_modele_id, get_modeles, get_modele, get_labels_of_model
from flask import render_template,redirect, url_for, Response, request, stream_with_context, jsonify
from transformers import pipeline
import os
from werkzeug.utils import secure_filename
import json
import time
import sys

graphique = Graphique()

with app.app_context():
    if sys.argv[1] == "run":
        graphique.modifier_modele("Peed911/french_sentiment_analysis")

@app.route("/", methods=["GET", "POST"])
def index():
    fichiers_recents = [f for f in os.listdir(app.config["UPLOAD_PATH"]) if os.path.isfile(os.path.join(app.config["UPLOAD_PATH"], f))]
    filename = graphique.donnees.fichier
    modeles_disponibles = get_modeles()
    modele_selectionne = graphique.modele_choisi.nom if graphique.modele_choisi.nom != None else modeles_disponibles[0].nom

    if request.method == 'POST':
        file = request.files.get('file')

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_PATH"], filename))
            graphique.modifier_donnees(os.path.join(app.config["UPLOAD_PATH"], filename))

    f=ModeleForm()
    #f.label_positif.choices = "-- Choisir un label --" + get_labels_of_model(f.nom.data)

    return render_template("index.html",
                           fichier_charge=filename,
                           modeles_disponibles=modeles_disponibles,
                           fichiers_recents=fichiers_recents,
                           modele_selectionne=modele_selectionne,
                           notes_ia=graphique.modele_choisi.correlation,
                           eleve_disponibles=graphique.donnees.get_eleves(),
                           eleve_selectionne=graphique.donnees.eleve_selectionne,
                           form=f)

@app.route('/progress') # Mettre a jour la bar de progression
def progress():
    def generate():
        while True:
            progression = graphique.chargement.progression
            statut = graphique.chargement.status

            data = json.dumps({"progression": progression, "statut": statut})
            yield f"data: {data}\n\n"

            if progression >= 100:
                break

            time.sleep(0.2)  # attend 0.5s avant le prochain envoi

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route("/get-graph") # Permetre de récupérer le graphique
def get_graph():
    graph = ""
    if (graphique.donnees.fichier != ""):
        graph = graphique.generer()
    return json.dumps({"graph": graph})

@app.route("/add/modele/", methods=["POST"])
def save_modele():
    modele = None
    f = ModeleForm()
    f.label_positif.choices = [(label, label) for label in get_labels_of_model(f.nom.data)]
    if f.validate_on_submit():
        id = get_last_modele_id() + 1
        modele = ModeleDB(id=id, nom=f.nom.data, correlation=None, label_positif=f.label_positif.data)
        db.session.add(modele)
        db.session.commit()

        return redirect(url_for("index"))

    fichiers_recents = [f for f in os.listdir(app.config["UPLOAD_PATH"]) if os.path.isfile(os.path.join(app.config["UPLOAD_PATH"], f))]
    filename = graphique.donnees.fichier
    modeles_disponibles = get_modeles()
    modele_selectionne = graphique.modele_choisi.nom if graphique.modele_choisi.nom != None else modeles_disponibles[0].nom
    return render_template("index.html",
                           fichier_charge=filename,
                           modeles_disponibles=modeles_disponibles,
                           fichiers_recents=fichiers_recents,
                           modele_selectionne=modele_selectionne,
                           notes_ia=graphique.modele_choisi.correlation,
                           eleve_disponibles=graphique.donnees.get_eleves(),
                           eleve_selectionne=graphique.donnees.eleve_selectionne,
                           form=f)
    
@app.route("/edit/file/", methods=["POST"])
def modifier_fichier():
    filename = request.form.get("recent_files_choice")
    graphique.modifier_donnees(os.path.join(app.config["UPLOAD_PATH"], filename))
    return redirect(url_for("index"))

@app.route("/edit/modele/", methods=["POST"])
def modifier_modele_choisi():
    modele_selectionne = request.form.get("modeles_choice")
    graphique.modifier_modele(modele_selectionne)
    return redirect(url_for("index"))

@app.route("/edit/eleve/", methods=["POST"])
def modifier_eleve():
    ine_eleve = request.form.get("eleve_choice")
    graphique.donnees.modifier_eleve(ine_eleve)
    return redirect(url_for("index"))

@app.route("/edit/correlation/", methods=["POST"])
def correler_modele():
    modeles_disponibles = get_modeles()
    for i in range(len(modeles_disponibles)):
        if modeles_disponibles[i].correlation == None:
            correlation = modeles_disponibles[i].noter()
            modele = get_modele(modeles_disponibles[i].id)
            modele.correlation = correlation
            db.session.add(modele)
            modeles_disponibles[i] = modele

    db.session.commit()

    return redirect(url_for("index"))

@app.route("/get/labels/<string:nom_auteur>/<string:nom_modele>", methods=["GET", "POST"])
def get_labels(nom_auteur:str, nom_modele:str):
    return jsonify(list(get_labels_of_model(nom_auteur + "/" + nom_modele)))