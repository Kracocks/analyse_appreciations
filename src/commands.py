from .app import app, db
from .models import ModeleDB

@app.cli.command()
def loaddb():
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

@app.cli.command()
def finetune():
    '''Ajouter les version fine-tune des modeles d'IA de base de l'application'''
    from datasets import load_dataset
    from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer, DataCollatorWithPadding, AutoTokenizer
    appreciations = load_dataset("eltorio/appreciation")

    for modele in ["Peed911/french_sentiment_analysis", "ac0hik/Sentiment_Analysis_French"]:

        tokenizer = AutoTokenizer.from_pretrained(modele)
        model = AutoModelForSequenceClassification.from_pretrained(modele)

        def labeliser(exemple):
            comportement = exemple["comportement 0-10"]
            participation = exemple["participation 0-10"]
            travail = exemple["travail 0-10"]
            note = comportement + participation + travail

            if model.config.num_labels == 2:
                label2id = {"negatif": 0, "positif": 1}

                if note > 15:
                    exemple["label"] = label2id["positif"]
                else:
                    exemple["label"] = label2id["negatif"]

            elif model.config.num_labels == 3:
                label2id = {"negatif": 0, "neutre": 1, "positif": 2}

                if note >= 20:
                    exemple["label"] = label2id["positif"]
                elif note >= 10:
                    exemple["label"] = label2id["neutre"]
                else:
                    exemple["label"] = label2id["negatif"]

            else:
                raise("Pas prévu pour un modèle avec " + model.config.num_labels + " labels")

            return exemple

        appreciations = appreciations.map(labeliser)

        def preprocess_function(examples):
            tokenized = tokenizer(examples["commentaire"], truncation=True)
            tokenized["labels"] = examples["label"]
            return tokenized

        tokenized_appreciations = appreciations.map(preprocess_function, batched=True)

        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        output_dir = "./finetune/" + modele

        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=2e-5,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=5,
            weight_decay=0.01,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_appreciations["train"],
            eval_dataset=tokenized_appreciations["validation"],
            tokenizer=tokenizer,
            data_collator=data_collator,
        )

        trainer.train()

        trainer.save_model(output_dir)
        tokenizer.save_pretrained(output_dir)

        db.session.add(ModeleDB(nom = output_dir))

    db.session.commit()