from transformers import T5Tokenizer, T5ForConditionalGeneration

# טוען את ה-tokenizer והמודל המאומן
model_name = "train_T5"  # הנתיב שבו שמרת את המודל המאומן
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
input_text = "Explain 2 social impacts and 3 scientific explanations."
# Tokenize את הקלט
input_ids = tokenizer(input_text, return_tensors="pt").input_ids

# הפקת התשובה
output_ids = model.generate(input_ids, max_length=64, num_return_sequences=1)

# המרת התשובה חזרה לטקסט
output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

print(output_text)
