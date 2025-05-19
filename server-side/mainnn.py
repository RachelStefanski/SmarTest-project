from fastapi import FastAPI
import Question_analysis
import Question_breakdown
import my_splitter

# יצירת תשובת מורה
teacher_text = "Political causes included: (1) the lack of colonial representation in the British Parliament (“no taxation without representation”), and (2) the increasing control of British authorities over colonial governments. Economic causes included: (1) heavy taxation through laws like the Stamp Act and the Townshend Acts, and (2) trade restrictions that hurt colonial merchants. These issues made colonists feel oppressed and fueled resentment against British rule, ultimately leading to organized resistance and the demand for independence."
teacher_units = my_splitter.split_text(teacher_text)
teacher_answer = Answer(raw_text=teacher_text)
teacher_answer.units_by_category = {category: [] for category in categories}  # נניח מילוי בהמשך

# יצירת אובייקט שאלה עם תשובת מורה ודרישות
question = Question(text=question_text, teacher_answer=teacher_answer, requirements=requirements)
assignment.questions.append(question)

# טקסט תשובת תלמיד
student_text = "One political cause of the American Revolution was that the colonies had no representation in the British Parliament, which made them feel their voices were ignored. Another political cause was the growing interference of the British government in local colonial affairs, which limited their self-rule. Economically, Britain imposed harsh taxes like the Stamp Act, which forced colonists to pay extra without consent. Also, strict trade laws, like the Navigation Acts, limited where colonists could sell or buy goods, hurting their economy. These political and economic pressures created anger and a desire for freedom, pushing the colonies toward revolution."
student_units = my_splitter.split_text(student_text)

# יצירת אובייקט תשובת תלמיד
student_answer = StudentAnswer(student_id="student_001", question_index=0, raw_text=student_text)
student_answer.answer = Answer(raw_text=student_text)
student_answer.answer.units_by_category = {category: [] for category in categories}  # כמו אצל המורה

# שמירת תשובת התלמיד תחת העבודה
assignment.student_answers.setdefault(student_answer.student_id, []).append(student_answer)

# שלב דוגמה - מילוי מטריצה
categories_matrix = [[], []]
Question_breakdown.Fill_matrix(categories_matrix, teacher_units, student_units, requirements, categories)

# החזרת נתונים בדיקה
return {
    "categories": categories,
    "teacher_units": teacher_units,
    "student_units": student_units,
    "categories_matrix": categories_matrix
}
if __name__ == "__main__":
    result = create_exam()
    from pprint import pprint
    pprint(result)
