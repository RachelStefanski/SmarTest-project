from sentence_transformers import SentenceTransformer
import units_classification
import semantic_similarity
import heapq
import nli_deberta
import syntactic_analysis
from sentence_transformers import CrossEncoder
import answer_processing
import ans_splitter
import units_classification


class answer_unit:
    def __init__(self, text, category, model):
        self.text = text  # טקסט התשובה
        self.emb = model.encode(text, convert_to_tensor=True)  # קידוד טקסט התשובה
        self.category = category  # קטגוריה של התשובה
    def to_dict(self):
        return {
            "text": self.text,
            "category": self.category,
            # embedding אולי תרצי לשמור כרשימה ולא כטנסור, אז להמיר:
            "embedding": self.emb.tolist() if hasattr(self.emb, "tolist") else self.embedding
        }


from sentence_transformers import SentenceTransformer, CrossEncoder

def analyze_teacher_answer(teacher_answer, question_requirements):
    cross_model = CrossEncoder('sentence-transformers/all-MiniLM-L6-v2')
    embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # למטרת encode()

    units = ans_splitter.split_text(teacher_answer)
    teacher_answer_units = []

    for i, unit in enumerate(units):
        print(f"Encoding teacher answer unit {i}: {unit[:30]}...")
        category = units_classification.match_units_to_categories([unit], question_requirements, cross_model)[0][1]
        teacher_answer_units.append(answer_unit(unit, category, embed_model))

    print(teacher_answer_units)
    return teacher_answer_units

    print(techer_answer_units)
    return techer_answer_units
