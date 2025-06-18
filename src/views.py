from .app import app
from .models import Graphique
from flask import render_template, Response
import os
from flask import request
from werkzeug.utils import secure_filename
import time

graphique = Graphique()

modeles_disponibles = ["Peed911/french_sentiment_analysis", "ac0hik/Sentiment_Analysis_French"]

graphique.modifier_modele(modeles_disponibles[0])

@app.route("/", methods=["GET", "POST"])
def index():
    fichiers_recents = [f for f in os.listdir("./uploaded_files/") if os.path.isfile(os.path.join("./uploaded_files/", f))]
    filename = graphique.donnees.fichier
    modele_selectionne = graphique.modele_ia.nom_modele if graphique.modele_ia.nom_modele != "" else modeles_disponibles[0]
    graph = ""
    
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

    if (graphique.donnees.fichier != ""):
        graph = graphique.generer()

    return render_template("index.html",
                           fichier_charge=filename,
                           modeles_disponibles=modeles_disponibles,
                           fichiers_recents=fichiers_recents,
                           modele_selectionne=modele_selectionne,
                           graph=graph)

@app.route('/progress')
def progress():
    def generate():
        x = 0
        
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x += 10
            time.sleep(0.5)
    
    return Response(generate(), mimetype='text/event-stream')