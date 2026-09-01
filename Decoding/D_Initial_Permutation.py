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
        
if __name__ == "__main__":
    try:
        p, g, S = InitialPermutation_load_initial_permutation_key()
        data = np.load(DATA_FILE)
        cipher_blocks = list(data["cipher"])
        pad_len = int(data["pad_len"])
        restored_text = decrypt_text(cipher_blocks, pad_len, p, g, S)
        print("\n[+] Kết quả giải mã thành công:\n")
        print(restored_text)
        output_file = os.path.join(CONTENT_DIR, "D_Initial_Permutation.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(restored_text)
        print(f"\n[+] Đã lưu văn bản giải mã tại: {output_file}")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{DATA_FILE}'. Vui lòng chạy file mã hóa trước!")