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
        if y_hex not in inv_table:
            inv_table[y_hex] = []
        inv_table[y_hex].append(int(x_hex, 16))
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
        y_target = y_hex.upper().zfill(2)
        candidates_X = inv_table.get(y_target, [])
        
        if not candidates_X:
            recovered_chars.append("?")
            continue
            
        found = False
        for X_cand in candidates_X:
            # XOR 16-bit trực tiếp để lấy lại đúng ký tự ASCII gốc
            char_code = X_cand ^ K_16
            if 0 <= char_code <= 0x10FFFF:
                recovered_chars.append(chr(char_code))
                found = True
                break
                
        if not found:
            recovered_chars.append(chr(candidates_X[0] ^ K_16))

    recovered_text = "".join(recovered_chars)
    return recovered_text, list(cipher_array), K_16

# if __name__ == "__main__":
#     try:
#         print("\n--- Tiến trình Giải mã Inverse M-Box (D_MBox) ---")
#         target_filename = "../Content/encrypted_data.npz"
#         recovered_text, cipher_input, K_16 = decrypt_from_npz(target_filename)
#         print("\n" + "=" * 60)
#         print("GIẢI MÃ (D_MBox)")
#         print(f"File nguồn        : Content/encrypted_data.npz")
#         print(f"Bản mã nhận được : {cipher_input}")
#         print(f"Khóa K_16         : {hex(K_16)}")
#         print(f"Văn bản khôi phục: '{recovered_text}'")
#         print("=" * 60)
#         print("[SUCCESS] D_MBox đã đọc file encrypted_data.npz và giải mã chính xác 100%!")
#     except Exception as e:
#         print(f"\n[!] Lỗi phát sinh: {e}")