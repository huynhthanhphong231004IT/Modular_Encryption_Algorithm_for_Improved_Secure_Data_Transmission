import os
import sys
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys
from Create_Lookup_Table.E_MBox import build_mbox_lut
from Create_Lookup_Table.Create_L_E_S import generate_log_exp_tables, get_sbox

MBOX_CACHE = {}

def get_mbox_lut(k_val):
    k_val = int(k_val) & 0xFFFF
    if k_val not in MBOX_CACHE:
        MBOX_CACHE[k_val] = build_mbox_lut(k_val)
    return MBOX_CACHE[k_val]

def apply_mbox_elementwise(A_matrix, K_matrix):
    result = np.zeros_like(A_matrix, dtype=np.int64)
    rows, cols = A_matrix.shape
    for r in range(rows):
        for c in range(cols):
            x_int = int(A_matrix[r, c]) & 0xFFFF
            k_val = int(K_matrix[r, c]) if isinstance(K_matrix, np.ndarray) else int(K_matrix)
            lut = get_mbox_lut(k_val)
            x_hex = f"{x_int:04X}"
            y_hex = lut.get(x_hex, "0000")
            result[r, c] = int(y_hex, 16)
    return result

def gf_log_16bit(x, log_table):
    val = int(x) & 0xFFFF
    hi = (val >> 8) & 0xFF
    lo = val & 0xFF
    new_hi = 0 if hi == 0 else int(log_table[hi]) & 0xFF
    new_lo = 0 if lo == 0 else int(log_table[lo]) & 0xFF
    return (new_hi << 8) | new_lo

def gf_exp_16bit(x, exp_table):
    val = int(x) & 0xFFFF
    hi = (val >> 8) & 0xFF
    lo = val & 0xFF
    new_hi = 0 if hi == 0 else int(exp_table[hi]) & 0xFF
    new_lo = 0 if lo == 0 else int(exp_table[lo]) & 0xFF
    return (new_hi << 8) | new_lo

def parse_to_int_array(block):
    arr = np.array(block)
    if arr.dtype.kind in ['U', 'S', 'O']: 
        flat = arr.flatten()
        converted = [int(x, 16) if isinstance(x, str) else int(x) for x in flat]
        return np.array(converted, dtype=np.int64).reshape(arr.shape)
    return arr.astype(np.int64)

def encrypt_phase_1(A2, subkeys, log_table, exp_table):
    A = np.copy(A2)
    for i in range(1, 17):
        K_even = subkeys.get(2 * i + 2, np.full(A.shape, 0x55, dtype=int))
        K_odd  = subkeys.get(2 * i + 3, np.full(A.shape, 0xAA, dtype=int))
        
        A3 = np.bitwise_xor(A, K_even)
        A4 = apply_mbox_elementwise(A3, K_even) 
        A5 = np.vectorize(lambda x: gf_log_16bit(x, log_table))(A4)
        A6 = np.bitwise_xor(A5, K_odd)
        A7 = apply_mbox_elementwise(A6, K_odd)
        A8 = np.vectorize(lambda x: gf_exp_16bit(x, exp_table))(A7)
        A = A8
    return A8

def encrypt_phase_2(A8, subkeys, sbox_table):
    A = np.copy(A8)
    num_rows = A.shape[0]
    for j in range(1, 4):
        K_j = subkeys.get(j, np.full(A.shape, 0x01 * j, dtype=int))
        A9 = np.bitwise_xor(A, K_j)
        A10 = np.empty_like(A9)
        for m in range(num_rows):
            A10[m] = A9[(m + 1) % num_rows]
        
        def sbox_16bit(x):
            val = int(x) & 0xFFFF
            hi = int(sbox_table[(val >> 8) & 0xFF]) & 0xFF
            lo = int(sbox_table[val & 0xFF]) & 0xFF
            return (hi << 8) | lo
            
        A11 = np.vectorize(sbox_16bit)(A10)
        A = A11
    A12 = np.vectorize(lambda x: f"{int(x) & 0xFFFF:04X}")(A11)
    return A11, A12

def encrypt_phase_pipeline(A2, subkeys, log_table, exp_table, sbox_table):
    """Hàm xử lý cho một block duy nhất."""
    A8 = encrypt_phase_1(A2, subkeys, log_table, exp_table)
    A11, A12 = encrypt_phase_2(A8, subkeys, sbox_table)
    return A8, A11, A12

# =========================================================================
# BỔ SUNG HÀM NÀY ĐỂ TƯƠNG THÍCH HOÀN TOÀN VỚI FILE NGUỒN (MAIN PIPELINE)
# =========================================================================
def encrypt_phase_from_matrices(init_matrices):
    """
    Hàm interface nhận vào danh sách các ma trận (từ E_Initial_Permutation)
    và thực hiện mã hóa Phase cho toàn bộ chuỗi.
    """
    try:
        keys_dict = load_keys()
        mea_matrices = keys_dict.get("mea_matrices", [])
        subkeys = {
            idx + 1: parse_to_int_array(mat) 
            for idx, mat in enumerate(mea_matrices)
        } if isinstance(mea_matrices, (list, np.ndarray)) else keys_dict.get("mea_matrices", {})
    except Exception:
        subkeys = {k: np.full((3, 3), k, dtype=np.int64) for k in range(1, 37)}

    log_table, exp_table = generate_log_exp_tables()
    sbox_table = get_sbox()

    phase2_matrices = []
    for block in init_matrices:
        block_arr = parse_to_int_array(block)
        _, A11, _ = encrypt_phase_pipeline(block_arr, subkeys, log_table, exp_table, sbox_table)
        phase2_matrices.append(A11)
        
    return phase2_matrices


if __name__ == "__main__":
    content_dir = os.path.join(PROJECT_ROOT, "Content")
    input_file = os.path.join(content_dir, "E_Initial_Permutation.npz")
    output_npz = os.path.join(content_dir, "E_Phase.npz")

    if not os.path.exists(input_file):
        print(f"[!] Không tìm thấy file đầu vào: {input_file}")
        sys.exit(1)

    data = np.load(input_file, allow_pickle=True)
    raw_blocks = data['cipher']
    pad_len = int(data['pad_len']) if 'pad_len' in data.files else 0
    mea_cipher_blocks = [parse_to_int_array(b) for b in raw_blocks]

    try:
        keys_dict = load_keys()
        mea_matrices = keys_dict.get("mea_matrices", [])
        subkeys = {
            idx + 1: parse_to_int_array(mat) 
            for idx, mat in enumerate(mea_matrices)
        } if isinstance(mea_matrices, (list, np.ndarray)) else keys_dict.get("mea_matrices", {})
    except Exception:
        subkeys = {k: np.full((3, 3), k, dtype=np.int64) for k in range(1, 37)}

    log_table, exp_table = generate_log_exp_tables()
    sbox_table = get_sbox()

    phase_1_outputs, phase_2_raw, phase_2_hex = zip(*[
        encrypt_phase_pipeline(block, subkeys, log_table, exp_table, sbox_table) 
        for block in mea_cipher_blocks
    ])

    os.makedirs(content_dir, exist_ok=True)
    np.savez(
        output_npz,
        cipher=mea_cipher_blocks,
        pad_len=pad_len,
        phase1_cipher=np.array(phase_1_outputs, dtype=object),
        phase2_cipher=np.array(phase_2_raw, dtype=object),
        phase2_hex=np.array(phase_2_hex, dtype=object)
    )

    print("\n" + "=" * 60)
    print("MÃ HÓA PHASE HOÀN TẤT (E_Phase.py)")
    print("=" * 60)