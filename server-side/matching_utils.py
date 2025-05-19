import heapq

def greedy_maximum_matching(similarity_matrix):
    num_teacher_units = len(similarity_matrix)
    num_student_units = len(similarity_matrix[0])

    used_teacher = [False] * num_teacher_units
    used_student = [False] * num_student_units

    edges = []
    for i in range(num_teacher_units):
        for j in range(num_student_units):
            if similarity_matrix[i][j] > 0:
                edges.append((-similarity_matrix[i][j], i, j))

    heapq.heapify(edges)

    total_similarity = 0
    matched_pairs = []

    while edges:
        neg_similarity, i, j = heapq.heappop(edges)
        similarity = -neg_similarity

        if not used_teacher[i] and not used_student[j]:
            used_teacher[i] = True
            used_student[j] = True
            matched_pairs.append((i, j, similarity))
            total_similarity += similarity

    return matched_pairs, total_similarity
