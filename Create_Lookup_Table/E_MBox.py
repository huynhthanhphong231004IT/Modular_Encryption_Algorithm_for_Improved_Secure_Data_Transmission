import json
import os
import sys
import numpy as np
import sympy as sp

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
    print(f"[+] [E_MBox] Đang sinh LUT với Khóa K_ij = {hex(key_K_ij)}...")
    
    for val in range(0x10000): 
        hex_in = f"{val:04X}"
        A1 = (val >> 8) & 0xFF
        B1 = val & 0xFF
        A2 = gf_mul(A1, key_K_ij)
        B2 = gf_mul(B1, key_K_ij)
        A3 = ((A2 << 1) ^ G_POLY) & 0xFF if (A2 & 0x80) else A2
        B3 = ((B2 << 1) ^ G_POLY) & 0xFF if (B2 & 0x80) else B2 
        if A3 != 0 and B3 != 0:
            p_mask = gf_mul_gf2(A3, B3)  
            remainder = poly_div_mod_gf2(p_mask, G_POLY)
        else:
            remainder = 0
            
        mbox_lut[hex_in] = f"{remainder:02X}"
        
    return mbox_lut

def encrypt_from_npz(filename="encrypted_data.npz"):
    content_dir = os.path.join(PROJECT_ROOT, "Content")
    npz_path = os.path.join(content_dir, filename)
    
    base_name = os.path.splitext(os.path.basename(filename))[0]
    json_path = os.path.join(content_dir, f"{base_name}_MBox_LUT.json")
    
    if not os.path.exists(npz_path):
        os.makedirs(content_dir, exist_ok=True)
        default_text = "HELLO HUYNH THANH PHONG (Reo Rioll)"
        np.savez(npz_path, plaintext=np.array([default_text]))
        print(f"[!] File chưa tồn tại. Đã tự tạo file mẫu với văn bản: '{default_text}'")
        
    input_data = np.load(npz_path, allow_pickle=True)
    if 'plaintext' in input_data:
        plaintext = str(input_data['plaintext'][0])
    else:
        first_key = input_data.files[0]
        plaintext = str(input_data[first_key][0])
        
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
    print(f"[+] Đã xuất file JSON bảng M-Box riêng biệt: {json_path}")
    
    lut_json_str = json.dumps(fwd_lut)
    np.savez_compressed(
        npz_path,
        plaintext=np.array([plaintext]),
        ciphertext=np.array(cipher_list, dtype=object),
        K_ij=np.array([K_ij]),
        K_16=np.array([K_16]),
        lut_json=np.array([lut_json_str])
        
    )
    print(f"[SUCCESS] [E_MBox] Đã mã hóa xong và lưu kết quả vào: {npz_path}")
    return plaintext, cipher_list, K_16

# if __name__ == "__main__":
#     target_filename = "encrypted_data.npz"
#     plaintext, ciphertext, K_16 = encrypt_from_npz(target_filename)