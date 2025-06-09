import re
import spacy
import json

# מילון המרת מילים למספרים באנגלית
english_number_words = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

# טען מודל אנגלי
nlp = spacy.load("en_core_web_sm")  # ודא שהמודל מותקן: python -m spacy download en_core_web_sm

# מילון של מילות מפתח לקטגוריות
category_keywords = {
    "reason": ["reason", "reasons"],
    "result": ["result", "results"],
    "conclusion": ["conclusion", "conclusions"],
    "explanation": ["explanation", "explanations"],
    "fact": ["fact", "facts"],
    "example": ["example", "examples"]
}

# Regex שמתאים גם למספרים וגם למילים מספריות
pattern = r'(\d+|\w+)\s*(%s)' % '|'.join([w for v in category_keywords.values() for w in v])

def convert_word_to_number(word):
    """המרת מילה מספרית למספר"""
    return english_number_words.get(word.lower(), None)

def extract_requirements(text):
    """פונקציה עיקרית לזיהוי הדרישות מהשאלה"""
    doc = nlp(text)
    results = []

    # ניתוח באמצעות regex
    matches = re.findall(pattern, text)
    for num_str, cat in matches:
        num = int(num_str) if num_str.isdigit() else convert_word_to_number(num_str)
        if num is None:
            continue
        for key, words in category_keywords.items():
            if cat.lower() in [w.lower() for w in words]:
                results.append({"category": key, "quantity": num})
                break

    # fallback ל-dependency parsing אם regex לא מוצא כלום
    if not results:
        results += extract_from_dependencies(doc)
    print (f"Extracted requirements: {results}")
    return results if results else [{"category": "Unknown", "quantity": 0}]

def extract_from_dependencies(doc):
    """פענוח תחבירי למציאת מספרים + קטגוריות"""
    if isinstance(doc, str):
        doc = nlp(doc)  # הפעלה מחדש במקרה שקיבלנו מחרוזת בטעות

    results = []
    for token in doc:
        num = None
        if token.like_num:
            num = int(token.text) if token.text.isdigit() else convert_word_to_number(token.text.lower())
        elif token.text.lower() in english_number_words:
            num = convert_word_to_number(token.text.lower())

        if num is not None:
            noun = None

            # חיפוש שם עצם בין הצאצאים
            for child in token.children:
                if child.pos_ in {"NOUN", "PROPN"}:
                    noun = child.text
                    break

            # fallback: חיפוש שם עצם לפני או אחרי
            if not noun:
                for offset in [-1, 1]:
                    try:
                        neighbor = doc[token.i + offset]
                        if neighbor.pos_ in {"NOUN", "PROPN"}:
                            noun = neighbor.text
                            break
                    except IndexError:
                        continue

            if noun:
                for key, words in category_keywords.items():
                    if noun.lower() in [w.lower() for w in words]:
                        results.append({"category": key, "quantity": num})
                        break
        return results

# דוגמה לשימוש
if __name__ == "__main__":
    test_sentences = "Identify two political and two economic causes of the American Revolution. Explain how each cause contributed to the outbreak of the war."
    print("Extracted:", extract_requirements(test_sentences))
