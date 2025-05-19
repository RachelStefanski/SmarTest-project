from fastapi import FastAPI
import question_analysis
import answer_processing
import ans_splitter

from models import Exam, Assignment, Question, Answer, StudentAnswer, Requirement

# יצירת אובייקט FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/analyze_question")
def analyze_question(question_text: str):
    # הוספת כל הקוד שקשור לניתוח השאלה
    question_requirements_dicts = question_analysis.extract_from_dependencies(question_text)
    requirements = [Requirement(**r) for r in question_requirements_dicts]
    categories = [r.category for r in requirements]

    return {"categories": categories}

@app.post("/create_exam")
def create_exam():
    # יצירת מבחן
    exam = Exam(exam_id="History_Midterm")

    # יצירת עבודה
    assignment = Assignment(name="American Revolution")

    # הוספת העבודה למבחן
    exam.assignments.append(assignment)

    # טקסט השאלה
    question_text = "Identify two political and two economic causes of the American Revolution. Explain how each cause contributed to the outbreak of the war."

    # ניתוח דרישות השאלה
    question_requirements_dicts = question_analysis.extract_requirements(question_text)
    requirements = [Requirement(**r) for r in question_requirements_dicts]
    categories = [r.category for r in requirements]

    # יצירת תשובת מורה
    teacher_text = "Political causes included: (1) the lack of colonial representation in the British Parliament (“no taxation without representation”), and (2) the increasing control of British authorities over colonial governments. Economic causes included: (1) heavy taxation through laws like the Stamp Act and the Townshend Acts, and (2) trade restrictions that hurt colonial merchants. These issues made colonists feel oppressed and fueled resentment against British rule, ultimately leading to organized resistance and the demand for independence."
    teacher_units = ans_splitter.split_text(teacher_text)
    teacher_answer = Answer(raw_text=teacher_text)
    teacher_answer.units_by_category = {category: [] for category in categories}  # נניח מילוי בהמשך

    # יצירת אובייקט שאלה עם תשובת מורה ודרישות
    question = Question(text=question_text, teacher_answer=teacher_answer, requirements=requirements)
    assignment.questions.append(question)

    # טקסט תשובת תלמיד
    student_text = "One political cause of the American Revolution was that the colonies had no representation in the British Parliament, which made them feel their voices were ignored. Another political cause was the growing interference of the British government in local colonial affairs, which limited their self-rule. Economically, Britain imposed harsh taxes like the Stamp Act, which forced colonists to pay extra without consent. Also, strict trade laws, like the Navigation Acts, limited where colonists could sell or buy goods, hurting their economy. These political and economic pressures created anger and a desire for freedom, pushing the colonies toward revolution."
    student_units = ans_splitter.split_text(student_text)

    # יצירת אובייקט תשובת תלמיד
    student_answer = StudentAnswer(student_id="student_001", question_index=0, raw_text=student_text)
    student_answer.answer = Answer(raw_text=student_text)
    student_answer.answer.units_by_category = {category: [] for category in categories}  # כמו אצל המורה

    # שמירת תשובת התלמיד תחת העבודה
    assignment.student_answers.setdefault(student_answer.student_id, []).append(student_answer)

    # שלב דוגמה - חישוב ציון
    # categories_matrix = [[], []]
    answer_processing.calculating_score(teacher_units, student_units, requirements, categories)

    # # החזרת נתונים בדיקה
    # return {
    #     "categories": categories,
    #     "teacher_units": teacher_units,
    #     "student_units": student_units,
    # }
if __name__ == "__main__":
    result = create_exam()
    from pprint import pprint
    pprint(result)


# אם תצטרך להריץ את השרת:
# uvicorn main:app --reload
