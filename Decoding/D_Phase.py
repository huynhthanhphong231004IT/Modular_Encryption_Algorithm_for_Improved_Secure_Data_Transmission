import os
import sys
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys
from Create_Lookup_Table.Create_L_E_S import generate_log_exp_tables, get_sbox
from Create_Lookup_Table.E_MBox import build_mbox_lut
from Create_Lookup_Table.D_MBox import build_inverse_table

DMBOX_CACHE = {}

def apply_dmbox_matrix(A_matrix, k_val):
    """
    Áp dụng giải mã D_MBox sử dụng chính hàm `build_inverse_table` từ D_MBox.py.
    """
    k_val = int(k_val) & 0xFFFF
    
    # 1. Tạo cache bảng đảo từ D_MBox để tránh tính toán lại nhiều lần
    if k_val not in DMBOX_CACHE:
        forward_lut = build_mbox_lut(k_val)
        DMBOX_CACHE[k_val] = build_inverse_table(forward_lut)
        
    inv_table = DMBOX_CACHE[k_val]
    
    # 2. Hàm tra cứu ngược từng giá trị byte mã hóa (y_val) ra giá trị gốc (x_val)
    def lookup_inverse(y_val):
        y_hex = f"{y_val & 0xFF:02X}"
        candidates = inv_table.get(y_hex, [])
        return candidates[0] if candidates else 0

    return np.vectorize(lookup_inverse)(A_matrix)

def get_inverse_sbox(sbox_table):
    """Tạo bảng S-Box ngược."""
    inv_sbox = np.zeros_like(sbox_table)
    for idx, val in enumerate(sbox_table):
        inv_sbox[val & 0xFF] = idx
    return inv_sbox

# --- DESHIFT & DECRYPT PHASE 2 ---
def decrypt_phase_2(A11, subkeys, inv_sbox_table):
    A = np.copy(A11)
    num_rows = A.shape[0]
    
    # Đảo ngược Phase 2: Chạy ngược từ j = 3 về 1
    for j in range(3, 0, -1):
        # Step 1: Reverse S-Box
        A10 = np.vectorize(lambda x: inv_sbox_table[x & 0xFF])(A)
        
        # Step 2: Reverse Shift Rows (Dịch hàng xuống lại vị trí ban đầu)
        A9 = np.empty_like(A10)
        for m in range(num_rows):
            A9[(m + 1) % num_rows] = A10[m]
            
        # Step 3: Reverse XOR Subkey K_j
        K_j = subkeys.get(j, np.full(A.shape, 0x01 * j, dtype=int))
        A = np.bitwise_xor(A9, K_j)
        
    return A

# --- DECRYPT PHASE 1 ---
def decrypt_phase_1(A8, subkeys, log_table, exp_table):
    A = np.copy(A8)
    
    # Đảo ngược Phase 1: Chạy ngược từ vòng 16 về 1
    for i in range(16, 0, -1):
        K_even = subkeys.get(2 * i + 2, np.full(A.shape, 0x55, dtype=int))
        K_odd  = subkeys.get(2 * i + 3, np.full(A.shape, 0xAA, dtype=int))
        
        k_even_val = int(K_even[0, 0]) if isinstance(K_even, np.ndarray) else int(K_even)
        k_odd_val  = int(K_odd[0, 0]) if isinstance(K_odd, np.ndarray) else int(K_odd)
        
        # 1. Reverse Exp -> Log
        A7 = np.vectorize(lambda x: log_table[x & 0xFF] if (x & 0xFF) != 0 else 0)(A)
        
        # 2. Reverse M-Box (D_MBox) với k_odd
        A6 = apply_dmbox_matrix(A7, k_odd_val)
        
        # 3. Reverse XOR K_odd
        A5 = np.bitwise_xor(A6, K_odd)
        
        # 4. Reverse Log -> Exp
        A4 = np.vectorize(lambda x: exp_table[x & 0xFF] if (x & 0xFF) != 0 else 0)(A5)
        
        # 5. Reverse M-Box (D_MBox) với k_even
        A3 = apply_dmbox_matrix(A4, k_even_val)
        
        # 6. Reverse XOR K_even
        A2 = np.bitwise_xor(A3, K_even)
        
        A = A2
        
    return A

def decrypt_Phase_pipeline(A11, subkeys, log_table, exp_table, inv_sbox_table):
    A8_recovered = decrypt_phase_2(A11, subkeys, inv_sbox_table)
    A2_recovered = decrypt_phase_1(A8_recovered, subkeys, log_table, exp_table)
    return A2_recovered

if __name__ == "__main__":
    content_dir = os.path.join(PROJECT_ROOT, "Content")
    data_file = os.path.join(content_dir, "encrypted_data.npz")
    
    if not os.path.exists(data_file):
        print(f"[!] Không tìm thấy file {data_file}.")
        sys.exit(1)
        
    data = np.load(data_file, allow_pickle=True)
    
    # Ưu tiên lấy bản mã Phase 2 nếu có sẵn trong NPZ, nếu không sẽ dùng ciphertext mặc định
    if 'phase2_cipher' in data.files:
        cipher_blocks = data['phase2_cipher']
    else:
        cipher_blocks = data['ciphertext']

    def parse_to_int_array(block):
        arr = np.array(block)
        if arr.dtype.kind in ['U', 'S', 'O']: 
            flat = arr.flatten()
            converted = [int(x, 16) if isinstance(x, str) else int(x) for x in flat]
            return np.array(converted, dtype=np.int64).reshape(arr.shape)
        return arr.astype(np.int64)

    mea_cipher_blocks = [parse_to_int_array(b) for b in cipher_blocks]
    
    # Nạp Subkeys
    try:
        keys_dict = load_keys()
        mea_matrices = keys_dict.get("mea_matrices", [])
        subkeys = {
            idx + 1: parse_to_int_array(mat) 
            for idx, mat in enumerate(mea_matrices)
        } if isinstance(mea_matrices, (list, np.ndarray)) else keys_dict.get("mea_matrices", {})
    except Exception:
        subkeys = {k: np.full((3, 3), k, dtype=np.int64) for k in range(1, 36)}

    # Nạp các bảng tra cứu
    log_table, exp_table = generate_log_exp_tables()
    sbox_table = get_sbox()
    inv_sbox_table = get_inverse_sbox(sbox_table)

    # Giải mã toàn bộ các khối
    decrypted_blocks = [
        decrypt_Phase_pipeline(block, subkeys, log_table, exp_table, inv_sbox_table)
        for block in mea_cipher_blocks
    ]

    print("\n" + "=" * 60)
    print("GIẢI MÃ HOÀN TẤT VỚI D_MBOX (D_Phase.py)")
    print(f"Tổng số khối đã giải mã : {len(decrypted_blocks)}")
    print(f"Ma trận gốc A2 khối 1   :\n{decrypted_blocks[0]}")
    print("=" * 60)