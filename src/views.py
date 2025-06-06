from .app import app
from .models import Graphique
from flask import render_template
import os
import io
from flask import request, redirect
from werkzeug.utils import secure_filename
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

graphique = Graphique()

modeles_disponibles = ["Peed911/french_sentiment_analysis", "ac0hik/Sentiment_Analysis_French"]

@app.route("/", methods=["GET", "POST"])
def index():
    filename = graphique.donnees.fichier
    modele = graphique.modele_ia.nom_modele if graphique.modele_ia.nom_modele != "" else modeles_disponibles[0]
    img = ""
    if request.method == 'POST':
        
        if "charger" in request.form:
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']

            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                return redirect(request.url)

            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join("./uploaded_files/", filename))
                graphique.modifier_donnees(os.path.join("./uploaded_files/", filename))

        if "analyser" in request.form:
            if request.form["modeles"]:
                modele = request.form["modeles"]
                graphique.modifier_modele(request.form["modeles"])

            img = graphique.generer()

    return render_template("index.html",
                           fichier_charge=filename,
                           modeles=modeles_disponibles,
                           modele_selectionne=modele,
                           data=img)

