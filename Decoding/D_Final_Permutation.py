import os
import sys
import math
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys

def compute_parameters(P: int):
    max_g = 15 + 225 * P
    B = max_g + 1
    k = math.ceil(4 * math.log2(B))
    return B, k

def solve_x(d: int, P: int) -> int:
    """
    Giải phương trình P*x^2 + x - d = 0 với x >= 0
    Công thức nghiệm: x = (-1 + sqrt(1 + 4*P*d)) / (2*P)
    """
    delta = 1 + 4 * P * d
    sqrt_delta = math.isqrt(delta)
    x = (-1 + sqrt_delta) // (2 * P)
    return int(x)

def decode_block(y: int, P: int, B: int) -> tuple:
    """
    Phân rã cơ số B và khôi phục bộ (x1, x2, x3, x4) từ y (Theo Bảng 2.16)
    """
    d4 = y // (B ** 3)
    r3 = y - d4 * (B ** 3)

    d3 = r3 // (B ** 2)
    r2 = r3 - d3 * (B ** 2)

    d2 = r2 // B
    r1 = r2 - d2 * B

    d1 = r1

    x4 = solve_x(d4, P)
    x3 = solve_x(d3, P)
    x2 = solve_x(d2, P)
    x1 = solve_x(d1, P)

    return x1, x2, x3, x4

def decrypt_binary_to_matrices(binary_text: str, num_matrices: int, P: int = None) -> list:
    """
    Quy trình giải mã từ chuỗi nhị phân A(13) về lại danh sách ma trận A(12)_n (3x3).
    Tự động nạp P từ load_keys() nếu không truyền vào.
    """
    if P is None:
        keys = load_keys()
        P = int(keys.get("P", keys.get("p", 1)))

    B, k = compute_parameters(P)

    # 1. Tách chuỗi nhị phân thành các khối k-bit và chuyển lại thành số y
    y_values = []
    for i in range(0, len(binary_text), k):
        bin_chunk = binary_text[i:i+k]
        if len(bin_chunk) == k:
            y_values.append(int(bin_chunk, 2))

    # 2. Giải mã từng y để khôi phục các nibble 4-bit (x1, x2, x3, x4)
    recovered_nibbles = []
    for y in y_values:
        x1, x2, x3, x4 = decode_block(y, P, B)
        recovered_nibbles.extend([x1, x2, x3, x4])

    # 3. Ghép cặp (h_left, h_right) lại thành các byte ban đầu
    recovered_bytes = []
    for i in range(0, len(recovered_nibbles), 2):
        if i + 1 < len(recovered_nibbles):
            h_left = recovered_nibbles[i]
            h_right = recovered_nibbles[i+1]
            byte_val = (h_left << 4) | h_right
            recovered_bytes.append(byte_val)

    # 4. Tái cấu trúc lại các ma trận 3x3
    target_N = num_matrices if num_matrices % 2 == 0 else num_matrices + 1
    
    recovered_matrices = []
    bytes_per_matrix = 9

    for n in range(target_N):
        start_idx = n * bytes_per_matrix
        end_idx = start_idx + bytes_per_matrix
        mat_flat = recovered_bytes[start_idx:end_idx]
        if len(mat_flat) == 9:
            mat = np.array(mat_flat, dtype=np.int64).reshape((3, 3))
            recovered_matrices.append(mat)

    return recovered_matrices[:num_matrices]

if __name__ == "__main__":
    from Encryption.E_Final_Permutation import encrypt_matrices_to_binary

    original_matrices = [
        np.array([[0x12, 0x34, 0x56], [0x78, 0x9A, 0xBC], [0xDE, 0xF0, 0x11]], dtype=np.int64),
        np.array([[0xAA, 0xBB, 0xCC], [0xDD, 0xEE, 0xFF], [0x00, 0x11, 0x22]], dtype=np.int64)
    ]

    # Kiểm chứng quy trình Mã hóa -> Giải mã dùng chung key từ key_manager
    binary_text, y_vals, B, k = encrypt_matrices_to_binary(original_matrices)
    recovered_matrices = decrypt_binary_to_matrices(binary_text, len(original_matrices))

    print("=" * 60)
    print("GIẢI MÃ PHI TUYẾN BẬC 2 (D_Nonlinear.py)")
    print(f"Số ma trận gốc          : {len(original_matrices)}")
    print(f"Khôi phục chính xác 100%: {np.array_equal(original_matrices, recovered_matrices)}")
    print(f"Ma trận gốc A(12)_1     :\n{original_matrices[0]}")
    print(f"Ma trận giải mã A(12)_1 :\n{recovered_matrices[0]}")
    print("=" * 60)