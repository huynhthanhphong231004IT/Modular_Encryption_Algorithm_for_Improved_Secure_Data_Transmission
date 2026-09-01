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

def g_func(x: int, P: int) -> int:
    return x + P * (x ** 2)

def encode_block(x1: int, x2: int, x3: int, x4: int, P: int, B: int) -> int:
    g1 = g_func(x1, P)
    g2 = g_func(x2, P)
    g3 = g_func(x3, P)
    g4 = g_func(x4, P)
    return g1 + B * g2 + (B ** 2) * g3 + (B ** 3) * g4
def encrypt_matrices_to_binary(matrices: list, P: int = None) -> tuple:
    if P is None:
        keys = load_keys()
        P = int(keys.get("P", keys.get("p", 1)))

    hex_nibbles = []
    for mat in matrices:
        flat = mat.flatten()
        for val in flat:
            # Tách số nguyên 16-bit thành 4 nibbles (4-bit)
            val = int(val)
            n1 = (val >> 12) & 0x0F
            n2 = (val >> 8) & 0x0F
            n3 = (val >> 4) & 0x0F
            n4 = val & 0x0F
            hex_nibbles.extend([n1, n2, n3, n4])

    # Đảm bảo chia hết cho 4
    while len(hex_nibbles) % 4 != 0:
        hex_nibbles.append(0)

    B, k = compute_parameters(P)

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
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    
    # 1. Khai báo các đường dẫn file
    input_file = os.path.join(CONTENT_DIR, "E_Phase.npz")
    output_npz = os.path.join(CONTENT_DIR, "E_Final_Permutation.npz")
    output_txt = os.path.join(CONTENT_DIR, "E_Final_Permutation.txt")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Không tìm thấy file đầu vào: {input_file}")

    # 2. Đọc danh sách ma trận và pad_len từ E_Phase.npz
    phase_data = np.load(input_file)
    matrices = phase_data["cipher"]
    pad_len = int(phase_data["pad_len"]) if "pad_len" in phase_data else 0

    print(f"[+] Đã nạp {len(matrices)} khối ma trận từ {input_file}")

    # 3. Thực hiện mã hóa sang chuỗi nhị phân
    binary_text, y_vals, B, k = encrypt_matrices_to_binary(matrices)

    # 4. Lưu kết quả ra file E_Final_Permutation.npz
    os.makedirs(CONTENT_DIR, exist_ok=True)
    np.savez(
        output_npz,
        binary_text=binary_text,
        num_matrices=len(matrices),
        total_blocks=len(matrices),
        pad_len=pad_len,
        B=B,
        k=k
    )

    # 5. Lưu kết quả dạng văn bản ra E_Final_Permutation.txt
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(f"Base (B): {B}\n")
        f.write(f"Bits per block (k): {k}\n")
        f.write(f"Padding Length: {pad_len}\n")
        f.write(f"Total Matrices: {len(matrices)}\n")
        f.write(f"Total Bit Length: {len(binary_text)}\n\n")
        f.write("--- Encrypted Binary Stream ---\n")
        f.write(binary_text + "\n\n")
        f.write("--- Decimal Y Values ---\n")
        for idx, y in enumerate(y_vals):
            f.write(f"Block {idx + 1}: {y}\n")

    print(f"\n[+] Mã hóa phi tuyến bậc 2 thành công.")
    print(f"-> Chuỗi nhị phân đầu ra ({len(binary_text)} bits)")
    print(f"-> File NPZ lưu tại: {output_npz}")
    print(f"-> File Text lưu tại: {output_txt}")