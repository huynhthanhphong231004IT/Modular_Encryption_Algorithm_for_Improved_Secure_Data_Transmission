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
    message: str, input_dir: str, output_dir: str = None
) -> list:
    if output_dir is None:
        content_dir = os.path.join(PROJECT_ROOT, "Content")
        output_dir = os.path.join(content_dir, "Output_Stego")
    os.makedirs(output_dir, exist_ok=True)
    cover_image_paths = get_image_files_from_dir(input_dir)
    if not cover_image_paths:
        raise FileNotFoundError(f"Không tìm thấy file ảnh nào trong thư mục: '{input_dir}'")
    keys = load_keys()
    des_key = keys["des_bytes"]
    msg_bytes = message.encode("utf-8")
    if isinstance(message, str) and all(c in '01' for c in message):
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

    print(f"[INFO] Thư mục ảnh đầu vào : {input_dir}")
    print(f"[INFO] Thư mục xuất ảnh Stego: {output_dir}")
    print(f"[INFO] Tổng số bit cần giấu: {LM} bits")
    print(f"[INFO] Dung lượng/ảnh L'    : {L_prime} bits")
    print(f"[INFO] Số ảnh sử dụng (N)   : {N}/{len(cover_image_paths)}")

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
        print(f" -> Đã tạo ảnh Stego {i}/{N}: {out_path}")
    return saved_stego_paths
