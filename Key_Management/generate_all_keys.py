import numpy as np
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Create_key.Create_key_DES import generate_DES_key_64bit
from Create_key.Create_key_FinalPermutation import generate_P_B
from Create_key.Create_key_InitialPermutation import generate_system_keys
from Create_key.Create_key_MEA import MEA_generate_35_random_numbers, MEA_create_matrices_from_n

CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
ALL_KEYS_FILE = os.path.join(CONTENT_DIR, "all_keys.npz")

def generate_and_save_all_keys():
    os.makedirs(CONTENT_DIR, exist_ok=True)
    print("[+] Đang tiến hành sinh hệ thống khóa...")
    des_bytes, des_int, des_bits = generate_DES_key_64bit()
    P, B = generate_P_B()
    p, g, S = generate_system_keys()
    mea_n_params = MEA_generate_35_random_numbers()
    mea_matrices = MEA_create_matrices_from_n(mea_n_params)
    np.savez(
        ALL_KEYS_FILE,
        des_bytes=np.frombuffer(des_bytes, dtype=np.uint8),
        des_int=des_int,
        des_bits=des_bits,
        P=P,
        B=B,
        p=p,
        g=g,
        S=S,
        mea_n_params=np.array(mea_n_params),
        mea_matrices=np.array(mea_matrices)
    )
    
    print(f"[SUCCESS] Đã khởi tạo và lưu thành công toàn bộ khóa vào:\n -> {ALL_KEYS_FILE}")

generate_and_save_all_keys()