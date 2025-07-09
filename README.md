
# analyse_appreciations

Une application permettant de visualiser, à l'aide d'un graphique, la progression scolaire d'une personne afin de prédire les risques de décrochage scolaire. Les appréciations sont transformées en notes à l'aide d'un modèle d'IA.

## Prérequis 

L'application a été testée dans la version **3.12.3 de Python**. Les versions antérieures ne sont pas supportées en raison des dépendances.

## Installation

Clonez le dépôt et installez les dépendances

```bash
  git clone https://github.com/Kracocks/analyse_appreciations
  cd analyse_appreciations
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
```
## Deployment

Pour déployer l'application, lancez

```bash
  flask run --no-reload
```

Si vous voulez avoir accès aux version fine-tune des premier modèles d'IA disponible, faite

```bash
  flask finetune
```