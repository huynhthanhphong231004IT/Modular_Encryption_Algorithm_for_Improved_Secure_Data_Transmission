import numpy as np
import sympy as sp
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import InitialPermutation_load_initial_permutation_key

CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
DATA_FILE = os.path.join(CONTENT_DIR, "encrypted_data.npz")

def matrix_mod_inv(S, p):
    S_sympy = sp.Matrix(S)
    return np.array(S_sympy.inv_mod(p), dtype=int)

def encrypt_text(plaintext: str, p: int, g: int, S: np.ndarray):
    S_inv = matrix_mod_inv(S, p)
    pad_len = (9 - len(plaintext) % 9) % 9
    padded_text = plaintext + (' ' * pad_len)
    cipher_blocks = []
    
    for i in range(0, len(padded_text), 9):
        block = padded_text[i:i+9]
        X = np.array([[ord(c) for c in block[j:j+3]] for j in range(0, 9, 3)], dtype=int)
        M = np.zeros((3, 3), dtype=int)
        for r in range(3):
            for c in range(3):
                M[r, c] = pow(g, int(X[r, c]), p)
        SM = np.matmul(S, M) % p
        Y = np.matmul(SM, S_inv) % p
        cipher_blocks.append(Y)
        
    return cipher_blocks, pad_len

if __name__ == "__main__":
    p, g, S = InitialPermutation_load_initial_permutation_key()
    
    text = "Hello World! MEA Encryption Test."
    print("Văn bản gốc:", text)

    cipher, pad_len = encrypt_text(text, p, g, S)
    
    os.makedirs(CONTENT_DIR, exist_ok=True)
    np.savez(DATA_FILE, cipher=np.array(cipher), pad_len=pad_len)
    
    print(f"\n[+] Đã mã hóa thành công {len(cipher)} khối.")
    print(f"-> File mã hóa lưu tại: {DATA_FILE}")