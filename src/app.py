from flask import Flask
import os.path

app = Flask(__name__)

def mkpath(p):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), p))
