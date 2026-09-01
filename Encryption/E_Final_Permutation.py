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

def g_func(x: int, P: int) -> int:
    return x + P * (x ** 2)

def encode_block(x1: int, x2: int, x3: int, x4: int, P: int, B: int) -> int:
    g1 = g_func(x1, P)
    g2 = g_func(x2, P)
    g3 = g_func(x3, P)
    g4 = g_func(x4, P)
    return g1 + B * g2 + (B ** 2) * g3 + (B ** 3) * g4
def encrypt_matrices_to_binary(matrices: list, P: int = None) -> tuple:
    if P is None:
        keys = load_keys()
        P = int(keys.get("P", keys.get("p", 1)))

    hex_nibbles = []
    for mat in matrices:
        flat = mat.flatten()
        for val in flat:
            val = int(val)
            n1 = (val >> 12) & 0x0F
            n2 = (val >> 8) & 0x0F
            n3 = (val >> 4) & 0x0F
            n4 = val & 0x0F
            hex_nibbles.extend([n1, n2, n3, n4])
    while len(hex_nibbles) % 4 != 0:
        hex_nibbles.append(0)
    B, k = compute_parameters(P)
    binary_blocks = []
    y_values = []
    for i in range(0, len(hex_nibbles), 4):
        x1, x2, x3, x4 = hex_nibbles[i:i+4]
        y = encode_block(x1, x2, x3, x4, P, B)
        y_values.append(y)
        
        bin_str = format(y, f'0{k}b')
        binary_blocks.append(bin_str)
    final_binary_text = "".join(binary_blocks)
    return final_binary_text, y_values, B, k
