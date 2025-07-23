from .app import app, db
from .models import ModeleDB

@app.cli.command()
def loaddb():
    '''Créer les tables et les populer avec des données'''

    db.create_all()

    modele = ModeleDB(nom = "Peed911/french_sentiment_analysis", label_positif = "Positive")
    db.session.add(modele)

    modele = ModeleDB(nom = "ac0hik/Sentiment_Analysis_French", label_positif = "positive")
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
    
    nom_model = "Peed911/french_sentiment_analysis"

    tokenizer = AutoTokenizer.from_pretrained(nom_model)
    model = AutoModelForSequenceClassification.from_pretrained(nom_model, problem_type="regression", num_labels=1, ignore_mismatched_sizes=True) # --> parametre pour tache de regression

    def labeliser(dataset):
        comportement = dataset["comportement 0-10"]
        participation = dataset["participation 0-10"]
        travail = dataset["travail 0-10"]
        note = comportement + participation + travail
        score = note / 30
        
        dataset["label"] = score

        return dataset

    appreciations = appreciations.map(labeliser)

    def preprocess_function(examples):
        tokenized = tokenizer(examples["commentaire"], truncation=True)
        tokenized["labels"] = examples["label"]
        return tokenized

    tokenized_appreciations = appreciations.map(preprocess_function, batched=True)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    output_dir = "./finetune/" + nom_model

    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=2e-4,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        weight_decay=0.1,
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

    db.session.add(ModeleDB(nom = output_dir, label_positif = "LABEL_0"))

    db.session.commit()