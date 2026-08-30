import secrets

def generate_DES_key_64bit():
    key_bytes = secrets.token_bytes(8)
    key_int = int.from_bytes(key_bytes, byteorder='big')
    key_bits_str = f"{key_int:064b}"
    return key_bytes, key_int, key_bits_str



key_bytes, key_int, key_bits = generate_DES_key_64bit()
print(f"1. Khóa D (Dạng Bytes): {key_bytes}")
print(f"2. Khóa D (Dạng Số nguyên): {key_int}")
print(f"3. Khóa D (Chuỗi 64 bit): {key_bits}")
print(f"-> Độ dài chuỗi bit: {len(key_bits)} bit")