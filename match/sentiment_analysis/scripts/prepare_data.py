from datasets import load_dataset
from transformers import AutoTokenizer

def prepare_datasets(model_name, train_path, val_path):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Load datasets with error handling
    try:
        dataset = load_dataset("csv", data_files={"train": train_path, "val": val_path})
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return None

    # Check if 'text' and 'labels' columns exist in the dataset
    if 'text' not in dataset['train'].column_names or 'text' not in dataset['val'].column_names:
        print("Error: 'text' column not found in datasets")
        return None
    if 'label' not in dataset['train'].column_names or 'label' not in dataset['val'].column_names:
        print("Error: 'labels' column not found in datasets")
        return None

    # Tokenize datasets
    def tokenize_function(examples):
        tokenized = tokenizer(examples["text"], truncation=True, padding=True, max_length=512)
        tokenized["label"] = examples["label"]  # Include labels in tokenized output
        return tokenized
    
    # Apply tokenization
    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    return tokenized_datasets

if __name__ == "__main__":
    model_name = "tabularisai/multilingual-sentiment-analysis"
    # train_path = "F:/Rest Api/Cricscore/match/sentiment_analysis/data/train.csv"
    # val_path = "F:/Rest Api/Cricscore/match/sentiment_analysis/data/val.csv"
    
    
    train_path = "C:/Users/Md Jannat Hasan/Desktop/Nitay/Cricscore/match/sentiment_analysis/data/train.csv"
    val_path = "C:/Users/Md Jannat Hasan/Desktop/Nitay/Cricscore/match/sentiment_analysis/data/val.csv"
    
    
    # Prepare the datasets
    datasets = prepare_datasets(model_name, train_path, val_path)
    
    if datasets:
        print("Datasets prepared successfully!")
        # You can add additional checks or print dataset information here
        print(datasets["train"][0])  # Checking the first element of the train dataset
    else:
        print("Datasets preparation failed.")
