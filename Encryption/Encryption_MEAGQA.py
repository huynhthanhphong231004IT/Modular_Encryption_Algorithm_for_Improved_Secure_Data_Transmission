import os
import sys
import glob
import numpy as np
from PIL import Image
from Crypto.Cipher import DES

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys, InitialPermutation_load_initial_permutation_key
from Encryption.E_Initial_Permutation import encrypt_text
from Encryption.E_Phase import parse_to_int_array, encrypt_phase_pipeline
from Create_Lookup_Table.Create_L_E_S import generate_log_exp_tables, get_sbox
from Encryption.E_Final_Permutation import encrypt_matrices_to_binary


def bytes_to_bits(data_bytes: bytes) -> str:
    return "".join(format(b, "08b") for b in data_bytes)


def des_encrypt_64bits(header_bits_64: str, des_key_bytes: bytes) -> str:
    header_bytes = int(header_bits_64, 2).to_bytes(8, byteorder="big")
    cipher = DES.new(des_key_bytes, DES.MODE_ECB)
    encrypted_bytes = cipher.encrypt(header_bytes)
    return bytes_to_bits(encrypted_bytes)


def get_image_files_from_dir(input_dir: str) -> list:
    valid_extensions = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff")
    image_paths = []
    for ext in valid_extensions:
        image_paths.extend(glob.glob(os.path.join(input_dir, ext)))
        image_paths.extend(glob.glob(os.path.join(input_dir, ext.upper())))
    image_paths.sort()
    return image_paths


def embed_message_from_folder(
    message: str, input_dir: str, output_dir: str
) -> list:
    os.makedirs(output_dir, exist_ok=True)
    cover_image_paths = get_image_files_from_dir(input_dir)
    if not cover_image_paths:
        raise FileNotFoundError(f"Không tìm thấy file ảnh nào trong thư mục: '{input_dir}'")
    
    keys = load_keys()
    des_key = keys["des_bytes"]

    if isinstance(message, str) and all(c in "01" for c in message):
        M_b = message
    else:
        M_b = bytes_to_bits(message.encode("utf-8"))

    LM = len(M_b)
    first_img = Image.open(cover_image_paths[0]).convert("RGBA")
    W, H = first_img.size
    Npixels = H * W
    L_prime = Npixels - 64  
    N = (LM + L_prime - 1) // L_prime

    if N > len(cover_image_paths):
        raise ValueError(
            f"Thông điệp quá lớn ({LM} bits). Cần {N} ảnh nhưng thư mục '{input_dir}' chỉ có {len(cover_image_paths)} ảnh!"
        )

    print(f"  [Stego] Số bit giấu       : {LM} bits")
    print(f"  [Stego] Dung lượng/ảnh L' : {L_prime} bits")
    print(f"  [Stego] Số ảnh sử dụng (N): {N}/{len(cover_image_paths)}")

    saved_stego_paths = []

    for i in range(1, N + 1):
        start_idx = (i - 1) * L_prime
        end_idx = min(i * L_prime, LM)
        M_i = M_b[start_idx:end_idx]

        header_N_bits = format(N, "032b")
        header_i_bits = format(i, "032b")
        header_64bits = header_N_bits + header_i_bits
        enc_header_64bits = des_encrypt_64bits(header_64bits, des_key)
        payload_bits = enc_header_64bits + M_i

        img = Image.open(cover_image_paths[i - 1]).convert("RGBA")
        img_np = np.array(img)
        alpha_flat = img_np[:, :, 3].flatten()
        total_pixels = len(alpha_flat)

        for idx in range(total_pixels):
            if idx < len(payload_bits):
                bit = payload_bits[idx]
                alpha_flat[idx] = 254 if bit == "0" else 255
            else:
                alpha_flat[idx] = 253

        img_np[:, :, 3] = alpha_flat.reshape((H, W))
        stego_img = Image.fromarray(img_np, mode="RGBA")
        out_filename = f"stego_image_{i}.png"
        out_path = os.path.join(output_dir, out_filename)
        stego_img.save(out_path, format="PNG")
        saved_stego_paths.append(out_path)

    return saved_stego_paths

def run_full_encryption_pipeline(input_txt_path: str, input_covers_dir: str, output_stego_dir: str):
    CONTENT_DIR = os.path.dirname(input_txt_path)
    os.makedirs(CONTENT_DIR, exist_ok=True)
    os.makedirs(output_stego_dir, exist_ok=True)

    print("=" * 65)
    print(" BẮT ĐẦU LUỒNG MÃ HÓA HOÀN CHỈNH (FULL ENCRYPTION PIPELINE)")
    print("=" * 65)
    print("\n[BƯỚC 1] Đọc văn bản và Hoán vị ban đầu")
    if not os.path.exists(input_txt_path):
        raise FileNotFoundError(f"Không tìm thấy file văn bản gốc: {input_txt_path}")
    with open(input_txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    p, g, S = InitialPermutation_load_initial_permutation_key()
    cipher_blocks, pad_len = encrypt_text(text, p, g, S)
    file_e_init_npz = os.path.join(CONTENT_DIR, "E_Initial_Permutation.npz")
    file_e_init_txt = os.path.join(CONTENT_DIR, "E_Initial_Permutation.txt")
    np.savez(file_e_init_npz, cipher=np.array(cipher_blocks), pad_len=pad_len)
    with open(file_e_init_txt, "w", encoding="utf-8") as f:
        f.write(f"Padding Length: {pad_len}\nTotal Blocks: {len(cipher_blocks)}\n\n")
        for idx, block in enumerate(cipher_blocks):
            f.write(f"--- Block {idx + 1} ---\n")
            np.savetxt(f, block, fmt="%d")
            f.write("\n")
    print(f"  -> Đã tạo {len(cipher_blocks)} khối ban đầu.")
    print("\n[BƯỚC 2] Xử lý mã hóa Phase")
    mea_cipher_blocks = [parse_to_int_array(b) for b in cipher_blocks]
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
    file_e_phase_npz = os.path.join(CONTENT_DIR, "E_Phase.npz")
    np.savez(
        file_e_phase_npz,
        cipher=mea_cipher_blocks,
        pad_len=pad_len,
        phase1_cipher=np.array(phase_1_outputs, dtype=object),
        phase2_cipher=np.array(phase_2_raw, dtype=object),
        phase2_hex=np.array(phase_2_hex, dtype=object)
    )
    print("  -> Mã hóa Phase hoàn tất.")
    print("\n[BƯỚC 3] Hoán vị cuối & Chuyển đổi ma trận sang dạng nhị phân")
    binary_text, y_vals, B, k = encrypt_matrices_to_binary(mea_cipher_blocks)
    file_e_final_npz = os.path.join(CONTENT_DIR, "E_Final_Permutation.npz")
    file_e_final_txt = os.path.join(CONTENT_DIR, "E_Final_Permutation.txt")
    np.savez(
        file_e_final_npz,
        binary_text=binary_text,
        num_matrices=len(mea_cipher_blocks),
        total_blocks=len(mea_cipher_blocks),
        pad_len=pad_len,
        B=B,
        k=k
    )

    with open(file_e_final_txt, "w", encoding="utf-8") as f:
        f.write(f"Base (B): {B}\n")
        f.write(f"Bits per block (k): {k}\n")
        f.write(f"Padding Length: {pad_len}\n")
        f.write(f"Total Matrices: {len(mea_cipher_blocks)}\n")
        f.write(f"Total Bit Length: {len(binary_text)}\n\n")
        f.write("--- Encrypted Binary Stream ---\n")
        f.write(binary_text + "\n\n")
        f.write("--- Decimal Y Values ---\n")
        for idx, y in enumerate(y_vals):
            f.write(f"Block {idx + 1}: {y}\n")

    print(f"  -> Chuỗi bit đầu ra: {len(binary_text)} bits")
    print("\n[BƯỚC 4] Nhúng chuỗi bit mã hóa vào kênh Alpha của ảnh")
    stego_paths = embed_message_from_folder(
        message=binary_text,
        input_dir=input_covers_dir,
        output_dir=output_stego_dir
    )

    print("\n" + "=" * 65)
    print(" [HOÀN THÀNH PIPELINE] Đã mã hóa và tạo ảnh Stego thành công!")
    print(f" -> Thư mục ảnh Stego đầu ra: {output_stego_dir}")
    print(" Danh sách các file ảnh Stego đã lưu:")
    for path in stego_paths:
        print(f"   - {path}")
    print("=" * 65)

    return output_stego_dir


if __name__ == "__main__":
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    input_text_file = os.path.join(CONTENT_DIR, "sample_doc.txt")
    input_covers_folder = os.path.join(CONTENT_DIR, "Input_Covers")
    output_stego_folder = os.path.join(CONTENT_DIR, "Output_Stego")
    try:
        stego_result_dir = run_full_encryption_pipeline(
            input_txt_path=input_text_file,
            input_covers_dir=input_covers_folder,
            output_stego_dir=output_stego_folder
        )
    except Exception as e:
        print(f"\n[LỖI THỰC THI PIPELINE] {e}")