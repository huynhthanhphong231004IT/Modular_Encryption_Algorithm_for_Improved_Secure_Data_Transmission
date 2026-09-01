import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from Decoding.Decoding_MEAGQA import Decoding_MEAGQA

if __name__ == "__main__":
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    os.makedirs(CONTENT_DIR, exist_ok=True)
    output_stego_folder = os.path.join(CONTENT_DIR, "Output_Stego")

    # --- Phần III: Giải mã MEA-GQA ---
    try:
        Decoding_MEAGQA(output_stego_folder)
    except Exception as e:
        print(f"\n[LỖI THỰC THI PIPELINE] - Phần giải mã MEA-GQA: {e}")