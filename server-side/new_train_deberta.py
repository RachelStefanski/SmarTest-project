# from transformers import DebertaV2ForSequenceClassification, DebertaV2Tokenizer
# from torch.utils.data import DataLoader, Dataset
# from transformers import Trainer, TrainingArguments, EarlyStoppingCallback
# import torch
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report, confusion_matrix
# import json

# # פונקציה לטעינת הנתונים
# def load_data(jsonl_file, max_samples=None):
#     pairs = []
#     labels = []
#     with open(jsonl_file, 'r', encoding='utf-8') as f:
#         for line in f:
#             data = json.loads(line)
#             label = data['gold_label']
#             if label not in ['entailment', 'neutral', 'contradiction']:
#                 continue
#             sentence1 = data['sentence1']
#             sentence2 = data['sentence2']
#             pairs.append((sentence1, sentence2))
#             labels.append(label)
#             if max_samples and len(pairs) >= max_samples:
#                 break
#     return pd.DataFrame({'sentence1': [p[0] for p in pairs],
#                          'sentence2': [p[1] for p in pairs],
#                          'label': labels})

# # מחלקה ל-Dataset עבור אימון והערכה
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
#         num_train_epochs=3,              # מספר epochs קטן יחסית
#         per_device_train_batch_size=8,   # שמור batch קטן
#         per_device_eval_batch_size=8,    # batch size להערכה
#         weight_decay=0.01,               # weight decay
#         logging_dir='./logs',            # תיקיית לוגים
#         logging_steps=100,               # כל כמה steps לעשות לוג
#         save_steps=100,                  # כל כמה steps לשמור את המודל
#         load_best_model_at_end=True,     # טען את המודל הטוב ביותר בסיום
#         metric_for_best_model="accuracy",# השתמש ב-accuracy להערכת המודל הטוב ביותר
#         gradient_accumulation_steps=2,   # צבירת gradient כדי להפעיל batch גדול יותר
#         fp16=False,                      # הפעלת precision 16 לא תמיד אפשרי על CPU
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


import json
import pandas as pd
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments, EarlyStoppingCallback
from datasets import Dataset
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import torch

# טוען את המודל והטוקניזר - גרסה v3
model_name = "microsoft/deberta-v3-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# טוען את הנתונים
def load_data(jsonl_file, max_samples=None):
    pairs = []
    labels = []
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            label = data['gold_label']
            if label not in ['entailment', 'neutral', 'contradiction']:
                continue
            sentence1 = data['sentence1']
            sentence2 = data['sentence2']
            pairs.append((sentence1, sentence2))
            labels.append(label)
            if max_samples and len(pairs) >= max_samples:
                break
    return pd.DataFrame({'sentence1': [p[0] for p in pairs],
                         'sentence2': [p[1] for p in pairs],
                         'label': labels})

# ממפה תוויות
label_map = {'entailment': 0, 'neutral': 1, 'contradiction': 2}

# טוען את הנתונים
train_df = load_data(r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\train_deberta\snli_1.0\snli_1.0_train.jsonl", max_samples=30000)
dev_df = load_data(r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\train_deberta\snli_1.0\snli_1.0_dev.jsonl", max_samples=3000)
test_df = load_data(r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\train_deberta\snli_1.0\snli_1.0_test.jsonl", max_samples=3000)

# ממיר תוויות למספרים
train_df['label'] = train_df['label'].map(label_map)
dev_df['label'] = dev_df['label'].map(label_map)
test_df['label'] = test_df['label'].map(label_map)

# המרה ל-HuggingFace Dataset
train_dataset = Dataset.from_pandas(train_df)
dev_dataset = Dataset.from_pandas(dev_df)
test_dataset = Dataset.from_pandas(test_df)

# טוקניזציה
def tokenize_function(example):
    tokens = tokenizer(example['sentence1'], example['sentence2'], padding='max_length', truncation=True, max_length=128)
    tokens['label'] = example['label']  # ← מוסיף את label ידנית לאחר הטוקניזציה
    return tokens

train_dataset = train_dataset.map(tokenize_function, batched=True)
dev_dataset = dev_dataset.map(tokenize_function, batched=True)
test_dataset = test_dataset.map(tokenize_function, batched=True)

# הגדרה כ-torch tensors
train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
dev_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])
test_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'label'])

# מודל אחרי הטוקניזציה
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

# פונקציה לחישוב מטריקות
def compute_metrics(pred):
    preds = np.argmax(pred.predictions, axis=1)
    labels = pred.label_ids
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

# פרמטרי אימון
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="steps",
    eval_steps=200,
    save_steps=200,
    logging_steps=100,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    num_train_epochs=3,
    weight_decay=0.01,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
)

def main():
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    )

    # אימון
    print("Training model...")
    trainer.train()

    # שמירה
    model.save_pretrained("nli_deberta_v3_trained")
    tokenizer.save_pretrained("nli_deberta_v3_trained")

    # הערכה על dev
    print("Evaluating on dev set...")
    dev_preds = trainer.predict(dev_dataset)
    dev_pred_classes = np.argmax(dev_preds.predictions, axis=1)
    dev_labels = dev_preds.label_ids

    print(classification_report(dev_labels, dev_pred_classes, target_names=label_map.keys()))
    print("Confusion Matrix (Dev):")
    print(confusion_matrix(dev_labels, dev_pred_classes))

    # הערכה על test
    print("Evaluating on test set...")
    test_preds = trainer.predict(test_dataset)
    test_pred_classes = np.argmax(test_preds.predictions, axis=1)
    test_labels = test_preds.label_ids

    print(classification_report(test_labels, test_pred_classes, target_names=label_map.keys()))
    print("Confusion Matrix (Test):")
    print(confusion_matrix(test_labels, test_pred_classes))

# ← חובה להריץ מתוך main ב-Windows
if __name__ == "__main__":
    main()
