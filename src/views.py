from .app import app
from .models import Graphique
from flask import render_template, Response
import os
from flask import request
from werkzeug.utils import secure_filename
import json

graphique = Graphique()

modeles_disponibles = graphique.modele_ia.modeles_disponibles

graphique.modifier_modele(modeles_disponibles[0])

@app.route("/", methods=["GET", "POST"])
def index():
    fichiers_recents = [f for f in os.listdir("./uploaded_files/") if os.path.isfile(os.path.join("./uploaded_files/", f))]
    filename = graphique.donnees.fichier
    modele_selectionne = graphique.modele_ia.nom_modele if graphique.modele_ia.nom_modele != "" else modeles_disponibles[0]

    if request.method == 'POST':

        file = request.files.get('file')

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join("./uploaded_files/", filename))
            graphique.modifier_donnees(os.path.join("./uploaded_files/", filename))

        # Selection d'un fichier récemment utilisé
        elif request.form.get("recent_files_choice"):
            filename = request.form.get("recent_files_choice")
            graphique.modifier_donnees(os.path.join("./uploaded_files/", filename))

        # Réafficher le tableau
        if request.form.get("modeles_choice"):
            modele_selectionne = request.form.get("modeles_choice")
            graphique.modifier_modele(modele_selectionne)

    return render_template("index.html",
                           fichier_charge=filename,
                           modeles_disponibles=modeles_disponibles,
                           fichiers_recents=fichiers_recents,
                           modele_selectionne=modele_selectionne)

@app.route('/progress') # Mettre a jour la bar de progression
def progress():
    def generate():
        progression = graphique.chargement.progession
        statut = graphique.chargement.status
        data = json.dumps({"progression": progression, "statut":statut})
        yield "data:" + str(data) + "\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route("/get-graph") # Permetre de récupérer le graphique
def get_graph():
    graph = ""
    if (graphique.donnees.fichier != ""):
        graph = graphique.generer()
    return json.dumps({"graph": graph})
