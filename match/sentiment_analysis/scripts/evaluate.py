from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import classification_report
import torch
from datasets import load_dataset
from torch.utils.data import DataLoader
from pathlib import Path


def evaluate_model( val_path):
    # Load the tokenizer and model
    model_dir = "F:/Rest Api/Cricscore/match/sentiment_analysis/models/fine_tuned_model_2/checkpoint-1658"
    tokenizer = AutoTokenizer.from_pretrained(
    model_dir, 
    local_files_only=True,
    use_fast=True  # Ensures using the correct tokenizer version
    )
    print("Tokenizer loaded successfully!")
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()

    # Load validation dataset
    dataset = load_dataset("csv", data_files={"val": val_path})["val"]

    # Tokenize the dataset
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding=True, max_length=512)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    tokenized_dataset = tokenized_dataset.remove_columns(["text"])  # Keep only necessary columns

    # Convert labels and inputs to tensors
    tokenized_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
    inputs = {key: tokenized_dataset[key] for key in ["input_ids", "attention_mask"]}
    labels = tokenized_dataset["label"]

    # Move model and inputs to the appropriate device (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = {key: val.to(device) for key, val in inputs.items()}
    labels = labels.to(device)

    # Make predictions
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, axis=-1)

    # Generate classification report
    predictions = predictions.cpu().tolist()
    labels = labels.cpu().tolist()
    print(classification_report(labels, predictions))

if __name__ == "__main__":
    evaluate_model(
        # "F:/Rest Api/Cricscore/match/sentiment_analysis/models/fine_tuned_model_2/checkpoint-1658",
        
        "F:/Rest Api/Cricscore/match/sentiment_analysis/data/val.csv",
    )
