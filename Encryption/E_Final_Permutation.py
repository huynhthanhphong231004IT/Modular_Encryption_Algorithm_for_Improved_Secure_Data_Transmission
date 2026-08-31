import os
import sys
import math
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys

def compute_parameters(P: int):
    """
    Tính cơ số B và số bit k cần thiết cho mỗi khối y.
    B > max g(x) = 15 + 225P ==> Chọn B = 16 + 225P
    k = ceil(4 * log2(B))
    """
    max_g = 15 + 225 * P
    B = max_g + 1
    k = math.ceil(4 * math.log2(B))
    return B, k

def g_func(x: int, P: int) -> int:
    """Hàm mã hóa thành phần: g(x) = x + P * x^2"""
    return x + P * (x ** 2)

def encode_block(x1: int, x2: int, x3: int, x4: int, P: int, B: int) -> int:
    """Mã hóa bộ 4 giá trị (x1, x2, x3, x4) thành 1 số nguyên y duy nhất"""
    g1 = g_func(x1, P)
    g2 = g_func(x2, P)
    g3 = g_func(x3, P)
    g4 = g_func(x4, P)
    return g1 + B * g2 + (B ** 2) * g3 + (B ** 3) * g4

def encrypt_matrices_to_binary(matrices: list, P: int = None) -> tuple:
    """
    Quy trình mã hóa từ danh sách ma trận A(12)_n (3x3).
    Tự động nạp tham số P từ load_keys() nếu không truyền vào.
    """
    if P is None:
        keys = load_keys()
        # Lấy tham số P (hoặc p) từ hệ thống khóa dùng chung
        P = int(keys.get("P", keys.get("p", 1)))

    N = len(matrices)
    if N % 2 != 0:
        matrices.append(np.zeros_like(matrices[0]))

    # 1. Làm phẳng và ghép tuần tự các ma trận
    flattened_bytes = []
    for mat in matrices:
        flat = mat.flatten()
        for val in flat:
            flattened_bytes.append(int(val) & 0xFF)

    # 2. Tách mỗi byte thành 2 giá trị hex (h_left, h_right) 4-bit (0-15)
    hex_nibbles = []
    for b in flattened_bytes:
        h_left = (b >> 4) & 0x0F
        h_right = b & 0x0F
        hex_nibbles.extend([h_left, h_right])

    while len(hex_nibbles) % 4 != 0:
        hex_nibbles.append(0)

    # 3. Tính thông số B và k
    B, k = compute_parameters(P)

    # 4. Mã hóa từng khối 4 nibbles -> y -> Binary string k-bit
    binary_blocks = []
    y_values = []
    
    for i in range(0, len(hex_nibbles), 4):
        x1, x2, x3, x4 = hex_nibbles[i:i+4]
        y = encode_block(x1, x2, x3, x4, P, B)
        y_values.append(y)
        
        bin_str = format(y, f'0{k}b')
        binary_blocks.append(bin_str)

    final_binary_text = "".join(binary_blocks)
    return final_binary_text, y_values, B, k

if __name__ == "__main__":
    sample_matrices = [
        np.array([[0x12, 0x34, 0x56], [0x78, 0x9A, 0xBC], [0xDE, 0xF0, 0x11]], dtype=np.int64),
        np.array([[0xAA, 0xBB, 0xCC], [0xDD, 0xEE, 0xFF], [0x00, 0x11, 0x22]], dtype=np.int64)
    ]

    binary_text, y_vals, B, k = encrypt_matrices_to_binary(sample_matrices)
    
    print("=" * 60)
    print("MÃ HÓA PHI TUYẾN BẬC 2 (E_Nonlinear.py)")
    print(f"Cơ số B          : {B}")
    print(f"Số bit/khối (k)  : {k}")
    print(f"Số khối y tạo ra : {len(y_vals)}")
    print(f"Chuỗi nhị phân A(13) (50 bit đầu): {binary_text[:50]}...")
    print("=" * 60)