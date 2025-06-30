import click
from .app import app, db
from.models import ModeleDB

@app.cli.command()
@click.argument("filename")
def loaddb(filename):
    '''Créer les tables et les populer avec des données'''

    db.create_all()

    modele = ModeleDB(nom = "Peed911/french_sentiment_analysis")
    db.session.add(modele)

    modele = ModeleDB(nom = "ac0hik/Sentiment_Analysis_French")
    db.session.add(modele)

    db.session.commit()

@app.cli.command()
def syncdb():
    '''Créer toute les tables manquantes'''
    db.create_all()

