import json
import os
import sys
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys

G_POLY = 0x11B

def gf_mul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        check_bit = a & 0x80
        a = (a << 1) & 0xFF
        if check_bit:
            a ^= 0x1B
        b >>= 1
    return p

def poly_div_mod_gf2(dividend: int, divisor: int = G_POLY) -> int:
    deg_divisor = divisor.bit_length() - 1
    while True:
        deg_dividend = dividend.bit_length() - 1
        if deg_dividend < deg_divisor:
            break
        shift = deg_dividend - deg_divisor
        dividend ^= (divisor << shift)
    return dividend

def gf_mul_gf2(a: int, b: int) -> int:
    p = 0
    while b > 0:
        if b & 1:
            p ^= a
        a <<= 1
        b >>= 1
    return p

def build_mbox_lut(key_K_ij: int) -> dict:
    mbox_lut = {}
    print(f"[+] [E_MBox] Đang sinh LUT 16-bit với Khóa K_ij = {hex(key_K_ij)}...")
    
    for val in range(0x10000): 
        hex_in = f"{val:04X}"
        A1 = (val >> 8) & 0xFF
        B1 = val & 0xFF
        
        A2 = gf_mul(A1, key_K_ij)
        B2 = gf_mul(B1, key_K_ij)
        
        # ĐÃ SỬA: Dịch trái (A2 << 1) ở cả 2 nhánh để đảm bảo song ánh 1-1
        A3 = ((A2 << 1) ^ G_POLY) & 0xFF if (A2 & 0x80) else (A2 << 1)
        B3 = ((B2 << 1) ^ G_POLY) & 0xFF if (B2 & 0x80) else (B2 << 1)
        
        rem_A = poly_div_mod_gf2(gf_mul_gf2(A3, key_K_ij), G_POLY) if A3 != 0 else 0
        rem_B = poly_div_mod_gf2(gf_mul_gf2(B3, key_K_ij), G_POLY) if B3 != 0 else 0
        
        remainder_16bit = (rem_A << 8) | rem_B
        mbox_lut[hex_in] = f"{remainder_16bit:04X}"
        
    return mbox_lut

def encrypt_from_npz(filename="encrypted_data.npz"):
    content_dir = os.path.join(PROJECT_ROOT, "Content")
    npz_path = os.path.join(content_dir, filename)
    json_path = os.path.join(content_dir, f"{os.path.splitext(filename)[0]}_MBox_LUT.json")
    
    if not os.path.exists(npz_path):
        os.makedirs(content_dir, exist_ok=True)
        default_text = "HELLO HUYNH THANH PHONG (Reo Rioll)"
        np.savez(npz_path, plaintext=np.array([default_text]))
        
    input_data = np.load(npz_path, allow_pickle=True)
    plaintext = str(input_data['plaintext'][0]) if 'plaintext' in input_data else str(input_data[input_data.files[0]][0])
        
    keys = load_keys()
    p, g = keys["p"], keys["g"]
    mea_matrices = keys["mea_matrices"]
    i, j = p % 3, g % 3
    S = mea_matrices[0]
    K_ij = int(S[i, j]) & 0xFF
    if K_ij == 0:
        K_ij = 0x01
    K_16 = (K_ij << 8) | K_ij
    
    fwd_lut = build_mbox_lut(K_ij)
    cipher_list = []
    for char in plaintext:
        D = ord(char)
        X = D ^ K_16
        X_hex = f"{X:04X}"
        Y_hex = fwd_lut[X_hex]
        cipher_list.append(Y_hex)
        
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(fwd_lut, f, indent=4)
    
    lut_json_str = json.dumps(fwd_lut)
    np.savez_compressed(
        npz_path,
        plaintext=np.array([plaintext]),
        ciphertext=np.array(cipher_list, dtype=object),
        K_ij=np.array([K_ij]),
        K_16=np.array([K_16]),
        lut_json=np.array([lut_json_str])
    )
    print(f"[SUCCESS] Đã mã hóa xong!")
    return plaintext, cipher_list, K_16

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