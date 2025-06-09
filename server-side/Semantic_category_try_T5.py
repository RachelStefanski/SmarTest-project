import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
import json

# 1. טוענים את ה-tokenizer והמודל
model_name = 't5-small'  # אתה יכול לשנות ל- t5-base או תדרוש מודל יותר גדול
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# 2. מכינים את הנתונים
# טוען קובץ JSON
data = pd.read_json(r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\train_BERT_EN\t5_dataset_ready.json")

# 3. המרת הנתונים לפורמט מתאים
def preprocess_data(examples):
    input_text = examples["text"]
    target_text = examples["target_text"]
    
    # המרת ה-target_text ממחרוזת JSON למילון
    target_text = [json.loads(t) for t in target_text]
    
    # Tokenize את הקלט ואת הפלט
    input_encodings = tokenizer(input_text, padding="max_length", truncation=True, max_length=64)
    target_encodings = tokenizer([str(t) for t in target_text], padding="max_length", truncation=True, max_length=64)
    
    return {
        'input_ids': input_encodings['input_ids'],
        'attention_mask': input_encodings['attention_mask'],
        'labels': target_encodings['input_ids']
    }

# 4. המרת המידע לפורמט Dataset של Hugging Face
dataset = Dataset.from_pandas(data)  # אם data הוא DataFrame, השתמש ב- from_pandas
dataset = dataset.map(preprocess_data, batched=True)

# 5. הגדרת פרמטרים לאימון
training_args = TrainingArguments(
    output_dir="./results",          # מקום שמאחסן את התוצאות
    evaluation_strategy="epoch",     # הערכה אחרי כל אפוק
    learning_rate=2e-5,              # שיעור הלמידה
    per_device_train_batch_size=8,   # גודל המיני-בצ' באימון
    per_device_eval_batch_size=8,    # גודל המיני-בצ' בהערכה
    num_train_epochs=3,              # מספר אפוקים
    weight_decay=0.01,               # ירידת משקל
    save_steps=10_000,               # שמירה כל 10,000 צעדים
    save_total_limit=2,              # הגבלת מספר הקבצים השמורים
)

# 6. יצירת ה- Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    eval_dataset=dataset,  # שים לב שאתה יכול להוסיף גם נתוני בדיקה אם יש לך
)

# 7. תחילת האימון
trainer.train()
import os
print("Working directory:", os.getcwd())

# שמירת המודל המאומן
model.save_pretrained("train_T5")
tokenizer.save_pretrained("train_T5")
