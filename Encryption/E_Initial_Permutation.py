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

def encrypt_text(plaintext: str, p: int, g: int, S: np.ndarray):
    S_inv = matrix_mod_inv(S, p)
    raw_bytes = plaintext.encode('utf-8')
    pad_len = (9 - len(raw_bytes) % 9) % 9
    padded_bytes = raw_bytes + b'\x00' * pad_len
    cipher_blocks = []
    for i in range(0, len(padded_bytes), 9):
        block = padded_bytes[i:i+9]
        X = np.array(list(block), dtype=int).reshape((3, 3))
        M = np.zeros((3, 3), dtype=int)
        for r in range(3):
            for c in range(3):
                M[r, c] = pow(int(g), int(X[r, c]), int(p))
        SM = np.matmul(S, M) % p
        Y = np.matmul(SM, S_inv) % p
        cipher_blocks.append(Y)
    return cipher_blocks, pad_len

def encrypt_text_to_matrices(plaintext: str) -> tuple:
    p, g, S = InitialPermutation_load_initial_permutation_key()
    cipher_blocks, pad_len = encrypt_text(plaintext, p, g, S)
    return cipher_blocks, pad_len

if __name__ == "__main__":
    p, g, S = InitialPermutation_load_initial_permutation_key()
    
    input_doc_file = os.path.join(PROJECT_ROOT, "Content", "sample_doc.txt")
    with open(input_doc_file, "r", encoding="utf-8") as f:
        text = f.read()
    print("Văn bản gốc từ file:\n", text)
    cipher, pad_len = encrypt_text(text, p, g, S)
    os.makedirs(CONTENT_DIR, exist_ok=True)
    np.savez(DATA_FILE, cipher=np.array(cipher), pad_len=pad_len)
    txt_file = os.path.join(CONTENT_DIR, "E_Initial_Permutation.txt")
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(f"Padding Length: {pad_len}\nTotal Blocks: {len(cipher)}\n\n")
        for idx, block in enumerate(cipher):
            f.write(f"--- Block {idx + 1} ---\n")
            np.savetxt(f, block, fmt="%d")
            f.write("\n")
    
    print(f"\n[+] Đã mã hóa thành công {len(cipher)} khối.")
    print(f"-> File mã hóa lưu tại: {DATA_FILE}")