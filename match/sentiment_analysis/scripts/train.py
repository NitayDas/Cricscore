import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
from datasets import load_dataset, Value
from sklearn.metrics import accuracy_score
import numpy as np

# Optimize GPU memory allocation
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = ""


# For Cpu
device = torch.device("cpu")
torch.cuda.is_available = lambda: False
print(f"Using device: {device}")

# For GPU
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"Using device: {device}")

# Compute evaluation metrics
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {"accuracy": accuracy_score(labels, predictions)}

def train_model(model_name, train_dataset, val_dataset, output_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=5)

    model.to(device)

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    # training_args = TrainingArguments(
    #     output_dir=output_dir,
    #     evaluation_strategy="epoch",
    #     save_strategy="epoch",
    #     learning_rate=5e-5,
    #     per_device_train_batch_size=8,  # Increased batch size for faster training
    #     per_device_eval_batch_size=8,
    #     dataloader_num_workers=4,
    #     gradient_accumulation_steps=4,  # Reduce overhead
    #     num_train_epochs=3,
    #     weight_decay=0.01,
    #     load_best_model_at_end=True,
    #     logging_dir="./logs",
    #     logging_steps=1000,  # Reduce logging frequency to speed up training
    #     metric_for_best_model="accuracy",
    #     report_to="none",
    #     fp16=False,  # Disable mixed precision (only for GPUs)
    #     optim="adamw_torch",  # Use optimized AdamW optimizer
    # )
    
    
    training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="steps",  # Evaluate more frequently
    eval_steps=500,  # Evaluate every 500 steps instead of once per epoch
    save_strategy="steps",
    save_steps=500,  # Save checkpoint every 500 steps
    learning_rate=3e-5,  # More stable fine-tuning LR
    per_device_train_batch_size=16,  # Larger batch for better generalization
    per_device_eval_batch_size=16,
    dataloader_num_workers=4,
    gradient_accumulation_steps=2,  # Lower accumulation for better step updates
    num_train_epochs=3,  # More epochs for better learning
    weight_decay=0.01,
    warmup_ratio=0.06,  # Warmup 6% of training steps for smoother start
    lr_scheduler_type="linear",  # More stable learning rate decay
    logging_dir="./logs",
    logging_steps=500,  # Log every 500 steps
    metric_for_best_model="accuracy",
    greater_is_better=True,  # Ensure higher accuracy is preferred
    report_to="none",
    fp16=False,  # Enable mixed precision (Speeds up training on GPUs)
    optim="adamw_torch",  # Optimized AdamW optimizer
    save_total_limit=1, # Keep only last 1 checkpoints (avoid storage issues)
    load_best_model_at_end=True,  # Keep only last checkpoints 
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    
    model_name = "tabularisai/multilingual-sentiment-analysis"  # Use TinyBERT for lower memory usage
    # Load dataset
    datasets = load_dataset(
        "csv", 
        data_files={ 
            "train": "F:/Rest Api/Cricscore/match/sentiment_analysis/data/train.csv",
            "val": "F:/Rest Api/Cricscore/match/sentiment_analysis/data/val.csv"
        }
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize_function(examples):
        return tokenizer(
            examples["text"], 
            truncation=True, 
            padding="max_length", 
            max_length=256
        )

    # Filter out missing labels
    datasets["train"] = datasets["train"].filter(lambda x: x["label"] is not None)
    datasets["val"] = datasets["val"].filter(lambda x: x["label"] is not None)

    # Convert labels to integers
    def cast_label_to_int(example):
        example["label"] = int(example["label"])
        return example

    datasets["train"] = datasets["train"].map(cast_label_to_int)
    datasets["val"] = datasets["val"].map(cast_label_to_int)

    # Apply tokenization
    datasets = datasets.map(tokenize_function, batched=True, remove_columns=["text"])

    # Cast "label" column to int64
    datasets["train"] = datasets["train"].cast_column("label", Value("int64"))
    datasets["val"] = datasets["val"].cast_column("label", Value("int64"))

    print(f"First train sample: {datasets['train'][0]}")
    print(f"First val sample: {datasets['val'][0]}")

    train_model(model_name, datasets["train"], datasets["val"], "../models/fine_tuned_model_1")
