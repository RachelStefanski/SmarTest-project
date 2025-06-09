from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
from datetime import datetime, timedelta
from dateutil.parser import parse  # תוספת נחוצה למעלה
import logging
import question_analysis
import ans_techaer_processing
import answer_processing

logging.basicConfig(level=logging.DEBUG)  # הגדרת רמת לוג ברירת מחדל

app = Flask(__name__)
CORS(app)

TESTS_DIR = 'tests'
os.makedirs(TESTS_DIR, exist_ok=True)  # לוודא שהתיקייה קיימת

def load_all_tests():
    tests = []
    for filename in os.listdir(TESTS_DIR):
        if filename.endswith('.json') and not filename.endswith('.answers.json'):
            filepath = os.path.join(TESTS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    test = json.load(f)
                    tests.append(test)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    return tests

@app.route('/')
def home():
    return jsonify(message="Home route")

@app.route('/student/marks', methods=['POST'])
def get_student_marks():
    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    results = []

    for filename in os.listdir(TESTS_DIR):
        if filename.endswith('.answers.json'):
            with open(os.path.join(TESTS_DIR, filename), 'r', encoding='utf-8') as f:
                all_answers = json.load(f)
                for test in all_answers:
                    if test['student_id'] == student_id:
                        total_score = sum(q['score'] for q in test['answers'])
                        max_score = sum(q['max_score'] for q in test['answers'])
                        test['total_score'] = total_score
                        test['max_score'] = max_score
                        results.append(test)

    return jsonify({'tests': results})

@app.route('/api/tests', methods=['GET'])
def get_tests():
    tests = load_all_tests()
    return jsonify(tests)

# @app.route('/api/tests', methods=['POST'])
# def create_new_test():
#     data = request.get_json()
#     teacher_id = data.get('teacher_id')
#     test_name = data.get('test_name')

#     if not teacher_id or not test_name:
#         return jsonify({'error': 'Missing teacher ID or test name'}), 400

#     filename = os.path.join(TESTS_DIR, f"{test_name}.json")
#     if os.path.exists(filename):
#         return jsonify({'error': 'A test with this name already exists'}), 409

#     new_test = {
#         'test_id': str(uuid.uuid4()),
#         'teacher_id': teacher_id,
#         'test_name': test_name,
#         'start_time': data.get('start_time', ''),
#         'duration_minutes': data.get('duration_minutes', ''),
#         'class_ids': data.get('class_ids', []),
#         'works': data.get('works', [])
#     }

#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(new_test, f, ensure_ascii=False, indent=2)

#     return jsonify({
#         'message': 'New test created',
#         'test_id': new_test['test_id'],
#         'test': new_test
#     }), 200

@app.route('/api/tests', methods=['POST'])
def create_new_test():
    print("question_analysis type:", type(question_analysis))
    print("dir:", dir(question_analysis))

    data = request.get_json()
    teacher_id = data.get('teacher_id')
    test_name = data.get('test_name')

    if not teacher_id or not test_name:
        return jsonify({'error': 'Missing teacher ID or test name'}), 400

    filename = os.path.join(TESTS_DIR, f"{test_name}.json")
    if os.path.exists(filename):
        return jsonify({'error': 'A test with this name already exists'}), 409

    works = data.get('works', [])
    print(f"Processing {len(works)} works for new test '{test_name}'")

    for work in works:
        question_requirements_map = {}

        # ניתוח דרישות רק לשאלות פתוחות
        for question in work.get('questions', []):
            if question.get('type') == 'open':
                requirements = question_analysis.extract_requirements(question.get('question', ''))
                question['requirements'] = [req.to_dict() for req in requirements]
                question_requirements_map[question['question_id']] = requirements
            else:
                question['requirements'] = []  # לוודא ששאר השאלות לא יקבלו דרישות בטעות

        # ניתוח תשובת מורה רק עבור שאלות פתוחות
        for answer_model in work.get('answer_models', []):
            qid = answer_model.get('question_id')
            question_type = next(
                (q.get('type') for q in work.get('questions', []) if q.get('question_id') == qid),
                None
            )

            if question_type == 'open':
                requirements = question_requirements_map.get(qid, [])
                answer_units = ans_techaer_processing.analyze_teacher_answer(
                    answer_model.get('answer', ''), requirements
                )
                answer_model['answer_units'] = [unit.to_dict() for unit in answer_units]
            else:
                answer_model['answer_units'] = answer_units

        print(f"Processed requirements for {len(work.get('questions', []))} questions in test '{test_name}'")

    new_test = {
        'test_id': str(uuid.uuid4()),
        'teacher_id': teacher_id,
        'test_name': test_name,
        'start_time': data.get('start_time', ''),
        'duration_minutes': data.get('duration_minutes', ''),
        'class_ids': data.get('class_ids', []),
        'works': works
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(new_test, f, ensure_ascii=False, indent=2)

    return jsonify({
        'message': 'New test created',
        'test_id': new_test['test_id'],
        'test': new_test
    }), 200


@app.route('/api/tests/available', methods=['GET'])
def get_available_tests():
    student_class = request.args.get('class')
    logging.debug(f"Received request for available tests for class: {student_class}")
    if not student_class:
        logging.warning("Missing 'class' parameter in request")
        return jsonify({'error': 'Missing class parameter'}), 400

    now = datetime.now()
    available_tests = []

    tests = load_all_tests()
    logging.debug(f"Loaded {len(tests)} tests from storage")

    for test in tests:
        if student_class not in test.get('class_ids', []):
            logging.debug(f"Skipping test {test.get('test_name')} - class {student_class} not in {test.get('class_ids')}")
            continue

        start_time_str = test.get('start_time')
        duration = test.get('duration_minutes')

        if not start_time_str or not duration:
            logging.warning(f"Test {test.get('test_name')} missing start_time or duration")
            continue

        try:
            start_time = parse(start_time_str)
            end_time = start_time + timedelta(minutes=int(duration))
        except Exception as e:
            logging.error(f"Error parsing date for test {test.get('test_name')}: {start_time_str}, error: {e}")
            continue

        if start_time <= now <= end_time:
            logging.debug(f"Test {test.get('test_name')} is currently available")
            available_tests.append(test)

    logging.debug(f"Returning {len(available_tests)} available tests")
    return jsonify(available_tests)

@app.route('/api/submit-answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    test_name = data.get('test_name')
    student_id = data.get('student_id')

    if not test_name or not student_id or 'answers' not in data:
        return jsonify({'error': 'Missing test_id, student_id, or answers'}), 400

    test_file = os.path.join(TESTS_DIR, f'{test_name}.json')

    if not os.path.exists(test_file):
        return jsonify({'error': 'Test file not found'}), 404

    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    if 'students' not in test_data:
        test_data['students'] = []

    # לא להסיר הגשות קודמות - רק להוסיף
    test_data['students'].append({
        'student_id': student_id,
        'exam': test_data.get('test_name', ''),
        'answers': data['answers'],
        'submitted_at': datetime.now().isoformat()
    })

    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    return jsonify({'message': 'Answers saved into test file successfully'})

import traceback

@app.route('/get_student_tests', methods=['POST'])
def get_student_tests():
    try:
        student_id = request.json.get('student_id')
        submissions = []

        for filename in os.listdir(TESTS_DIR):
            filepath = os.path.join(TESTS_DIR, filename)
            if filename.endswith('.json'):
                try:
                    if os.path.getsize(filepath) == 0:
                        continue
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"שגיאה בטעינת קובץ {filename}: {e}")
                    continue

                students_list = data.get('students')
                if not students_list:
                    continue

                # אסוף את כל השאלות מכל ה-works
                all_questions = []
                for work in data.get('works', []):
                    all_questions.extend(work.get('questions', []))

                for student in students_list:
                    if student.get('student_id') == student_id:
                        if 'final_score' not in student or student['final_score'] is None:
                            continue

                        submission = {
                            'test_id': data.get('test_id', os.path.splitext(filename)[0]),
                            'test_name': data.get('test_name', ''),
                            'final_score': student.get('final_score'),
                            'general_feedback': student.get('general_feedback', ''),
                            'answers': [],
                        }

                        for answer in student.get('answers', []):
                            question_id = answer.get('question_id')
                            teacher_question = ''
                            teacher_answer = ''
                            max_score = 100

                            for q in all_questions:
                                if q.get('question_id') == question_id:
                                    teacher_question = q.get('question', '')  # שים לב לשם השדה
                                    model_answer_list = q.get('model_answer')
                                    if model_answer_list and isinstance(model_answer_list, list):
                                        if isinstance(model_answer_list[0], dict):
                                            teacher_answer = '\n'.join(
                                                item.get('text', '') for item in model_answer_list
                                            )
                                        else:
                                            teacher_answer = '\n'.join(str(item) for item in model_answer_list)
                                    max_score = q.get('weight', 100)
                                    break  # יצאנו כי מצאנו את השאלה המתאימה

                            submission['answers'].append({
                                'question_id': question_id,
                                'teacher_question': teacher_question,
                                'teacher_answer': teacher_answer,
                                'answer': answer.get('answer'),
                                'score': answer.get('score'),
                                'max_score': max_score,
                                'remark': answer.get('remark', []),
                            })

                        submissions.append(submission)

        return jsonify({'student_tests': submissions})

    except Exception as e:
        print("Error in /get_student_tests:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get_teacher_tests', methods=['POST'])
def get_teacher_tests():
    try:
        teacher_id = request.json.get('teacher_id')
        submissions = []

        for filename in os.listdir(TESTS_DIR):
            filepath = os.path.join(TESTS_DIR, filename)
            if filename.endswith('.json'):
                try:
                    if os.path.getsize(filepath) == 0:
                        continue
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"שגיאה בטעינת קובץ {filename}: {e}")
                    continue

                # ✨ הוספה חשובה: בדוק אם המבחן שייך למורה הזה
                if str(data.get('teacher_id')) != str(teacher_id):
                    continue

                students_list = data.get('students')
                if not students_list:
                    continue

                # אסוף את כל השאלות מכל ה-works
                all_questions = []
                for work in data.get('works', []):
                    all_questions.extend(work.get('questions', []))

                for student in students_list:
                    if 'final_score' not in student or student['final_score'] is None:
                        continue

                    submission = {
                        'test_id': data.get('test_id', os.path.splitext(filename)[0]),
                        'test_name': data.get('test_name', ''),
                        'final_score': student.get('final_score'),
                        'general_feedback': student.get('general_feedback', ''),
                        'answers': [],
                    }

                    for answer in student.get('answers', []):
                        question_id = answer.get('question_id')
                        teacher_question = ''
                        teacher_answer = ''
                        max_score = 100

                        for q in all_questions:
                            if q.get('question_id') == question_id:
                                teacher_question = q.get('question', '')
                                model_answer_list = q.get('model_answer')
                                if model_answer_list and isinstance(model_answer_list, list):
                                    if isinstance(model_answer_list[0], dict):
                                        teacher_answer = '\n'.join(
                                            item.get('text', '') for item in model_answer_list
                                        )
                                    else:
                                        teacher_answer = '\n'.join(str(item) for item in model_answer_list)
                                max_score = q.get('weight', 100)
                                break

                        submission['answers'].append({
                            'question_id': question_id,
                            'teacher_question': teacher_question,
                            'teacher_answer': teacher_answer,
                            'answer': answer.get('answer'),
                            'score': answer.get('score'),
                            'max_score': max_score,
                            'remark': answer.get('remark', []),
                        })

                    submissions.append(submission)

        return jsonify({'teacher_tests': submissions})

    except Exception as e:
        print("Error in /get_teacher_tests:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
