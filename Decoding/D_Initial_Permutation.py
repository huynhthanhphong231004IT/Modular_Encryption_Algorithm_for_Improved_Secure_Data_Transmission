import os
import sys
import numpy as np
import sympy as sp

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import InitialPermutation_load_initial_permutation_key

CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
DATA_FILE = os.path.join(CONTENT_DIR, "E_Initial_Permutation.npz")

def matrix_mod_inv(S, p):
    S_sympy = sp.Matrix(S)
    return np.array(S_sympy.inv_mod(p), dtype=int)

def discrete_log(base, val, p):
    return int(sp.discrete_log(p, val, base))

def decrypt_text(cipher_blocks: list, pad_len: int, p: int, g: int, S: np.ndarray):
    S_inv = matrix_mod_inv(S, p)
    decrypted_bytes = []
    for Y in cipher_blocks:
        S_inv_Y = np.matmul(S_inv, Y) % p
        M_prime = np.matmul(S_inv_Y, S) % p
        X = np.zeros((3, 3), dtype=int)
        for r in range(3):
            for c in range(3):
                val = int(M_prime[r, c])
                x_ij = discrete_log(g, val, p)
                X[r, c] = x_ij % (p - 1)
        for r in range(3):
            for c in range(3):
                decrypted_bytes.append(int(X[r, c]) & 0xFF)
    raw_bytes = bytes(decrypted_bytes)
    if pad_len > 0:
        raw_bytes = raw_bytes[:-pad_len]
    return raw_bytes.decode('utf-8', errors='ignore')