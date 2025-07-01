from .app import app, db
from .models import Graphique, ModeleForm, ModeleDB, get_last_modele_id, get_modeles
from flask import render_template,redirect, url_for, Response
import os
from flask import request
from werkzeug.utils import secure_filename
import json

graphique = Graphique()

graphique.modifier_modele("Peed911/french_sentiment_analysis")

@app.route("/", methods=["GET", "POST"])
def index():
    fichiers_recents = [f for f in os.listdir(app.config["UPLOAD_PATH"]) if os.path.isfile(os.path.join(app.config["UPLOAD_PATH"], f))]
    filename = graphique.donnees.fichier
    modeles_disponibles = [modele.nom for modele in get_modeles()]
    modele_selectionne = graphique.modele_ia.modele_choisi if graphique.modele_ia.modele_choisi != "" else modeles_disponibles[0]

    if request.method == 'POST':

        file = request.files.get('file')

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_PATH"], filename))
            graphique.modifier_donnees(os.path.join(app.config["UPLOAD_PATH"], filename))

        # Selection d'un fichier récemment utilisé
        elif request.form.get("recent_files_choice"):
            filename = request.form.get("recent_files_choice")
            graphique.modifier_donnees(os.path.join(app.config["UPLOAD_PATH"], filename))

        # Réafficher le tableau
        if request.form.get("modeles_choice"):
            modele_selectionne = request.form.get("modeles_choice")
            graphique.modifier_modele(modele_selectionne)
        
    f=ModeleForm()

    return render_template("index.html",
                           fichier_charge=filename,
                           modeles_disponibles=modeles_disponibles,
                           fichiers_recents=fichiers_recents,
                           modele_selectionne=modele_selectionne,
                           notes_ia=graphique.modele_ia.notes,
                           form=f)

@app.route('/progress') # Mettre a jour la bar de progression
def progress():
    def generate():
        progression = graphique.chargement.progression
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

@app.route("/add/modele/", methods=["POST"])
def save_modele():
    modele = None
    f = ModeleForm()
    if f.validate_on_submit():
        id = get_last_modele_id() + 1
        modele = ModeleDB(id=id, nom=f.nom.data, correlation=None)
        db.session.add(modele)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/edit/correlation", methods=["POST"])
def correler_modele():
    return