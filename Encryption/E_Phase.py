import os
import sys
import numpy as np
import sympy as sp

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import (
    load_keys,
    InitialPermutation_load_initial_permutation_key
)

from Create_Lookup_Table.E_MBox import encrypt_from_npz, build_mbox_lut
from Create_Lookup_Table.Create_L_E_S import generate_log_exp_tables, get_sbox

G_POLY = 0x11B
MBOX_CACHE = {}

def poly_div_mod_gf2(dividend: int, divisor: int = G_POLY) -> int:
    deg_divisor = divisor.bit_length() - 1
    while True:
        deg_dividend = dividend.bit_length() - 1
        if deg_dividend < deg_divisor:
            break
        shift = deg_dividend - deg_divisor
        dividend ^= (divisor << shift)
    return dividend

def apply_mbox_matrix(A_matrix, k_val):
    k_val = int(k_val) & 0xFFFF
    if k_val not in MBOX_CACHE:
        MBOX_CACHE[k_val] = build_mbox_lut(k_val)
    lut_dict = MBOX_CACHE[k_val]
    return np.vectorize(lambda x: int(lut_dict.get(f"{x & 0xFFFF:04X}", "00"), 16))(A_matrix)

def encrypt_phase_1(A2, subkeys, log_table, exp_table):
    A = np.copy(A2)
    for i in range(1, 17):
        K_even = subkeys.get(2 * i + 2, np.full(A.shape, 0x55, dtype=int))
        K_odd  = subkeys.get(2 * i + 3, np.full(A.shape, 0xAA, dtype=int))
        k_even_val = int(K_even[0, 0]) if isinstance(K_even, np.ndarray) else int(K_even)
        k_odd_val  = int(K_odd[0, 0]) if isinstance(K_odd, np.ndarray) else int(K_odd)
        A3 = np.bitwise_xor(A, K_even)
        A4 = apply_mbox_matrix(A3, k_even_val) 
        A5 = np.vectorize(lambda x: log_table[x & 0xFF] if (x & 0xFF) != 0 else 0)(A4)
        A6 = np.bitwise_xor(A5, K_odd)
        A7 = apply_mbox_matrix(A6, k_odd_val)
        A8 = np.vectorize(lambda x: exp_table[x & 0xFF] if (x & 0xFF) != 0 else 0)(A7)
        A = A8
    return A8

# Phase_II
def encrypt_phase_2(A8, subkeys, sbox_table):
    A = np.copy(A8)
    num_rows = A.shape[0]
    for j in range(1, 4):
        K_j = subkeys.get(j, np.full(A.shape, 0x01 * j, dtype=int))
        A9 = np.bitwise_xor(A, K_j)
        A10 = np.empty_like(A9)
        for m in range(num_rows):
            A10[m] = A9[(m + 1) % num_rows]
        A11 = np.vectorize(lambda x: sbox_table[x & 0xFF])(A10)
        A = A11
    A12 = np.vectorize(lambda x: f"{x & 0xFF:02X}")(A11)
    return A11, A12


def encrypt_Phase_pipeline(A2, subkeys, log_table, exp_table, sbox_table):
    A8 = encrypt_phase_1(A2, subkeys, log_table, exp_table)
    A11, A12 = encrypt_phase_2(A8, subkeys, sbox_table)
    return A8, A11, A12


if __name__ == "__main__":
    content_dir = os.path.join(PROJECT_ROOT, "Content")
    data_file = os.path.join(content_dir, "encrypted_data.npz")
    if not os.path.exists(data_file):
        print(f"[!] Không tìm thấy file {data_file}.")
        sys.exit(1)
    data = np.load(data_file, allow_pickle=True)
    raw_blocks = data['ciphertext']
    def parse_to_int_array(block):
        arr = np.array(block)
        if arr.dtype.kind in ['U', 'S', 'O']: 
            flat = arr.flatten()
            converted = [int(x, 16) if isinstance(x, str) else int(x) for x in flat]
            return np.array(converted, dtype=np.int64).reshape(arr.shape)
        return arr.astype(np.int64)
    mea_cipher_blocks = [parse_to_int_array(b) for b in raw_blocks]
    pad_len = int(data['pad_len']) if 'pad_len' in data.files else 0
    try:
        keys_dict = load_keys()
        mea_matrices = keys_dict.get("mea_matrices", [])
        subkeys = {
            idx + 1: parse_to_int_array(mat) 
            for idx, mat in enumerate(mea_matrices)
        } if isinstance(mea_matrices, (list, np.ndarray)) else keys_dict.get("mea_matrices", {})
    except Exception:
        subkeys = {k: np.full((3, 3), k, dtype=np.int64) for k in range(1, 36)}
        
    log_table, exp_table = generate_log_exp_tables()
    sbox_table = get_sbox()
    phase_1_outputs, phase_2_raw, phase_2_hex = zip(*[
        encrypt_Phase_pipeline(block, subkeys, log_table, exp_table, sbox_table) 
        for block in mea_cipher_blocks
    ])
    np.savez(
        data_file,
        cipher=mea_cipher_blocks,
        pad_len=pad_len,
        phase1_cipher=np.array(phase_1_outputs, dtype=object),
        phase2_cipher=np.array(phase_2_raw, dtype=object),
        phase2_hex=np.array(phase_2_hex, dtype=object)
    )
    
    print("\n" + "=" * 60)
    print("MÃ HÓA HOÀN TẤT (E_Phase.py)")
    print(f"Tổng số khối đã xử lý : {len(mea_cipher_blocks)}")
    print(f"Khối 1 HEX [A(12)]    :\n{phase_2_hex[0]}")
    print("=" * 60)