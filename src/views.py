from .app import app
from flask import render_template
import os
from flask import flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

@app.route("/", methods=["GET", "POST"])
def index():
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
            file.save(os.path.join("./", filename))
    return render_template("index.html")
