# from transformers import DebertaV2ForSequenceClassification, DebertaV2Tokenizer
# from torch.utils.data import DataLoader, Dataset
# from transformers import Trainer, TrainingArguments, EarlyStoppingCallback
# import torch
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report, confusion_matrix
# import json

#  # פונקציה לטעינת הנתונים
# def load_data(jsonl_file, max_samples=None):
#      pairs = []
#      labels = []
#      with open(jsonl_file, 'r', encoding='utf-8') as f:
#          for line in f:
#              data = json.loads(line)
#              label = data['gold_label']
#              if label not in ['entailment', 'neutral', 'contradiction']:
#                  continue
#              sentence1 = data['sentence1']
#              sentence2 = data['sentence2']
#              pairs.append((sentence1, sentence2))
#              labels.append(label)
#              if max_samples and len(pairs) >= max_samples:
#                 break
#                 return pd.DataFrame({'sentence1': [p[0] for p in pairs],
#                           'sentence2': [p[1] for p in pairs],
#                           'label': labels})
#  # מחלקה ל-Dataset עבור אימון והערכה
# class NLI_Dataset(Dataset):
#     def __init__(self, dataframe, tokenizer, label_map, max_length=512):
#         self.sentences1 = dataframe['sentence1'].tolist()
#         self.sentences2 = dataframe['sentence2'].tolist()
#         self.labels = dataframe['label_id'].tolist()
#         self.tokenizer = tokenizer
#         self.label_map = label_map
#         self.max_length = max_length
#     def __len__(self):
#         return len(self.sentences1)
#     def __getitem__(self, idx):
#         encoding = self.tokenizer.encode_plus(
#             self.sentences1[idx], self.sentences2[idx],
#             truncation=True,
#             max_length=self.max_length,
#             padding='max_length',
#             return_tensors='pt'
#         )
#         return {
#             'input_ids': encoding['input_ids'].flatten(),
#             'attention_mask': encoding['attention_mask'].flatten(),
#             'labels': torch.tensor(self.labels[idx], dtype=torch.long)
#         }
# if __name__ == '__main__':
#     # טוען את הדאטה
#     df = load_data(r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\train_deberta\snli_1.0\snli_1.0_train.jsonl", max_samples=20000)
#     # ממפה תוויות
#     label_map = {'entailment': 0, 'neutral': 1, 'contradiction': 2}
#     df['label_id'] = df['label'].map(label_map)
#     # מפצל ל-train/test
#     train_df, test_df = train_test_split(df, test_size=0.1, random_state=42, stratify=df['label_id'])
#     # טוען את הטוקניזר
#     tokenizer = DebertaV2Tokenizer.from_pretrained('microsoft/deberta-v3-base')
#     # יוצר את המודל
#     model = DebertaV2ForSequenceClassification.from_pretrained('microsoft/deberta-v3-base', num_labels=3)
#     # יוצר את ה-Dataset לאימון והערכה
#     train_dataset = NLI_Dataset(train_df, tokenizer, label_map)
#     test_dataset = NLI_Dataset(test_df, tokenizer, label_map)
#     # הגדרת פרמטרי אימון
#     training_args = TrainingArguments(
#         output_dir='./results',          # תיקיית פלט
#         evaluation_strategy="steps",     # הערכה כל מספר steps
#         num_train_epochs=3,              # הגדל את מספר ה-epochs
#         per_device_train_batch_size=32,  # הגדל את ה-batch size
#         per_device_eval_batch_size=64,   # batch size להערכה
#         weight_decay=0.01,               # weight decay
#         logging_dir='./logs',            # תיקיית לוגים
#         logging_steps=100,               # כל כמה steps לעשות לוג
#         save_steps=100,                  # כל כמה steps לשמור את המודל
#         load_best_model_at_end=True,     # טען את המודל הטוב ביותר בסיום
#         metric_for_best_model="accuracy",# השתמש ב-accuracy להערכת המודל הטוב ביותר
#     )
#     # יצירת EarlyStoppingCallback
#     early_stopping_callback = EarlyStoppingCallback(early_stopping_patience=2)  # עצירה מוקדמת אחרי 2 סבבים ללא שיפור
#     # יוצר את ה-Trainer
#     trainer = Trainer(
#         model=model,
#         args=training_args,
#         train_dataset=train_dataset,
#         eval_dataset=test_dataset,
#         tokenizer=tokenizer,
#         callbacks=[early_stopping_callback]  # הוספת callback של עצירה מוקדמת
#     )
#     # מתחיל את האימון
#     print("Training model...")
#     trainer.train()
#     # שומר את המודל
#     model.save_pretrained("nli_deberta_trained")
#     # טוען dev set
#     dev_df = load_data(r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\train_deberta\snli_1.0\snli_1.0_dev.jsonl", max_samples=20000)
#     dev_df['label_id'] = dev_df['label'].map(label_map)
#     # חיזוי על dev
#     dev_dataset = NLI_Dataset(dev_df, tokenizer, label_map)
#     dev_data = [(item['input_ids'], item['attention_mask']) for item in dev_dataset]
#     dev_labels = dev_df['label_id'].tolist()
#     print("Evaluating on dev set...")
#     preds = trainer.predict(dev_dataset)
#     pred_classes = np.argmax(preds.predictions, axis=1)
#     # דיווח תוצאות
#     print(classification_report(dev_labels, pred_classes, target_names=label_map.keys()))

#     # הדפסת confusion matrix
#     print("Confusion Matrix:")
#     print(confusion_matrix(dev_labels, pred_classes))
#     # טוען את קובץ ה-test
#     test_df = load_data(r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\train_deberta\snli_1.0\snli_1.0_test.jsonl", max_samples=20000)
#     test_df['label_id'] = test_df['label'].map(label_map)
#     # חיזוי על test
#     test_dataset = NLI_Dataset(test_df, tokenizer, label_map)
#     test_data = [(item['input_ids'], item['attention_mask']) for item in test_dataset]
#     test_labels = test_df['label_id'].tolist()
#     print("Evaluating on test set...")
#     preds = trainer.predict(test_dataset)
#     pred_classes = np.argmax(preds.predictions, axis=1)
#     # דיווח תוצאות
#     print("Test set evaluation results:")
#     print(classification_report(test_labels, pred_classes, target_names=label_map.keys()))
#     # הדפסת confusion matrix
#     print("Confusion Matrix (Test Set):")
#     print(confusion_matrix(test_labels, pred_classes))
#     print("Evaluation complete.")

from transformers import DebertaV2ForSequenceClassification, DebertaV2Tokenizer
import torch
import torch.nn.functional as F

# # טוען את המודל והטוקניזר
# model_path = "nli_deberta_trained"
# model = DebertaV2ForSequenceClassification.from_pretrained(model_path)
# tokenizer = DebertaV2Tokenizer.from_pretrained(model_path)

# # העבר למצב הערכה
# model.eval()
# def predict_nli(sentence1, sentence2):
#     inputs = tokenizer.encode_plus(
#         sentence1, sentence2,
#         return_tensors='pt',
#         truncation=True,
#         padding='max_length',
#         max_length=512
#     )

#     with torch.no_grad():
#         outputs = model(**inputs)
#         logits = outputs.logits
#         probs = F.softmax(logits, dim=1)
#         predicted_class = torch.argmax(probs).item()

#     label_map_inv = {0: 'entailment', 1: 'neutral', 2: 'contradiction'}
#     return label_map_inv[predicted_class], probs.squeeze().tolist()
# sentence1 = "The chef added extra spices to the dish to enhance the flavor."
# sentence2 = "The dish was served with a side of rice."

# label, probabilities = predict_nli(sentence1, sentence2)
# print(f"Prediction: {label}")
# print(f"Probabilities: {probabilities}")


# import json
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch

# # טען את המודל וה-tokenizer
# model_path = "nli_deberta_trained"
# model = DebertaV2ForSequenceClassification.from_pretrained(model_path)
# tokenizer = DebertaV2Tokenizer.from_pretrained(model_path)

# # טען את קובץ ה-JSON
# with open(r"C:\Users\User.DESKTOP-HT62HRR\Downloads\nli_examples.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# # עבור כל זוג של premise והיפותזה, בצע חיזוי
# for example in data:
#     premise = example["premise"]
#     hypothesis = example["hypothesis"]
    
#     # קידוד הזוג
#     inputs = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
#     with torch.no_grad():
#         logits = model(**inputs).logits
#         probabilities = torch.softmax(logits, dim=1).squeeze().tolist()

#     labels = ["entailment", "neutral", "contradiction"]
#     predicted_label = labels[probabilities.index(max(probabilities))]

#     print(f"Premise: {premise}")
#     print(f"Hypothesis: {hypothesis}")
#     print(f"Prediction: {predicted_label}")
#     print(f"Probabilities: {probabilities}")
#     print("-" * 40)



import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def predict_nli(premise, hypothesis, tokenizer, model):
    inputs = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=-1).item()
    return prediction  # 0: contradiction, 1: neutral, 2: entailment

def evaluate_model_on_file(filepath, model_name="nli_deberta_trained"):
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Load dataset
    data = load_data(filepath)

    correct = 0
    total = len(data)

    label_map = {"contradiction": 0, "neutral": 1, "entailment": 2}

    for sample in tqdm(data):
        premise = sample["premise"]
        hypothesis = sample["hypothesis"]
        true_label = label_map[sample["label"]]
        
        # Predict using the model
        pred_label = predict_nli(premise, hypothesis, tokenizer, model)
        
        # Print premise, hypothesis, true label, and predicted label for debugging
        print(f"Premise: {premise}")
        print(f"Hypothesis: {hypothesis}")
        print(f"True Label: {true_label}, Predicted Label: {pred_label}")
        print("-" * 50)
        
        if pred_label == true_label:
            correct += 1

    accuracy = correct / total
    print(f"Accuracy on {total} samples: {accuracy:.2%}")
    return accuracy

# Call the function with the path to your data file
evaluate_model_on_file(r"C:\Users\User.DESKTOP-HT62HRR\Downloads\nli_realistic_100.json")
