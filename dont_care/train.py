# This is for training commands(abandoned)

from datasets import load_dataset
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import pickle

def train_model():
    dataset = load_dataset("csv", data_files="intents.csv")["train"]

    # Collect all labels first and fit the encoder
    all_labels = dataset["intent"]
    label_encoder = LabelEncoder()
    label_encoder.fit(all_labels)

    # transform using a clean map function
    def encode_labels(example):
        example["label"] = label_encoder.transform([example["intent"]])[0]
        return example

    dataset = dataset.map(encode_labels)

    # Tokenizer and tokenization
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

    def tokenize(batch):
        return tokenizer(batch["text"], padding="max_length", truncation=True)

    dataset = dataset.map(tokenize, batched=True)
    dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

    # encoder has full label list
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=len(label_encoder.classes_)
    )

    # Training args
    args = TrainingArguments(
        output_dir="./results",
        per_device_train_batch_size=8,
        num_train_epochs=5,
        logging_dir="./logs",
        save_strategy="no"
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset
    )

    trainer.train()

    # Save model/tokenizer/label encoder
    model.save_pretrained("my_intent_model")
    tokenizer.save_pretrained("my_intent_model")

    with open("label_encoder.pkl", "wb") as f:
        pickle.dump(label_encoder, f)

    print("Training complete and saved.")

if __name__ == "__main__":
    train_model()
