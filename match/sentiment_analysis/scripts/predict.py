from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


model_name = "tabularisai/multilingual-sentiment-analysis"

def predict_sentiment(texts, model_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_map = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
    return [sentiment_map[p] for p in torch.argmax(probabilities, dim=-1).tolist()]

if __name__ == "__main__":
    texts = ["I love this!","Ortho thakle gorther obhab hoy na", "মাগি নাস্তিক", "বড় একটা মাদারচুড একটা রাজাকার যে মিনিটেই কথা বদলাাই"]
    predictions = predict_sentiment(texts, "F:/Rest Api/Cricscore/match/sentiment_analysis/models/fine_tuned_model_2")
    print(predictions)
