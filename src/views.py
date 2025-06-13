from .app import app
from .models import Graphique
from flask import render_template
import os
from flask import request
from werkzeug.utils import secure_filename

graphique = Graphique()

modeles_disponibles = ["Peed911/french_sentiment_analysis", "ac0hik/Sentiment_Analysis_French"]

@app.route("/", methods=["GET", "POST"])
def index():
    recent_files = [f for f in os.listdir("./uploaded_files/") if os.path.isfile(os.path.join("./uploaded_files/", f))]
    filename = graphique.donnees.fichier
    modele = graphique.modele_ia.nom_modele if graphique.modele_ia.nom_modele != "" else modeles_disponibles[0]
    graph = ""
    print('passer ici 1')
    if request.method == 'POST':
        
        file = request.files.get('file')
        print('file')

        if file:
            print(file)
            filename = secure_filename(file.filename)
            file.save(os.path.join("./uploaded_files/", filename))
            print(graphique.donnees.fichier)
            graphique.modifier_donnees(os.path.join("./uploaded_files/", filename))
            print(graphique.donnees.fichier)

        # Selection d'un fichier récemment utilisé
        elif request.form.get("recent_files_choice"):
            filename = request.form.get("recent_files_choice")
            graphique.modifier_donnees(os.path.join("./uploaded_files/", filename))
                    
        print('passer ici 2')
        
        # Réafficher le tableau
        if "analyser" in request.form:
            if request.form["modeles"]:
                modele = request.form["modeles"]
                graphique.modifier_modele(request.form["modeles"])

    if (graphique.donnees.fichier != ""):
        graph = graphique.generer()

    return render_template("index.html",
                           fichier_charge=filename,
                           modeles=modeles_disponibles,
                           recent_files=recent_files,
                           modele_selectionne=modele,
                           data=graph)
