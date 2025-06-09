from sentence_transformers import SentenceTransformer
import units_classification
import semantic_similarity
import heapq
import nli_deberta
import syntactic_analysis
from sentence_transformers import CrossEncoder
import ans_splitter
import question_analysis

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
feedbacks = []
# מחלקה לייצוג התאמה בין יחידות תשובה של מורה ותלמיד
class cat_match_units:
    def __init__(self, category, quantity):
        self.cat = category  # קטגוריה
        self.quantity = quantity  # כמות נדרשת
        self.count = 0 #ספירת התאמות שנמצאו
        self.scores = [] # מערך ציוני התאמות לקטגוריה

    # הוספת ציון התאמה
    def add_score(self, score, i, j, text):
        self.scores.append((score, i, j, text))
        self.count += 1
        print(f"  Added score {score:.3f} for teacher unit {i} and student unit {j} with text snippet: '{text[:30]}...'")
        
    # בדיקת האם כמות ההתאמות הגיעה למכסה הנדרשת
    def is_full(self):
        return self.count >= self.quantity

    def __repr__(self):
        return f"AnswerUnit(text='{self.text[:30]}...', category='{self.category}')"
# הדפסת מטריצת הדמיון
def print_matrix(matrix):
    print("\n--- Similarity Matrix ---")
    for row in matrix:
        print(["{:.3f}".format(v) for v in row])


def greedy_maximum_matching(similarity_matrix, teacher_answer_units, student_answer_units, Question_requirements):
    print("\nStarting greedy maximum matching...")

    # הכנת מילון category -> match object
    optimal_matches = {
        req.get("category", "unknown"): cat_match_units(
            req.get("category", "unknown"),
            req.get("quantity", 0)
        ) for req in Question_requirements
    }

    max_heap = []
    visited_teacher = [False] * len(teacher_answer_units)
    visited_student = [False] * len(student_answer_units)

    # בניית ערימת מקסימום מהנקודות במטריצת הדמיון עם ערך חיובי
    for i, row in enumerate(similarity_matrix):
        for j, score in enumerate(row):
            if score > 0:
                heapq.heappush(max_heap, (-score, i, j))

    # בחירת ההתאמות הטובות ביותר מבלי לחזור על יחידות כבר משוייכות
    while max_heap:
        neg_score, i, j = heapq.heappop(max_heap)
        score = -neg_score
        if not visited_teacher[i] and not visited_student[j] and score > 0:
            student_text, student_cat = student_answer_units[j]
            teacher_text, teacher_cat = teacher_answer_units[i]
            # הדפסות דיבאג שיעזרו לבדוק התאמה בקטגוריות וציונים
            print(f"Checking pair: teacher[{i}]({teacher_cat}) <-> student[{j}]({student_cat}), score={score}")
            if student_cat == teacher_cat and teacher_cat in optimal_matches:
                match_obj = optimal_matches[teacher_cat]
                if not match_obj.is_full():
                    print(f"Match accepted for category {teacher_cat}: score {score}")
                    match_obj.add_score(score, i, j, student_text)
                    visited_teacher[i] = True
                    visited_student[j] = True
                else:
                    print(f"Category {teacher_cat} is full, skipping")
            else:
                print(f"Categories don't match or category {teacher_cat} not in requirements")
        print("Finished greedy matching.")
    return optimal_matches


def calculating_score(teacher_answer_units, student_answer, Question_requirements, question_score, cross_model, embed_model, question_type):
    
    if question_type != "open":
        def normalize(text):
            return str(text).strip().lower()

        # תומך גם במקרה ש-teacher_answer_units היא רשימה
        student_answer_normalized = normalize(student_answer)
        model_answers = teacher_answer_units if isinstance(teacher_answer_units, list) else [teacher_answer_units]
        normalized_model_answers = [normalize(ans) for ans in model_answers]

        if student_answer_normalized in normalized_model_answers:
            return question_score, ["Perfect"]
        else:
            return 0, ["wrong answer"]
    else:

        student_answer_units = ans_splitter.split_text(student_answer)
        student_answer_units = units_classification.match_units_to_categories(
        student_answer_units, [question_analysis.Requirement.from_dict(r) for r in Question_requirements], cross_model
    )

        similarity_matrix = [[0 for _ in range(len(student_answer_units))] for _ in range(len(teacher_answer_units))]

        for i, teacher_unit in enumerate(teacher_answer_units):
            teacher_emb = teacher_unit["embedding"]
            teacher_cat = teacher_unit["category"]
            teacher_text = teacher_unit["text"]
            for j, (student_text, student_cat) in enumerate(student_answer_units):
                if teacher_cat == student_cat:
                    contradiction, probs = nli_deberta.detecting_contradiction(teacher_text, student_text) 
                    syntax_ok = syntactic_analysis.compare_roles(teacher_text, student_text) 
                    sem_similarity = semantic_similarity.cal_similarity(teacher_emb, student_text, embed_model)

                    if contradiction == "entailment" and probs > 0.95:
                        similarity = 1
                    elif contradiction == "contradiction" and not syntax_ok:
                        similarity = -1
                    elif sem_similarity >= 0.5:
                        similarity = sem_similarity
                    else:
                        similarity = 0

                    similarity_matrix[i][j] = similarity

        print_matrix(similarity_matrix)

        optimal_matches = greedy_maximum_matching(
            similarity_matrix,
            [(u["text"], u["category"]) for u in teacher_answer_units],
            student_answer_units,
            Question_requirements
        )

        total_requirements = sum(req.get('quantity', 0) for req in Question_requirements if req.get('quantity') is not None)
        unit_score = question_score / total_requirements if total_requirements else 0
        total_score = 0
        feedbacks = []

        for req in Question_requirements:
            cat = req.get('category')
            required = req.get('quantity', 0)
            match_obj = optimal_matches.get(cat)
            matched_scores = sorted(match_obj.scores, reverse=True) if match_obj else []
            matched_count = min(len(matched_scores), required)

            score_contrib = sum(score * unit_score for score, _, _, _ in matched_scores[:matched_count])
            total_score += score_contrib

            if matched_count < required:
                missing = required - matched_count
                feedbacks.append(f"Missing {missing} unit{'s' if missing > 1 else ''} from category '{cat}'")

            for score, i, j, student_text in matched_scores[:matched_count]:
                if score == 1:
                    continue  # לא צריך פידבק
                elif score == -1:
                    feedbacks.append(f"Contradictory answer in category '{cat}': '{student_text[:40]}...'")
                elif score >= 0.5:
                    feedbacks.append(f"Imprecise answer in category '{cat}': '{student_text[:40]}...'")
                else:
                    feedbacks.append(f"Irrelevant answer in category '{cat}': '{student_text[:40]}...'")
        
        return total_score, feedbacks
