from sentence_transformers import SentenceTransformer, util

# מודל לדמיון סמנטי
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

from sentence_transformers import util

def cal_similarity(teacher_emb, student_text, embed_model):
    emb_student = embed_model.encode(student_text, convert_to_tensor=True)
    semantic_sim = float(util.pytorch_cos_sim(teacher_emb, emb_student))
    return semantic_sim

if __name__ == "__main__":
    # דוגמאות של משפטים להשוואה
    # ניתן להוסיף עוד משפטים כדי לבדוק את הדמיון הסמנטי
    sentence_pairs = [
        ("The boy kicked the ball.", "The child kicked the ball."),  # very similar
        ("She answered the question correctly.", "She responded to the question accurately."),
        ("The girl watched a movie.", "The girl read a book."),       # medium similarity
        ("The cat chased the mouse.", "The mouse chased the cat."),   # inverted meaning
        ("He solved the problem easily.", "The problem was easy for him to solve."),  # paraphrase
        ("He loves playing football.", "He hates playing football."), # contradiction
        ("Tom was reading a novel in his room.", "In his room, Tom was reading a novel.")  # same meaning
    ]
    for sen1, sent2 in sentence_pairs:
        score = cal_similarity(sen1, sent2, semantic_model)
        print("Score:", score)

