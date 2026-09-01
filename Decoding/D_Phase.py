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

def ensure_subkeys_dict(subkeys):
    if isinstance(subkeys, dict):
        return subkeys
    if isinstance(subkeys, (list, tuple, np.ndarray)):
        arr = np.array(subkeys, dtype=object)
        if arr.ndim == 2:
            return {i: arr for i in range(1, 37)}
        return {idx + 1: mat for idx, mat in enumerate(arr)}
    return {}

def get_dmbox_lut(k_val):
    k_val = int(k_val) & 0xFFFF
    if k_val not in DMBOX_CACHE:
        forward_lut = build_mbox_lut(k_val)
        DMBOX_CACHE[k_val] = build_inverse_table(forward_lut)
    return DMBOX_CACHE[k_val]

def apply_dmbox_elementwise(A_matrix, K_matrix):
    result = np.zeros_like(A_matrix, dtype=np.int64)
    rows, cols = A_matrix.shape
    for r in range(rows):
        for c in range(cols):
            y_int = int(A_matrix[r, c]) & 0xFFFF
            k_val = int(K_matrix[r, c]) if isinstance(K_matrix, np.ndarray) else int(K_matrix)
            inv_lut = get_dmbox_lut(k_val)
            y_hex = f"{y_int:04X}"
            val = inv_lut.get(y_hex, 0)
            if isinstance(val, str):
                val = int(val, 16)
            result[r, c] = int(val) & 0xFFFF
    return result

def get_inverse_sbox(sbox_table):
    inv_sbox = np.zeros_like(sbox_table)
    for idx, val in enumerate(sbox_table):
        inv_sbox[int(val) & 0xFF] = idx
    return inv_sbox

def inv_exp_16bit(x, log_table):
    val = int(x) & 0xFFFF
    hi = (val >> 8) & 0xFF
    lo = val & 0xFF
    new_hi = 0 if hi == 0 else int(log_table[hi]) & 0xFF
    new_lo = 0 if lo == 0 else int(log_table[lo]) & 0xFF
    return (new_hi << 8) | new_lo

def inv_log_16bit(x, exp_table):
    val = int(x) & 0xFFFF
    hi = (val >> 8) & 0xFF
    lo = val & 0xFF
    new_hi = 0 if hi == 0 else int(exp_table[hi]) & 0xFF
    new_lo = 0 if lo == 0 else int(exp_table[lo]) & 0xFF
    return (new_hi << 8) | new_lo

def decrypt_phase_2(A11, subkeys, inv_sbox_table):
    subkeys = ensure_subkeys_dict(subkeys)
    A = np.copy(A11)
    num_rows = A.shape[0]
    
    def inv_sbox_16bit(x):
        val = int(x) & 0xFFFF
        hi = int(inv_sbox_table[(val >> 8) & 0xFF]) & 0xFF
        lo = int(inv_sbox_table[val & 0xFF]) & 0xFF
        return (hi << 8) | lo
        
    for j in range(3, 0, -1):
        A10 = np.vectorize(inv_sbox_16bit)(A)
        A9 = np.empty_like(A10)
        for m in range(num_rows):
            A9[m] = A10[(m - 1) % num_rows]
            
        K_j = subkeys.get(j, np.full(A.shape, 0x01 * j, dtype=int))
        A = np.bitwise_xor(A9, K_j)
        
    return A

def decrypt_phase_1(A8, subkeys, log_table, exp_table):
    subkeys = ensure_subkeys_dict(subkeys)
    A = np.copy(A8)
    
    for i in range(16, 0, -1):
        k_odd_idx  = 2 * i + 3
        k_even_idx = 2 * i + 2
        
        K_odd = subkeys.get(k_odd_idx, np.full(A.shape, 0xAA, dtype=int))
        K_even = subkeys.get(k_even_idx, np.full(A.shape, 0x55, dtype=int))
        
        A7 = np.vectorize(lambda x: inv_exp_16bit(x, log_table))(A)
        A6 = apply_dmbox_elementwise(A7, K_odd)
        A5 = np.bitwise_xor(A6, K_odd)
        A4 = np.vectorize(lambda x: inv_log_16bit(x, exp_table))(A5)
        A3 = apply_dmbox_elementwise(A4, K_even)
        A2 = np.bitwise_xor(A3, K_even)
        
        A = A2
        
    return A

def decrypt_Phase_pipeline(A11, subkeys, log_table, exp_table, inv_sbox_table):
    subkeys = ensure_subkeys_dict(subkeys)
    A8_recovered = decrypt_phase_2(A11, subkeys, inv_sbox_table)
    A2_recovered = decrypt_phase_1(A8_recovered, subkeys, log_table, exp_table)
    return A2_recovered
