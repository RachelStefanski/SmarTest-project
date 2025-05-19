import json
import question_analysis

# --- עיבוד שאלה יחידה --- 
def process_question(question_data):
    question_id = question_data.get('question_id')
    question_type = question_data.get('type', '')
    question_text = question_data.get('question', '')
    model_answer = question_data.get('model_answer', [])
    score = question_data.get('score', 0)

    # חילוץ דרישות מתוך טקסט השאלה
    requirements = question_analysis.extract_requirements(question_text)

    student_answers = question_data.get('student_answers', [])

    # עדכון הדרישות בשאלה
    question_data['requirements'] = requirements

    return {
        'question_id': question_id,
        'type': question_type,
        'question_text': question_text,
        'model_answer': model_answer,
        'score': score,
        'requirements': requirements,
        'student_answers': student_answers
    }

# --- קריאת כל השאלות מתוך המבחן --- 
def load_exam_data(json_data):
    test_data = json_data.get('test', {})
    works = test_data.get('works', [])

    all_questions = []
    for work in works:
        work_title = work.get('work_title', '')
        questions = work.get('questions', [])

        for question in questions:
            question_info = process_question(question)  # עדכון הדרישות בשאלה
            question_info['work_title'] = work_title
            all_questions.append(question_info)

    return all_questions

# --- הדפסת כל השאלות עם ניתוח --- 
def print_questions_with_analysis(questions):
    print("\n📄 Questions with Analysis:\n")
    for q in questions:
        print(f"Q{q['question_id']} ({q['work_title']}): {q['question_text']}")
        print(f"   Requirements Analysis: {q['requirements']}")
        print("=" * 40)

# --- הדפסת כל תשובות התלמידים --- 
def print_student_exams(json_data):
    students = json_data.get('students', [])
    questions_lookup = {}

    # יצירת מילון בין question_id לבין טקסט השאלה
    for work in json_data.get('test', {}).get('works', []):
        for question in work.get('questions', []):
            qid = question.get('question_id')
            qtext = question.get('question')
            questions_lookup[qid] = qtext

    print("\n📘 Student Exams:\n")
    for student in students:
        student_id = student.get('student_id', 'Unknown')
        exam_title = student.get('exam', 'Unknown Exam')
        print(f"🧑 Student ID: {student_id}")
        print(f"📝 Exam: {exam_title}")
        print("Answers:")
        for answer in student.get('answers', []):
            qid = answer.get('question_id')
            qtext = questions_lookup.get(qid, "[Unknown Question]")
            atext = answer.get('answer', '[No answer]')
            print(f"\n  Q{qid}: {qtext}")
            print(f"  Answer: {atext}")
        print("\n" + "=" * 40 + "\n")

# --- טעינת קובץ JSON --- 
def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- שמירת קובץ JSON לאחר העדכון --- 
def save_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- הפעלה ראשית ---
if __name__ == "__main__":
    file_path = r"C:\Users\User.DESKTOP-HT62HRR\Desktop\Project\server-side\tests\history_test.json"
    exam_data = load_json_file(file_path)
    
    # קריאת השאלות ועדכון הדרישות
    questions = load_exam_data(exam_data)

    # הדפסת השאלות עם הניתוח
    print_questions_with_analysis(questions)

    # הדפסת תשובות תלמידים
    print_student_exams(exam_data)

    # שמירת המבחן עם הדרישות המעודכנות
    save_json_file(file_path, exam_data)

    print("✓ כל הדרישות עודכנו ונשמרו בקובץ.")

#  עבור כל תשובת מודל לשאלה - ניתוח לפי קטגוריות
