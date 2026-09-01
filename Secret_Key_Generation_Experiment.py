from MEA_GQA.MEA_GQA import MEA_GQA
if __name__ == "__main__":
    # --- Phần I: Sinh khóa ---
    try:
        MEA_GQA.Create_Key()
    except Exception as e:
        print(f"\n[LỖI THỰC THI PIPELINE] - Sinh Khóa: {e}")
