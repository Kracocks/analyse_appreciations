from flask import Flask
from flask_dropzone import Dropzone
import os.path

MAXIMUM_FILE_SIZE = 15 # En MB

app = Flask(__name__)
dropzone = Dropzone(app)
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.json'
app.config['DROPZONE_INVALID_FILE_TYPE'] = 'Seuls les fichiers .json sont acceptés'
app.config['DROPZONE_FILE_TOO_BIG'] = 'Le fichier est trop lourd {{filesize}}. Le poids maximum est de {{maxFilesize}} MiB'
app.config["DROPZONE_SERVER_ERROR"] = 'Problème serveur : code d\'erreur {{statusCode}}'
app.config["DROPZONE_BROWSER_UNSUPPORTED"] = 'Votre navigateur ne supporte pas le glisser-déposer'
app.config["DROPZONE_MAX_FILE_EXCEED"] = "Vous ne pouvez pas importer plus de fichier"

def mkpath(p):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), p))
