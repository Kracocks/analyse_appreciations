text = "Un très bon trimestre. Romain est un élève appliqué et sérieux qui progressera encore en s'impliquant un peu à l'oral."

from transformers import pipeline

classifier = pipeline("text-classification", model="./finetune/test", tokenizer="./finetune/test")

# Prédire sur un texte
resultat = classifier(text)

print(resultat)