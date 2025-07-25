from flask import Flask
from flask_dropzone import Dropzone
from flask_sqlalchemy import SQLAlchemy
import os.path

def mkpath(p):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), p))

MAXIMUM_FILE_SIZE = 15 # En MB

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = ('sqlite:///'+mkpath('../app.db'))
db = SQLAlchemy(app)

app.config.update(
    DROPZONE_REDIRECT_VIEW = 'index',
    DROPZONE_ALLOWED_FILE_CUSTOM = True,
    DROPZONE_ALLOWED_FILE_TYPE = '.json',
    DROPZONE_MAX_FILES = 1,
    DROPZONE_DEFAULT_MESSAGE = '>>> Glissez-déposez ou cliquez pour sélectionner <<<',
    DROPZONE_INVALID_FILE_TYPE = 'Seuls les fichiers .json sont acceptés',
    DROPZONE_FILE_TOO_BIG = 'Le fichier est trop lourd {{filesize}}. Le poids maximum est de {{maxFilesize}} MiB',
    DROPZONE_SERVER_ERROR = 'Problème serveur : code d\'erreur {{statusCode}}',
    DROPZONE_BROWSER_UNSUPPORTED = 'Votre navigateur ne supporte pas le glisser-déposer',
    DROPZONE_MAX_FILE_EXCEED = 'Vous ne pouvez pas importer plus de fichier',
    
    UPLOAD_PATH = "uploads",
    
    SECRET_KEY = "s;8yY2.5ge}PH0:"
)

modeles_disponibles = []

dropzone = Dropzone(app)
