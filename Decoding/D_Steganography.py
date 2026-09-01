import os
import sys
import glob
import numpy as np
from PIL import Image
from Crypto.Cipher import DES

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys


def bits_to_bytes(bits_str: str) -> bytes:
    """Chuyển đổi chuỗi nhị phân bội số 8 về dạng bytes."""
    byte_list = []
    for i in range(0, len(bits_str), 8):
        byte_list.append(int(bits_str[i : i + 8], 2))
    return bytes(byte_list)


def des_decrypt_64bits(enc_header_64bits: str, des_key_bytes: bytes) -> tuple:
    """Giải mã 64 bit Header bằng DES thu lại N và index i."""
    enc_bytes = bits_to_bytes(enc_header_64bits)
    cipher = DES.new(des_key_bytes, DES.MODE_ECB)
    dec_bytes = cipher.decrypt(enc_bytes)

    dec_bits = "".join(format(b, "08b") for b in dec_bytes)
    N = int(dec_bits[0:32], 2)
    idx = int(dec_bits[32:64], 2)

    return N, idx


def extract_message_from_folder(stego_dir: str = None) -> str:
    """
    Đọc toàn bộ các ảnh Stego trong thư mục stego_dir.
    Nếu không truyền stego_dir, mặc định lấy từ Content/Output_Stego.
    """
    if stego_dir is None:
        stego_dir = os.path.join(PROJECT_ROOT, "Content", "Output_Stego")

    valid_extensions = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff")
    stego_image_paths = []
    for ext in valid_extensions:
        stego_image_paths.extend(glob.glob(os.path.join(stego_dir, ext)))
        stego_image_paths.extend(glob.glob(os.path.join(stego_dir, ext.upper())))

    if not stego_image_paths:
        raise FileNotFoundError(f"Không tìm thấy ảnh Stego nào trong thư mục: '{stego_dir}'")

    keys = load_keys()
    des_key = keys["des_bytes"]

    segments = {}
    total_images_N = None

    for img_path in stego_image_paths:
        img = Image.open(img_path).convert("RGBA")
        img_np = np.array(img)

        alpha_flat = img_np[:, :, 3].flatten()

        enc_header_bits = ""
        for val in alpha_flat[:64]:
            if val == 254:
                enc_header_bits += "0"
            elif val == 255:
                enc_header_bits += "1"
            else:
                break

        if len(enc_header_bits) < 64:
            continue

        N, img_index = des_decrypt_64bits(enc_header_bits, des_key)
        if total_images_N is None:
            total_images_N = N

        M_i_bits = []
        for val in alpha_flat[64:]:
            if val == 254:
                M_i_bits.append("0")
            elif val == 255:
                M_i_bits.append("1")
            elif val == 253:
                break

        segments[img_index] = "".join(M_i_bits)

    if not segments:
        raise ValueError("Không tìm thấy dữ liệu giấu tin hợp lệ trong thư mục!")

    full_binary_M = ""
    for i in range(1, total_images_N + 1):
        if i not in segments:
            raise KeyError(f"Thiếu phân đoạn ảnh thứ {i} trong thư mục Stego!")
        full_binary_M += segments[i]

    msg_bytes = bits_to_bytes(full_binary_M)
    return full_binary_M

if __name__ == "__main__":
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    stego_folder = os.path.join(CONTENT_DIR, "Output_Stego")
    
    # 1. Đường dẫn file lưu kết quả và file đối chứng
    output_npz = os.path.join(CONTENT_DIR, "D_Steganography.npz")
    output_txt = os.path.join(CONTENT_DIR, "D_Steganography.txt")
    original_npz = os.path.join(CONTENT_DIR, "E_Final_Permutation.npz")

    try:
        # 2. Trích xuất chuỗi nhị phân từ các ảnh stego
        recovered_binary = extract_message_from_folder(stego_folder)
        print(f"[+] Trích xuất thành công {len(recovered_binary)} bits từ {stego_folder}")

        # 3. Đọc dữ liệu từ E_Final_Permutation.npz để đối chứng
        if not os.path.exists(original_npz):
            raise FileNotFoundError(f"Không tìm thấy file đối chứng: {original_npz}")

        orig_data = np.load(original_npz)
        original_binary = str(orig_data["binary_text"])
        pad_len = int(orig_data["pad_len"]) if "pad_len" in orig_data else 0
        num_matrices = int(orig_data["num_matrices"]) if "num_matrices" in orig_data else 0

        # 4. THUẬT TOÁN SO SÁNH TỪNG BIT (Bit-by-Bit Comparison)
        len_orig = len(original_binary)
        len_rec = len(recovered_binary)
        
        mismatches = 0
        first_mismatch_idx = -1
        
        # So sánh độ dài tối thiểu của 2 chuỗi
        min_len = min(len_orig, len_rec)
        for idx in range(min_len):
            if original_binary[idx] != recovered_binary[idx]:
                mismatches += 1
                if first_mismatch_idx == -1:
                    first_mismatch_idx = idx

        # Nếu độ dài chênh lệch, đếm số bit thừa/thiếu vào số bit sai
        mismatches += abs(len_orig - len_rec)
        
        # Tỷ lệ chính xác %
        match_rate = ((max(len_orig, len_rec) - mismatches) / max(len_orig, len_rec)) * 100
        is_exact_100_percent = (mismatches == 0) and (len_orig == len_rec)

        # 5. Lưu kết quả trích xuất ra D_Steganography.npz
        np.savez(
            output_npz,
            binary_text=recovered_binary,
            num_matrices=num_matrices,
            pad_len=pad_len
        )

        # 6. Lưu kết quả chi tiết ra D_Steganography.txt
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(f"Exact Match (100% Bit-by-Bit): {is_exact_100_percent}\n")
            f.write(f"Bit Match Accuracy Rate      : {match_rate:.4f}%\n")
            f.write(f"Total Original Bits          : {len_orig}\n")
            f.write(f"Total Recovered Bits         : {len_rec}\n")
            f.write(f"Total Bit Mismatches         : {mismatches}\n")
            if first_mismatch_idx != -1:
                f.write(f"First Mismatch Index         : Bit thứ {first_mismatch_idx}\n")
            f.write(f"Number of Matrices           : {num_matrices}\n")
            f.write(f"Padding Length               : {pad_len}\n\n")
            f.write("--- Recovered Binary Stream ---\n")
            f.write(recovered_binary + "\n")

        # 7. In báo cáo chi tiết ra Terminal
        print("\n" + "=" * 65)
        print("KHÔI PHỤC & KIỂM TRA SO SÁNH TỪNG BIT (D_Steganography.py)")
        print("=" * 65)
        print(f"Tổng số bit gốc (E_Final_Permutation) : {len_orig} bits")
        print(f"Tổng số bit trích xuất (D_Steganography): {len_rec} bits")
        print(f"Số bit bị lệch / sai khác             : {mismatches} bits")
        print(f"Tỷ lệ khớp bit chính xác              : {match_rate:.2f}%")
        
        if is_exact_100_percent:
            print("=> THÀNH CÔNG: TẤT CẢ CÁC BIT ĐỀU TRÙNG KHỚP 100%!")
        else:
            print(f"=> CẢNH BÁO: Lệch tại vị trí bit đầu tiên: #{first_mismatch_idx}")

        print(f"-> File NPZ giải mã lưu tại : {output_npz}")
        print(f"-> File Text giải mã lưu tại: {output_txt}")
        print("=" * 65)

    except Exception as e:
        print(f"[LỖI GIẢI MÃ] {e}")