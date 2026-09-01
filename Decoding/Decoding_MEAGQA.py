import os
import sys
import glob
import numpy as np
from PIL import Image
from Crypto.Cipher import DES

# 1. Định nghĩa đường dẫn gốc dự án
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Key_Management.key_manager import load_keys, InitialPermutation_load_initial_permutation_key
from Decoding.D_Initial_Permutation import decrypt_text
from Decoding.D_Phase import ensure_subkeys_dict, decrypt_Phase_pipeline, get_inverse_sbox
from Decoding.D_Final_Permutation import decrypt_binary_to_matrices
from Create_Lookup_Table.Create_L_E_S import generate_log_exp_tables, get_sbox


# --- BƯỚC 1: HÀM HỖ TRỢ TRÍCH XUẤT STEGO ---
def bits_to_bytes(bits_str: str) -> bytes:
    byte_list = [int(bits_str[i : i + 8], 2) for i in range(0, len(bits_str), 8)]
    return bytes(byte_list)

def des_decrypt_64bits(enc_header_64bits: str, des_key_bytes: bytes) -> tuple:
    enc_bytes = bits_to_bytes(enc_header_64bits)
    cipher = DES.new(des_key_bytes, DES.MODE_ECB)
    dec_bytes = cipher.decrypt(enc_bytes)

    dec_bits = "".join(format(b, "08b") for b in dec_bytes)
    N = int(dec_bits[0:32], 2)
    idx = int(dec_bits[32:64], 2)
    return N, idx

def extract_message_from_folder(stego_dir: str) -> str:
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

    full_binary_M = ""
    for i in range(1, total_images_N + 1):
        full_binary_M += segments[i]

    return full_binary_M


# --- MAIN PIPELINE CHẨN ĐOÁN TỪNG BƯỚC FILE KẾT HỢP LƯU NPZ ---
def run_step_by_step_pipeline():
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    stego_folder = os.path.join(CONTENT_DIR, "Output_Stego")
    
    # Khai báo các đường dẫn file .npz
    file_e_final = os.path.join(CONTENT_DIR, "E_Final_Permutation.npz")
    file_e_phase = os.path.join(CONTENT_DIR, "E_Phase.npz")
    
    file_d_stego = os.path.join(CONTENT_DIR, "D_Steganography.npz")
    file_d_final = os.path.join(CONTENT_DIR, "D_Final_Permutation.npz")
    file_d_phase = os.path.join(CONTENT_DIR, "D_Phase.npz")
    file_d_result = os.path.join(CONTENT_DIR, "D_Result.txt")

    print("=" * 70)
    print(" BẮT ĐẦU CHẨN ĐOÁN VÀ GIẢI MÃ NỐI TIẾP TỪNG FILE (.NPZ)")
    print("=" * 70)

    # -----------------------------------------------------------------
    # BƯỚC 1: TRÍCH XUẤT STEGO -> LƯU D_Steganography.npz
    # -----------------------------------------------------------------
    print("\n[BƯỚC 1] Trích xuất chuỗi Bit từ thư mục Stego...")
    rec_binary = extract_message_from_folder(stego_folder)
    
    # Lấy metadata từ E_Final_Permutation.npz nếu có
    pad_len, num_matrices = 0, len(rec_binary) // 90
    if os.path.exists(file_e_final):
        data_e_final = np.load(file_e_final, allow_pickle=True)
        pad_len = int(data_e_final["pad_len"]) if "pad_len" in data_e_final else 0
        num_matrices = int(data_e_final["num_matrices"]) if "num_matrices" in data_e_final else num_matrices
        orig_binary = str(data_e_final["binary_text"])
        
        # Check đối chứng
        is_stego_exact = (rec_binary == orig_binary)
        print(f"  -> Kết quả Bit trích xuất : {len(rec_binary)} bits")
        print(f"  -> Đối chứng E_Final_Permutation : {'[✓] KHỚP 100%' if is_stego_exact else '[X] SAI LỆCH!'}")

    # Ghi ra file D_Steganography.npz
    np.savez(file_d_stego, binary_text=rec_binary, pad_len=pad_len, num_matrices=num_matrices)
    print(f"  -> Đã lưu kết quả Bước 1 vào: {file_d_stego}")

    # -----------------------------------------------------------------
    # BƯỚC 2: ĐỌC D_Steganography.npz -> GIẢI MÃ FINAL PERMUTATION -> LƯU D_Final_Permutation.npz
    # -----------------------------------------------------------------
    print("\n[BƯỚC 2] Giải mã Binary thành Ma trận (Final Permutation)...")
    d_stego_data = np.load(file_d_stego, allow_pickle=True)
    binary_to_decode = str(d_stego_data["binary_text"])
    matrices_count = int(d_stego_data["num_matrices"])

    recovered_matrices = decrypt_binary_to_matrices(binary_to_decode, matrices_count)
    recovered_matrices = np.array(recovered_matrices, dtype=np.int64)

    if os.path.exists(file_e_phase):
        orig_phase_data = np.load(file_e_phase, allow_pickle=True)
        orig_matrices = orig_phase_data["cipher"] if "cipher" in orig_phase_data else orig_phase_data["phase2_cipher"]
        is_final_exact = np.array_equal(orig_matrices, recovered_matrices)
        print(f"  -> Số lượng khối ma trận khôi phục: {len(recovered_matrices)}")
        print(f"  -> Đối chứng E_Phase.npz        : {'[✓] KHỚP 100%' if is_final_exact else '[X] SAI LỆCH!'}")

    # Ghi ra file D_Final_Permutation.npz
    np.savez(file_d_final, cipher=recovered_matrices, pad_len=pad_len)
    print(f"  -> Đã lưu kết quả Bước 2 vào: {file_d_final}")

    # -----------------------------------------------------------------
    # BƯỚC 3: ĐỌC D_Final_Permutation.npz -> GIẢI MÃ PHASE -> LƯU D_Phase.npz
    # -----------------------------------------------------------------
    print("\n[BƯỚC 3] Giải mã Phase từ D_Final_Permutation.npz...")
    d_final_data = np.load(file_d_final, allow_pickle=True)
    phase_input_blocks = d_final_data["cipher"]

    keys_dict = load_keys()
    mea_matrices = keys_dict.get("mea_matrices", [])
    subkeys = {
        idx + 1: np.array(mat, dtype=np.int64) 
        for idx, mat in enumerate(mea_matrices)
    } if isinstance(mea_matrices, (list, np.ndarray)) else keys_dict.get("mea_matrices", {})

    subkeys = ensure_subkeys_dict(subkeys)
    log_table, exp_table = generate_log_exp_tables()
    sbox_table = get_sbox()
    inv_sbox_table = get_inverse_sbox(sbox_table)

    phase_decoded_blocks = []
    for blk in phase_input_blocks:
        dec_b = decrypt_Phase_pipeline(blk, subkeys, log_table, exp_table, inv_sbox_table)
        phase_decoded_blocks.append(np.array(dec_b, dtype=np.int64))

    phase_decoded_blocks = np.array(phase_decoded_blocks, dtype=np.int64)

    if os.path.exists(file_e_phase):
        orig_phase_data = np.load(file_e_phase, allow_pickle=True)
        if "cipher" in orig_phase_data and "phase2_cipher" in orig_phase_data:
            # Nếu E_Phase lưu input gốc là 'cipher'
            orig_phase_input = orig_phase_data["cipher"]
            is_phase_exact = np.array_equal(orig_phase_input, phase_decoded_blocks)
            print(f"  -> Đối chứng Ma trận đầu vào Phase gốc: {'[✓] KHỚP 100%' if is_phase_exact else '[X] SAI LỆCH!'}")
            if not is_phase_exact:
                print("     [X] Ma trận Gốc Khối 1:\n", orig_phase_input[0])
                print("     [X] Ma trận Giải Mã Khối 1:\n", phase_decoded_blocks[0])

    # Ghi ra file D_Phase.npz
    np.savez(file_d_phase, cipher=phase_decoded_blocks, pad_len=pad_len)
    print(f"  -> Đã lưu kết quả Bước 3 vào: {file_d_phase}")

    # -----------------------------------------------------------------
    # BƯỚC 4: ĐỌC D_Phase.npz -> HOÁN VỊ BAN ĐẦU (D_Initial_Permutation) -> VĂN BẢN
    # -----------------------------------------------------------------
    print("\n[BƯỚC 4] Khôi phục Văn bản Gốc (Initial Permutation)...")
    d_phase_data = np.load(file_d_phase, allow_pickle=True)
    final_phase_blocks = d_phase_data["cipher"]

    p, g, S = InitialPermutation_load_initial_permutation_key()
    restored_text = decrypt_text(final_phase_blocks, pad_len, p, g, S)

    with open(file_d_result, "w", encoding="utf-8") as f:
        f.write(restored_text)

    print("=" * 70)
    print(" KẾT QUẢ VĂN BẢN GIẢI MÃ BẰNG NỐI TIẾP FILE NPZ:")
    print("=" * 70)
    print(restored_text)
    print("=" * 70)
    print(f"-> Đã xuất kết quả văn bản giải mã vào: {file_d_result}")


if __name__ == "__main__":
    run_step_by_step_pipeline()