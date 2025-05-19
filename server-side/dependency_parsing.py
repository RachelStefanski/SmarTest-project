import spacy
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# טוען את המודלים
nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# שני משפטים לבדיקה
sentence1 = "The cat chased the dog."
sentence2 = "The dog chased the cat."

# שלב 1: ניתוח תחבירי בסיסי
def extract_structure(doc):
    """
    מחזיר נושא, פועל ראשי, מושא או משלים מהמשפט
    """
    subject = None
    verb = None
    obj_or_comp = None
    for token in doc:
        if token.dep_ == "nsubj":
            subject = token.lemma_
        if token.dep_ == "ROOT":
            verb = token.lemma_
        if token.dep_ in ("dobj", "xcomp"):
            obj_or_comp = token.lemma_
    return subject, verb, obj_or_comp

def structures_match(s1, s2):
    """
    השוואת מבנה תחבירי בסיסי
    """
    matches = sum([a == b for a, b in zip(s1, s2)])
    return matches / 3

# שלב 2: ניתוח המשפטים
doc1 = nlp(sentence1)
doc2 = nlp(sentence2)
structure1 = extract_structure(doc1)
structure2 = extract_structure(doc2)

# שלב 3: ניתוח תחבירי מפורט
def print_dependencies(doc, index):
    print(f"\n● משמעות תחבירית של משפט {index}:")
    for token in doc:
        print(f"{token.text:12} → {token.dep_:10} (ראש: {token.head.text})")

print_dependencies(doc1, 1)
print_dependencies(doc2, 2)

# שלב 4: ניתוח סמנטי
embedding1 = semantic_model.encode([sentence1])
embedding2 = semantic_model.encode([sentence2])
semantic_similarity = cosine_similarity(embedding1, embedding2)[0][0]

# תוצאות
print("\n● מבנה תחבירי בסיסי:")
print(f"משפט 1: {structure1}")
print(f"משפט 2: {structure2}")
print(f"\n● אחוז התאמה תחבירית בסיסית: {structures_match(structure1, structure2) * 100:.0f}%")
print(f"● אחוז דמיון סמנטי: {semantic_similarity * 100:.2f}%")

# שלב 5: זיהוי סתירות אפשריות
def check_for_contradiction(structure1, structure2):
    """
    אם מבני התחביר שונים בתכלית (כמו הפוך סובייקט ומושא), יש סבירות לסתירה
    """
    if structure1[0] != structure2[0] or structure1[1] != structure2[1]:
        print("\n● ישנה סתירה בין המבנים התחביריים של המשפטים.")
    else:
        print("\n● אין סתירה בין המבנים התחביריים של המשפטים.")

# בדוק אם יש סתירה
check_for_contradiction(structure1, structure2)
