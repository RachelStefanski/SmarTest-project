# exam_model.py
# מודל נתונים לייצוג מבחן, הכולל עבודות, שאלות, דרישות, תשובות מורה ותלמיד, והשוואות

class Requirement:
    # דרישה של שאלה – לדוגמה: "ציין שני גורמים היסטוריים"
    def __init__(self, category, quantity_type="default", quantity=None, min_val=None, max_val=None):
        self.category = category  # קטגוריה (למשל: "גורמים היסטוריים")
        self.quantity_type = quantity_type  # טיפוס דרישה: default / exact / min/max
        self.quantity = quantity  # אם quantity_type הוא exact
        self.min = min_val  # מינימום דרוש
        self.max = max_val  # מקסימום מותר

class Answer:
    # תשובה של מורה או תלמיד (לפני או אחרי ניתוח)
    def __init__(self, raw_text):
        self.raw_text = raw_text  # הטקסט המקורי של התשובה
        self.units_by_category = {}  # קטגוריה → רשימת יחידות
        self.embeddings_by_category = {}  # קטגוריה → וקטורי embedding של היחידות
        self.class_confidence_by_unit = {}  # מיפוי: (קטגוריה, אינדקס יחידה) → ביטחון המודל

class ComparisonResult:
    # תוצאה של השוואת תשובת תלמיד לתשובת מורה
    def __init__(self):
        self.similarity_matrix = []  # מטריצת דמיון בין יחידות מורה לתלמיד (אופציונלי)
        self.matches = []  # רשימת התאמות: (אינדקס מורה, אינדקס תלמיד, ציון)
        self.score = 0  # הציון הסופי של התלמיד לשאלה הזו

class Question:
    # שאלה אחת במבחן
    def __init__(self, text, teacher_answer, requirements):
        self.text = text  # טקסט השאלה
        self.teacher_answer = teacher_answer  # תשובת מורה (מחלקת Answer)
        self.requirements = requirements  # רשימת דרישות שאלה (Requirement)
        self.teacher_analysis_done = False  # האם ניתוח התשובה בוצע כבר

class Assignment:
    # עבודה אחת בתוך מבחן (קבוצת שאלות)
    def __init__(self, name):
        self.name = name  # שם העבודה
        self.questions = []  # רשימת שאלות
        self.student_answers = {}  # student_id → רשימת תשובות (StudentAnswer)

    def get_question_weight(self):
        # משקל שווה לכל שאלה בעבודה
        return 1 / len(self.questions) if self.questions else 0

class StudentAnswer:
    # תשובה של תלמיד לשאלה מסוימת
    def __init__(self, student_id, question_index, raw_text):
        self.student_id = student_id  # מזהה תלמיד
        self.question_index = question_index  # אינדקס שאלה ברשימת השאלות
        self.raw_text = raw_text  # תשובת התלמיד כפי שנכתבה
        self.answer = None  # תשובה לאחר ניתוח (מחלקת Answer)
        self.comparison_result = None  # תוצאה של ההשוואה מול תשובת המורה

class Exam:
    # מבחן שלם – כולל עבודות
    def __init__(self, exam_id):
        self.exam_id = exam_id  # מזהה מבחן
        self.assignments = []  # רשימת עבודות (Assignment)

    def get_assignment_by_name(self, name):
        # שליפה לפי שם עבודה
        for a in self.assignments:
            if a.name == name:
                return a
        return None
