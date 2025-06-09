import spacy

# טעינת המודל של spaCy עם וקטורים
nlp = spacy.load("en_core_web_md")

# חילוץ תפקידים תחביריים בסיסיים: נושא, מושא וכו'
def extract_roles(doc):
    roles = {"nsubj": None, "dobj": None, "agent": None, "nsubjpass": None}
    for token in doc:
        if token.dep_ in roles:
            roles[token.dep_] = token
        elif token.dep_ == "agent":
            for child in token.children:
                if child.dep_ == "pobj":
                    roles["agent"] = child
    return roles

# נורמליזציה של נושא ומושא – תומך גם בפסיבי וגם באקטיבי
def get_normalized_roles(roles):
    subject = roles["nsubj"] or roles["agent"]
    obj = roles["dobj"] or roles["nsubjpass"]
    return subject, obj

# חישוב דמיון בטוח בין שני טוקנים
def safe_similarity(tok1, tok2):
    if tok1 and tok2 and tok1.has_vector and tok2.has_vector:
        return tok1.similarity(tok2)
    else:
        return 0.0

# השוואה בין שני משפטים לפי מבנה תחבירי ודמיון
def compare_roles(teacher_answer, student_answer, threshold=0.8):
    teacher_doc = nlp(teacher_answer)
    student_doc = nlp(student_answer)

    teacher_roles = extract_roles(teacher_doc)
    student_roles = extract_roles(student_doc)

    teacher_subj, teacher_obj = get_normalized_roles(teacher_roles)
    student_subj, student_obj = get_normalized_roles(student_roles)

    # אם אי אפשר לחלץ את כל התפקידים – לא לפסול
    if not all([teacher_subj, teacher_obj, student_subj, student_obj]):
        return True

    # דמיון בין תפקידים מקבילים
    subj2subj = safe_similarity(teacher_subj, student_subj)
    obj2obj = safe_similarity(teacher_obj, student_obj)

    # דמיון בין תפקידים הפוכים (נושא מול מושא)
    subj2obj = safe_similarity(teacher_subj, student_obj)
    obj2subj = safe_similarity(teacher_obj, student_subj)

    correct_structure = (subj2subj + obj2obj) / 2
    reversed_structure = (subj2obj + obj2subj) / 2

    # פסילה אם ההיפוך חזק יותר מהמבנה התקין וגם עובר את הסף
    if abs(reversed_structure) > correct_structure and abs(reversed_structure) > threshold:
        return False
    return True

# דוגמאות בדיקה
if __name__ == "__main__":
    teacher = "The boy kicked the ball"
    student1 = "The boy hit the ball"          
    # student2 = "The cat was chased by the dog"   # נכון → True
    # student3 = "A dog chased a cat"              # ניסוח דומה → True

    print("student1:", compare_roles(teacher, student1))  # False
    # print("student2:", compare_roles(teacher, student2))  # True
    # print("student3:", compare_roles(teacher, student3))  # True
    true_synonym_examples = [
        # subject synonym
        ("The teacher praised the student",     "The instructor praised the student"),     # "teacher" ≈ "instructor"
        ("The child drew the picture",          "The kid drew the picture"),               # "child" ≈ "kid"
        ("The man fixed the car",               "The guy fixed the car"),                  # "man" ≈ "guy"
        
        # object synonym
        ("The dog chased the rabbit",           "The dog chased the bunny"),               # "rabbit" ≈ "bunny"
        ("The artist painted the house",        "The artist painted the home"),            # "house" ≈ "home"
        ("The chef cooked the dinner",          "The chef cooked the meal"),               # "dinner" ≈ "meal"

        # both subject and object synonyms
        ("The girl hugged the puppy",           "The kid embraced the dog"),               # "girl" ≈ "kid", "hugged" ≈ "embraced", "puppy" ≈ "dog"
        ("The police caught the thief",         "The officers captured the criminal"),     # "police" ≈ "officers", "thief" ≈ "criminal"
    ]
    false_synonym_examples = [
        ("The cat chased the mouse",            "The mouse chased the cat"),               # התהפכו
        ("The boy helped the girl",             "The girl helped the boy"),                # התהפכו
        ("The manager promoted the worker",     "The worker promoted the manager"),        # התהפכו
        ("The soldier defended the city",       "The city defended the soldier"),          # התהפכו
        ("The player kicked the ball",          "The ball kicked the player"),             # התהפכו
    ]
    print("True cases (should return True):")
    for i, (t, s) in enumerate(true_synonym_examples, 1):
        print(f"Example {i}: {compare_roles(t, s)}")

    print("\nFalse cases (should return False):")
    for i, (t, s) in enumerate(false_synonym_examples, 1):
        print(f"Example {i}: {compare_roles(t, s)}")

