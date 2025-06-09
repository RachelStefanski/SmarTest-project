import torch
from transformers import AutoTokenizer, DebertaV2ForSequenceClassification
import torch.nn.functional as F

def get_prediction(model, tokenizer, sentence1, sentence2):
    model.eval()
    inputs = tokenizer(sentence1, sentence2, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=1).squeeze().tolist()
        prediction = torch.argmax(logits, dim=1).item()
    return prediction, probs

def main():
    # טקסט לבדיקה
    sentence1 = "The weather is nice today."
    sentence2 = "It is sunny and warm outside."

    # הנתיב המקומי למודל המאומן
    trained_model_path = r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\nli_deberta_trained"
    # שם המודל המקורי מה־HuggingFace
    hf_model_name = "microsoft/deberta-v3-base"

    # טוען את הטוקנייזר פעם אחת
    tokenizer = AutoTokenizer.from_pretrained(trained_model_path)

    # טוען את המודל הלא מאומן מהאינטרנט
    model_hf = DebertaV2ForSequenceClassification.from_pretrained(hf_model_name, num_labels=3)
    
    # טוען את המודל המאומן מקומית
    model_trained = DebertaV2ForSequenceClassification.from_pretrained(trained_model_path)

    # תחזיות
    pred_hf, probs_hf = get_prediction(model_hf, tokenizer, sentence1, sentence2)
    pred_trained, probs_trained = get_prediction(model_trained, tokenizer, sentence1, sentence2)

    # הדפסה
    labels = ["entailment", "neutral", "contradiction"]
    print("\n--- Hugging Face model ---")
    print("Prediction:", labels[pred_hf])
    print("Probabilities:", dict(zip(labels, [round(p, 3) for p in probs_hf])))

    print("\n--- Trained model ---")
    print("Prediction:", labels[pred_trained])
    print("Probabilities:", dict(zip(labels, [round(p, 3) for p in probs_trained])))

    # השוואה
    print("\n=== Comparison ===")
    if pred_hf == pred_trained:
        print("✅ Same prediction")
    else:
        print("❌ Different prediction")

if __name__ == "__main__":
    main()
