import numpy as np
import random

def MEA_generate_35_random_numbers():
    return random.choices(range(1, 36), k=35)

def MEA_create_matrices_from_n(n_list):
    matrices = []
    for n in n_list:
        matrix = np.array([
            [8*n**2 + 28*n + 20, 2*n + 5, 4*n + 4],
            [4*n**2 + 14*n + 10,   n + 3, 2*n + 3],
            [4*n**2 + 14*n + 11,   n + 2, 2*n + 1]
        ], dtype=int)
        matrices.append(matrix)
    return matrices

n_params = MEA_generate_35_random_numbers()
S_matrices = MEA_create_matrices_from_n(n_params)
print(f"Giá trị n_1 = {n_params[0]}")
print("Ma trận S_1 tương ứng:")
print(S_matrices[0])