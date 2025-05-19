import numpy as np
from sentence_transformers import SentenceTransformer
import units_classification
import roberta_similarity
from scipy.optimize import linear_sum_assignment
from matching_utils import greedy_maximum_matching  # ← ייבוא הפונקציה
import heapq

model = SentenceTransformer('all-MiniLM-L6-v2')

def calculating_score(teacher_answer_units, student_answer_units, Question_requirements, categories):
    print(Question_requirements)
    # סיווג היחידות לקטגוריות
    teacher_answer_units, teacher_categories_counter = units_classification.match_units_to_categories(teacher_answer_units, categories, model)
    student_answer_units, student_categories_counter = units_classification.match_units_to_categories(student_answer_units, categories, model)
    # מילוי מטריצת דמיון באפסים
    similarity_matrix = [[0 for _ in range(len(student_answer_units))] for _ in range(len(teacher_answer_units))]
    # מילוי מטריצת דמיון על פי דמיון קוסינוס בין היחידות
    for i in range(len(teacher_answer_units)):
        teacher_text, teacher_cat_idx = teacher_answer_units[i]
        for j in range(len(student_answer_units)):
            student_text, student_cat_idx = student_answer_units[j]
            if teacher_cat_idx == student_cat_idx:
                similarity = roberta_similarity.cal_similarity(teacher_text, student_text)
                print(f"Similarity raw output: {similarity}")

                if similarity > 0.4:
                    similarity_matrix[i][j] = similarity
    # optimal_matches = greedy_maximum_matching(similarity_matrix)
    print(teacher_answer_units)


# פונקציה לבחירת היחידות המתאימות ביותר ע"פ האלגוריתם הגרידי
def greedy_maximum_matching(similarity_matrix, teacher_answer_units, student_answer_units, categories):
    optimal_matches = [cat_match_units() for _ in range(len(categories))]
    max_heap = []
    visited_rows = [0 for _ in range(len(similarity_matrix))]
    visited_cols = [0 for _ in range(len(similarity_matrix[1]))]
    # בניית ערימת מקסימום
    for i in range(len(similarity_matrix)):
            for j in range(len(similarity_matrix[i])):
                if similarity_matrix[i][j] > 0:
                    heapq.heappush(max_heap, (similarity_matrix[i][j], i, j))
    # בחירת היחידות המתאימות ביותר והוספתן לרשימה
    while max_heap:
        score, i, j = heapq.heappop(max_heap)
        if visited_rows[i]==visited_cols[j]==0 and score > 0:
            student_text, student_cat_idx = student_answer_units[j]
            optimal_matches[student_cat_idx].add_score(score, i, j, student_text)
            visited_rows[i] = visited_cols[j] = 1
    return optimal_matches



# הדפסת מטריצת הדמיון
def print_matrix(matrix):
    print("\n--- Similarity Matrix ---")
    for row in matrix:
        print(["{:.3f}".format(v) for v in row])

# רשימת בחירה של היחידות המתאימות ביותר
class cat_match_units:
    def __init__(self):
        self.sum = 0
        self.text = ""
        self.scores = []
    def add_score(self, score, i, j, text):
        self.scores.append((score, i, j, text))
        self.sum += 1
    