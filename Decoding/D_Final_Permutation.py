import os
import sys
import math
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys

def compute_parameters(P: int):
    max_g = 15 + 225 * P
    B = max_g + 1
    k = math.ceil(4 * math.log2(B))
    return B, k

def solve_x(d: int, P: int) -> int:
    delta = 1 + 4 * P * d
    sqrt_delta = math.isqrt(delta)
    x = (-1 + sqrt_delta) // (2 * P)
    return int(x)

def decode_block(y: int, P: int, B: int) -> tuple:
    d4 = y // (B ** 3)
    r3 = y - d4 * (B ** 3)
    d3 = r3 // (B ** 2)
    r2 = r3 - d3 * (B ** 2)
    d2 = r2 // B
    r1 = r2 - d2 * B
    d1 = r1
    x4 = solve_x(d4, P)
    x3 = solve_x(d3, P)
    x2 = solve_x(d2, P)
    x1 = solve_x(d1, P)
    return x1, x2, x3, x4

def decrypt_binary_to_matrices(binary_text: str, num_matrices: int, P: int = None) -> list:
    if P is None:
        keys = load_keys()
        P = int(keys.get("P", keys.get("p", 1)))
    B, k = compute_parameters(P)
    y_values = []
    for i in range(0, len(binary_text), k):
        bin_chunk = binary_text[i:i+k]
        if len(bin_chunk) == k:
            y_values.append(int(bin_chunk, 2))
    recovered_nibbles = []
    for y in y_values:
        x1, x2, x3, x4 = decode_block(y, P, B)
        recovered_nibbles.extend([x1, x2, x3, x4])
    total_required_nibbles = num_matrices * 9 * 4
    recovered_nibbles = recovered_nibbles[:total_required_nibbles]
    recovered_values = []
    for i in range(0, len(recovered_nibbles), 4):
        n1, n2, n3, n4 = recovered_nibbles[i:i+4]
        val = (n1 << 12) | (n2 << 8) | (n3 << 4) | n4
        recovered_values.append(val)
    recovered_matrices = []
    for n in range(num_matrices):
        start_idx = n * 9
        end_idx = start_idx + 9
        mat_flat = recovered_values[start_idx:end_idx]
        mat = np.array(mat_flat, dtype=np.int64).reshape((3, 3))
        recovered_matrices.append(mat)
    return recovered_matrices
