from datasets import load_dataset
appreciations = load_dataset("eltorio/appreciation")

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("ac0hik/Sentiment_Analysis_French")

label2id = {"negatif": 0, "neutre": 1, "positif": 2}

def labeliser(exemple):
    comportement = exemple["comportement 0-10"]
    participation = exemple["participation 0-10"]
    travail = exemple["travail 0-10"]
    note = comportement + participation + travail
    
    if note > 20:
        exemple["label"] = label2id["positif"]
    elif note > 10:
        exemple["label"] = label2id["neutre"]
    else:
        exemple["label"] = label2id["negatif"]

    return exemple

appreciations = appreciations.map(labeliser)

def preprocess_function(examples):
    tokenized = tokenizer(examples["commentaire"], truncation=True)
    tokenized["labels"] = examples["label"]
    return tokenized

tokenized_appreciations = appreciations.map(preprocess_function, batched=True)

from transformers import DataCollatorWithPadding
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
model = AutoModelForSequenceClassification.from_pretrained("ac0hik/Sentiment_Analysis_French", num_labels=3)

training_args = TrainingArguments(
    output_dir="./finetune/test",
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

trainer.save_model("./finetune/test")
tokenizer.save_pretrained("./finetune/test")