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
    byte_list = []
    for i in range(0, len(bits_str), 8):
        byte_list.append(int(bits_str[i : i + 8], 2))
    return bytes(byte_list)

def des_decrypt_64bits(enc_header_64bits: str, des_key_bytes: bytes) -> tuple:
    enc_bytes = bits_to_bytes(enc_header_64bits)
    cipher = DES.new(des_key_bytes, DES.MODE_ECB)
    dec_bytes = cipher.decrypt(enc_bytes)
    dec_bits = "".join(format(b, "08b") for b in dec_bytes)
    N = int(dec_bits[0:32], 2)
    idx = int(dec_bits[32:64], 2)
    return N, idx

def extract_message_from_folder(stego_dir: str) -> tuple:
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
    pad_len = 0
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
        try:
            N, img_index = des_decrypt_64bits(enc_header_bits, des_key)
        except Exception:
            continue
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
            else:
                M_i_bits.append(str(val % 2))
        segments[img_index] = "".join(M_i_bits)
    if not segments:
        raise ValueError("Không trích xuất được bit nào từ các ảnh trong thư mục Stego! Kiểm tra lại quá trình giấu tin (Encoding).")
    full_binary_M = ""
    for i in range(1, (total_images_N or len(segments)) + 1):
        if i in segments:
            full_binary_M += segments[i]
        else:
            raise KeyError(f"Thiếu đoạn dữ liệu từ ảnh stego số {i}")
    return full_binary_M, pad_len
