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
    if P is None:
        keys = load_keys()
        P = int(keys.get("P", keys.get("p", 1)))

    B, k = compute_parameters(P)

    # 1. Tách chuỗi nhị phân thành các khối k-bit
    y_values = []
    for i in range(0, len(binary_text), k):
        bin_chunk = binary_text[i:i+k]
        if len(bin_chunk) == k:
            y_values.append(int(bin_chunk, 2))

    # 2. Giải mã từng y
    recovered_nibbles = []
    for y in y_values:
        x1, x2, x3, x4 = decode_block(y, P, B)
        recovered_nibbles.extend([x1, x2, x3, x4])

    # 3. Lấy đúng số nibble cho num_matrices (mỗi ma trận 3x3 có 9 phần tử * 4 nibbles = 36 nibbles)
    total_required_nibbles = num_matrices * 9 * 4
    recovered_nibbles = recovered_nibbles[:total_required_nibbles]

    # 4. Tái lập các giá trị phần tử 16-bit
    recovered_values = []
    for i in range(0, len(recovered_nibbles), 4):
        n1, n2, n3, n4 = recovered_nibbles[i:i+4]
        val = (n1 << 12) | (n2 << 8) | (n3 << 4) | n4
        recovered_values.append(val)

    # 5. Tái cấu trúc lại các ma trận 3x3
    recovered_matrices = []
    for n in range(num_matrices):
        start_idx = n * 9
        end_idx = start_idx + 9
        mat_flat = recovered_values[start_idx:end_idx]
        mat = np.array(mat_flat, dtype=np.int64).reshape((3, 3))
        recovered_matrices.append(mat)

    return recovered_matrices

if __name__ == "__main__":
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    
    # 1. Đường dẫn các file cần kiểm tra
    file_encrypted = os.path.join(CONTENT_DIR, "E_Final_Permutation.npz")
    file_original = os.path.join(CONTENT_DIR, "E_Phase.npz")

    if not os.path.exists(file_encrypted):
        raise FileNotFoundError(f"Không tìm thấy file mã hóa: {file_encrypted}")
    if not os.path.exists(file_original):
        raise FileNotFoundError(f"Không tìm thấy file gốc: {file_original}")

    # 2. Đọc chuỗi nhị phân từ E_Final_Permutation.npz
    data_enc = np.load(file_encrypted)
    binary_text = str(data_enc["binary_text"])
    num_matrices = int(data_enc["num_matrices"]) if "num_matrices" in data_enc else int(data_enc["total_blocks"])

    # 3. Đọc dữ liệu gốc từ E_Phase.npz để làm đối chứng
    data_orig = np.load(file_original)
    original_matrices = data_orig["cipher"]

    # 4. Thực hiện giải mã
    recovered_matrices = decrypt_binary_to_matrices(binary_text, num_matrices)

    # 5. So sánh 2 tập ma trận
    is_exact_match = np.array_equal(original_matrices, recovered_matrices)

    print("=" * 60)
    print("KIỂM TRA GIẢI MÃ PHI TUYẾN BẬC 2 (E_Final_Permutation.npz -> E_Phase.npz)")
    print(f"Tổng số khối ma trận gốc    : {len(original_matrices)}")
    print(f"Tổng số khối giải mã        : {len(recovered_matrices)}")
    print(f"Khôi phục chính xác 100%   : {is_exact_match}")
    print("=" * 60)

    if len(original_matrices) > 0:
        print("\n--- Ma trận gốc (Khối 1 - E_Phase.npz) ---")
        print(original_matrices[0])
        print("\n--- Ma trận giải mã (Khối 1 - D_Nonlinear) ---")
        print(recovered_matrices[0])