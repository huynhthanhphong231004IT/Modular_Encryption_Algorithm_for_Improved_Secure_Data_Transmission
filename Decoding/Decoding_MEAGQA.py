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
from Decoding.D_Initial_Permutation import decrypt_text
from Decoding.D_Phase import ensure_subkeys_dict, decrypt_Phase_pipeline, get_inverse_sbox
from Decoding.D_Final_Permutation import decrypt_binary_to_matrices
from Decoding.D_Steganography import extract_message_from_folder
from Create_Lookup_Table.Create_L_E_S import generate_log_exp_tables, get_sbox

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

def Decoding_MEAGQA(stego_dir: str):
    if not os.path.exists(stego_dir):
        raise FileNotFoundError(f"Thư mục Stego không tồn tại: '{stego_dir}'")

    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    file_e_final = os.path.join(CONTENT_DIR, "E_Final_Permutation.npz")
    file_e_phase = os.path.join(CONTENT_DIR, "E_Phase.npz")
    file_d_stego = os.path.join(CONTENT_DIR, "D_Steganography.npz")
    output_txt = os.path.join(CONTENT_DIR, "D_Steganography.txt")
    file_d_final = os.path.join(CONTENT_DIR, "D_Final_Permutation.npz")
    file_d_phase = os.path.join(CONTENT_DIR, "D_Phase.npz")
    file_d_result = os.path.join(CONTENT_DIR, "D_Result.txt")
    DATA_FILE = os.path.join(CONTENT_DIR, "E_Initial_Permutation.npz")

    print(" BẮT ĐẦU CHẨN ĐOÁN VÀ GIẢI MÃ NỐI TIẾP TỪNG FILE (.NPZ)")
    try:
        recovered_binary, extracted_pad_len = extract_message_from_folder(stego_folder)
        print(f"[+] Trích xuất thành công {len(recovered_binary)} bits từ {stego_folder}")
        if not os.path.exists(file_e_final):
            raise FileNotFoundError(f"Không tìm thấy file đối chứng: {file_e_final}")
        orig_data = np.load(file_e_final)
        original_binary = str(orig_data["binary_text"])
        pad_len = int(orig_data["pad_len"]) if "pad_len" in orig_data else 0
        num_matrices = int(orig_data["num_matrices"]) if "num_matrices" in orig_data else 0
        len_orig = len(original_binary)
        len_rec = len(recovered_binary)
        mismatches = 0
        first_mismatch_idx = -1
        min_len = min(len_orig, len_rec)
        for idx in range(min_len):
            if original_binary[idx] != recovered_binary[idx]:
                mismatches += 1
                if first_mismatch_idx == -1:
                    first_mismatch_idx = idx
        mismatches += abs(len_orig - len_rec)
        match_rate = ((max(len_orig, len_rec) - mismatches) / max(len_orig, len_rec)) * 100
        is_exact_100_percent = (mismatches == 0) and (len_orig == len_rec)
        np.savez(
            file_d_stego,
            binary_text=recovered_binary,
            num_matrices=num_matrices,
            pad_len=pad_len
        )
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
        print("KHÔI PHỤC & KIỂM TRA SO SÁNH TỪNG BIT (D_Steganography.py)")
        print(f"Tổng số bit gốc (E_Final_Permutation) : {len_orig} bits")
        print(f"Tổng số bit trích xuất (D_Steganography): {len_rec} bits")
        print(f"Số bit bị lệch / sai khác             : {mismatches} bits")
        print(f"Tỷ lệ khớp bit chính xác              : {match_rate:.2f}%")
        if is_exact_100_percent:
            print("=> THÀNH CÔNG: TẤT CẢ CÁC BIT ĐỀU TRÙNG KHỚP 100%!")
        else:
            print(f"=> CẢNH BÁO: Lệch tại vị trí bit đầu tiên: #{first_mismatch_idx}")
        print(f"-> File NPZ giải mã lưu tại : {file_d_stego}")
        print(f"-> File Text giải mã lưu tại: {output_txt}")
        print("=" * 65)
    except Exception as e:
        print(f"[LỖI GIẢI MÃ] {e}")
    if not os.path.exists(file_e_final):
        raise FileNotFoundError(f"Không tìm thấy file mã hóa: {file_e_final}")
    if not os.path.exists(file_e_phase):
        raise FileNotFoundError(f"Không tìm thấy file gốc: {file_e_phase}")
    data_enc = np.load(file_e_final)
    binary_text = str(data_enc["binary_text"])
    num_matrices = int(data_enc["num_matrices"]) if "num_matrices" in data_enc else int(data_enc["total_blocks"])
    data_orig = np.load(file_e_phase)
    original_matrices = data_orig["cipher"]
    recovered_matrices = decrypt_binary_to_matrices(binary_text, num_matrices)
    is_exact_match = np.array_equal(original_matrices, recovered_matrices)
    print("KIỂM TRA GIẢI MÃ PHI TUYẾN BẬC 2 (E_Final_Permutation.npz -> E_Phase.npz)")
    print(f"Khôi phục chính xác 100%   : {is_exact_match}")
    if not os.path.exists(file_e_phase):
        print(f"[!] Không tìm thấy file đầu vào: {file_e_phase}")
        sys.exit(1)
    data = np.load(file_e_phase, allow_pickle=True)
    phase2_blocks = data['phase2_cipher'] if 'phase2_cipher' in data.files else data['cipher']
    original_input = data['cipher'] if 'cipher' in data.files else None
    pad_len = int(data['pad_len']) if 'pad_len' in data.files else 0
    try:
        keys_dict = load_keys()
        mea_matrices = keys_dict.get("mea_matrices", [])
        subkeys = {
            idx + 1: np.array(mat, dtype=np.int64) 
            for idx, mat in enumerate(mea_matrices)
        } if isinstance(mea_matrices, (list, np.ndarray)) else keys_dict.get("mea_matrices", {})
    except Exception:
        subkeys = {k: np.full((3, 3), k, dtype=np.int64) for k in range(1, 37)}
    subkeys = ensure_subkeys_dict(subkeys)
    log_table, exp_table = generate_log_exp_tables()
    sbox_table = get_sbox()
    inv_sbox_table = get_inverse_sbox(sbox_table)
    recovered_blocks = [
        decrypt_Phase_pipeline(block, subkeys, log_table, exp_table, inv_sbox_table)
        for block in phase2_blocks
    ]
    print("GIẢI MÃ PHASE HOÀN TẤT (D_Phase.py)")
    if original_input is not None:
        print("\n=== KIỂM TRA TÍNH CHÍNH XÁC (E_Phase vs D_Phase) ===")
        all_matched = True
        for idx, (orig, rec) in enumerate(zip(original_input, recovered_blocks)):
            if np.array_equal(orig, rec):
                print(f"Block {idx + 1}: KHỚP HOÀN TOÀN (100%)")
            else:
                all_matched = False
                print(f"Block {idx + 1}: KHÔNG KHỚP!")
                print(" -> Gốc    :\n", orig)
                print(" -> Giải mã:\n", rec)
        if all_matched:
            print("\n>>> KẾT LUẬN: THÀNH CÔNG! Mã hóa và giải mã khớp 100%. <<<")
        else:
            print("\n>>> KẾT LUẬN: THẤT BẠI! Hãy kiểm tra lại logic Phase 1. <<<")
    try:
        p, g, S = InitialPermutation_load_initial_permutation_key()
        data = np.load(DATA_FILE)
        cipher_blocks = list(data["cipher"])
        pad_len = int(data["pad_len"])
        restored_text = decrypt_text(cipher_blocks, pad_len, p, g, S)
        print("\n[+] Kết quả giải mã thành công:\n")
        output_file = os.path.join(CONTENT_DIR, "RESULT_Sample_doc_Encrypted.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(restored_text)
        print(f"\n[+] Đã lưu văn bản giải mã tại: {output_file}")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{DATA_FILE}'. Vui lòng chạy file mã hóa trước!")

