from Key_Management.generate_all_keys import generate_and_save_all_keys
if __name__ == "__main__":
    # --- Phần I: Sinh khóa ---
    try:
        generate_and_save_all_keys()
    except Exception as e:
        print(f"\n[LỖI THỰC THI PIPELINE] - Sinh Khóa: {e}")
