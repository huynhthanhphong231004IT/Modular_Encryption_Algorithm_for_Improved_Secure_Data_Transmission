import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Encryption.Encryption_MEAGQA import Encryption_MEAGQA

if __name__ == "__main__":
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    os.makedirs(CONTENT_DIR, exist_ok=True)
    input_text_file     = os.path.join(CONTENT_DIR, "sample_doc.txt")
    input_covers_folder = os.path.join(CONTENT_DIR, "Input_Covers")
    output_stego_folder = os.path.join(CONTENT_DIR, "Output_Stego")
    
    # --- Phần II: Mã hóa MEA-GQA ---
    try:
        stego_result_dir = Encryption_MEAGQA(
            input_txt_path=input_text_file,
            input_covers_dir=input_covers_folder,
            output_stego_dir=output_stego_folder
        )
    except Exception as e:
        print(f"\n[LỖI THỰC THI PIPELINE] - Phần mã hóa MEA-GQA: {e}")
