import os
import sys
import json
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Create_Lookup_Table.D_MBox import decrypt_from_npz
from Create_Lookup_Table.E_MBox import build_mbox_lut
from Key_Management.key_manager import InitialPermutation_load_initial_permutation_key

CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")

AES_INV_SBOX = [
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D
]

LOG_TABLE = [0] * 256
EXP_TABLE = [0] * 256

def init_gf_tables():
    x = 1
    for i in range(255):
        EXP_TABLE[i] = x
        LOG_TABLE[x] = i
        x <<= 1
        if x & 0x100:
            x ^= 0x11B
    EXP_TABLE[255] = EXP_TABLE[0]

init_gf_tables()

def inv_exp_table_transform(val_int):
    return LOG_TABLE[val_int & 0xFF]

def inv_log_table_transform(val_int):
    return EXP_TABLE[val_int % 255]

def inv_row_interchange(matrix_3x3):
    res = np.zeros_like(matrix_3x3)
    for m in range(3):
        res[m] = matrix_3x3[(m + 2) % 3]
    return res

def inv_sbox_transform(val_int):
    return AES_INV_SBOX[val_int & 0xFF]

def phase_decrypt(input_filename="encrypted_phase_data.npz", mbox_filename="encrypted_data_restored.npz"):
    in_path = os.path.join(CONTENT_DIR, input_filename)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Không tìm thấy file: {in_path}")
        
    data = np.load(in_path, allow_pickle=True)
    cipher_hex = data['cipher_hex']
    pad_len = int(data['pad_len'][0])
    K_16 = int(data['K_16'][0])

    p, g, S = InitialPermutation_load_initial_permutation_key()
    keys_flat = S.flatten().tolist()
    keys_expanded = [((k + idx * 7) % 255) + 1 for idx, k in enumerate(keys_flat * 4)]

    print("\n[+] BẮT ĐẦU GIẢI MÃ PHA II...")
    decrypted_blocks = []
    
    for block_idx in range(0, len(cipher_hex), 9):
        hex_block = cipher_hex[block_idx:block_idx+9]
        block = np.array([int(h, 16) for h in hex_block]).reshape(3, 3)
        
        for j in range(3, 0, -1):
            K_j = keys_expanded[j]
            A10 = np.vectorize(inv_sbox_transform)(block)
            A9 = inv_row_interchange(A10)
            block = (A9 ^ K_j) & 0xFF
            
        decrypted_blocks.extend(block.flatten().tolist())

    if pad_len > 0:
        decrypted_blocks = decrypted_blocks[:-pad_len]

    print("[+] BẮT ĐẦU GIẢI MÃ PHA I...")
    fwd_lut = build_mbox_lut(K_16 & 0xFF)
    
    current_data = decrypted_blocks
    
    for k in range(15, -1, -1):
        idx_odd = 2 * k + 3
        K_odd = keys_expanded[idx_odd % len(keys_expanded)]
        
        A5 = []
        for val in current_data:
            a6_val = inv_exp_table_transform(val)
            a5_val = (a6_val ^ K_odd) & 0xFF
            A5.append(a5_val)
            
        idx_even = 2 * k + 2
        K_even = keys_expanded[idx_even % len(keys_expanded)]
        
        A3_list = []
        for val in A5:
            a3_val = (inv_log_table_transform(val) ^ K_even) & 0xFF
            A3_list.append(a3_val)
            
        current_data = A3_list

    restored_cipher_hex = [f"{v & 0xFF:02X}" for v in current_data]

    temp_mbox_path = os.path.join(CONTENT_DIR, mbox_filename)
    
    base_name = os.path.splitext(os.path.basename(mbox_filename))[0]
    restored_json_path = os.path.join(CONTENT_DIR, f"{base_name}_MBox_LUT.json")
    with open(restored_json_path, "w", encoding="utf-8") as f:
        json.dump(fwd_lut, f, indent=4)

    np.savez_compressed(
        temp_mbox_path,
        ciphertext=np.array(restored_cipher_hex, dtype=object),
        K_16=np.array([K_16]),
        lut_json=np.array([json.dumps(fwd_lut)])
    )

    # Giải mã ra văn bản gốc
    recovered_text, _, _ = decrypt_from_npz(mbox_filename)
    # Lấy lại văn bản gốc ban đầu từ encrypted_data.npz
    original_text_path = os.path.join(CONTENT_DIR, "encrypted_data.npz")
    original_text = "Không xác định"
    
    if os.path.exists(original_text_path):
        orig_data = np.load(original_text_path, allow_pickle=True)
        if 'plaintext' in orig_data:
            original_text = str(orig_data['plaintext'][0])

    is_match = (original_text == recovered_text)
    
    print("\n" + "=" * 65)
    print(" BẢNG KIỂM TRA ĐỐI CHIẾU KẾT QUẢ MÃ HÓA & GIẢI MÃ")
    print("=" * 65)
    print(f" [+] Văn bản trước mã hóa : '{original_text}'")
    print(f" [+] Văn bản sau giải mã  : '{recovered_text}'")
    print(f" [+] Trạng thái trùng khớp : {'KHỚP 100% (Thành công)' if is_match else 'KHÔNG KHỚP (Lỗi)'}")
    print("=" * 65)

    return recovered_text

if __name__ == "__main__":
    phase_decrypt()