import json
import os
import sys
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

def build_inverse_table(forward_lut: dict) -> dict:
    inv_table = {}
    for x_hex, y_hex in forward_lut.items():
        inv_table[y_hex] = int(x_hex, 16)
    return inv_table

def decrypt_from_npz(filename="encrypted_data.npz") -> tuple:
    content_dir = os.path.join(PROJECT_ROOT, "Content")
    npz_path = os.path.join(content_dir, filename)
    
    if not os.path.exists(npz_path):
        raise FileNotFoundError(f"Không tìm thấy file: {npz_path}")
        
    data = np.load(npz_path, allow_pickle=True)
    cipher_array = data['ciphertext']
    K_16 = int(data['K_16'][0])
    lut_json_str = str(data['lut_json'][0])
    
    fwd_lut = json.loads(lut_json_str)
    inv_table = build_inverse_table(fwd_lut)
    
    recovered_chars = []
    for y_hex in cipher_array:
        y_target = y_hex.upper().zfill(4)
        if y_target in inv_table:
            X_cand = inv_table[y_target]
            char_code = X_cand ^ K_16
            recovered_chars.append(chr(char_code))
        else:
            recovered_chars.append("?")

    recovered_text = "".join(recovered_chars)
    return recovered_text, list(cipher_array), K_16
