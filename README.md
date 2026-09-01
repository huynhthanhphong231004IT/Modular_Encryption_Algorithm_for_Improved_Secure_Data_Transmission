<h2 align="center">
  Author: Huynh Thanh Phong (ReoRioll)
</h2>

<p align="center">
   Computer Science of College of Information and Communication Technology of Can Tho University (Course 48)<br>
</p>

<p>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<b>Researchs:</b> Artificial Intelligence in Education - Mathematics in Deep Learning and Machine Learning<br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<mark><b><b>Name Project:</b></b> </mark> Modular Encryption Algorithm for Game Question Authentication<br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<mark><b><b>Update Research:</b></b> </mark> Modular Encryption Algorithm for Improved Secure Data Transmission<br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<b>Timeline:</b> 03/2025 – 08/2026 at Computer science department
</p>
<p align="center">
   <b>Presional link Information</b>
</p>

<p>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
Facbook: https://www.facebook.com/huynh.thanh.phong.561667 <br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
Kaggle: https://www.kaggle.com/reorioll <br>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
Youtobe: https://www.youtube.com/@ReoRioll-2304CICTCTU <br>
</p>
<br>

<h3 align="left">
  <span style="color:#8B4513;">
    <b>Clone the code from Git and proceed with testing.</b>
  </span>
</h3>

<p>
  Step 1. Clone module from git
</p>

```python
!git clone https://github.com/huynhthanhphong231004IT/Modular_Encryption_Algorithm_for_Improved_Secure_Data_Transmission.git
```

<p>
  Step 2. Create the file Secret_Key_Generation_Experiment.py. Generate a secret key for the algorithm.
</p>

```python
from MEA_GQA.MEA_GQA import MEA_GQA
if __name__ == "__main__":
    # --- Phần I: Sinh khóa ---
    try:
        MEA_GQA.Create_Key()
    except Exception as e:
        print(f"\n[LỖI THỰC THI PIPELINE] - Sinh Khóa: {e}")
```

<p>
  Step 3. Create the file Encryption_MEAGQA_Experiment.py. Encrypt the data.
</p>

```python
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from MEA_GQA.MEA_GQA import MEA_GQA

if __name__ == "__main__":
    CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content")
    os.makedirs(CONTENT_DIR, exist_ok=True)
    input_text_file     = os.path.join(CONTENT_DIR, "sample_doc.txt")
    input_covers_folder = os.path.join(CONTENT_DIR, "Input_Covers")
    output_stego_folder = os.path.join(CONTENT_DIR, "Output_Stego")
    
    # --- Phần II: Mã hóa MEA-GQA ---
    try:
        stego_result_dir = MEA_GQA.Encryption_MEAGQA(
            input_txt_path=input_text_file,
            input_covers_dir=input_covers_folder,
            output_stego_dir=output_stego_folder
        )
    except Exception as e:
        print(f"\n[LỖI THỰC THI PIPELINE] - Phần mã hóa MEA-GQA: {e}")

```
