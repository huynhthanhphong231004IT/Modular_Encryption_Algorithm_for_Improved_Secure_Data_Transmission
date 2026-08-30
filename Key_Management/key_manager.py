import numpy as np
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
ALL_KEYS_FILE = os.path.join(CONTENT_DIR, "all_keys.npz")

def load_keys():
    if not os.path.exists(ALL_KEYS_FILE):
        raise FileNotFoundError(
            f"\n[ERROR] Không tìm thấy file khóa tại: '{ALL_KEYS_FILE}'!\n"
            f"Vui lòng chạy file 'Key_Management/generate_all_keys.py' trước để khởi tạo hệ thống khóa."
        )
    data = np.load(ALL_KEYS_FILE)
    keys_dict = {

        # A DES key
        "des_bytes": bytes(data["des_bytes"]),
        "des_int": int(data["des_int"]),
        "des_bits": str(data["des_bits"]),

        # Final Permutation keys
        "P": int(data["P"]),
        "B": int(data["B"]),

        # Initial Permutation keys
        "p": int(data["p"]),
        "g": int(data["g"]),
        "S": data["S"],

        # MEA keys
        "mea_n_params": data["mea_n_params"].tolist(),
        "mea_matrices": data["mea_matrices"]
    }
    
    return keys_dict

def InitialPermutation_load_initial_permutation_key():
    keys = load_keys()
    return keys["p"], keys["g"], keys["S"]

def TrinomialMatrix_load_initial_permutation_key():
    keys = load_keys()
    return keys["mea_matrices"]