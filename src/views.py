from .app import app
from flask import render_template
import os
from flask import request, redirect
from werkzeug.utils import secure_filename

modeles_disponibles = ["Peed911/french_sentiment_analysis", "ac0hik/Sentiment_Analysis_French"]

@app.route("/", methods=["GET", "POST"])
def index():
    filename = ""
    modele = modeles_disponibles[0]
    if request.method == 'POST':
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

        if request.form["modeles"]:
            modele = request.form["modeles"]

    return render_template("index.html",
                           fichier_charge=filename,
                           modeles=modeles_disponibles,
                           modele_selectionne=modele)

