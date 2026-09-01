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
  Step 2. Import the MEA-GQA model.
</p> 

```python
from MEA_GQA.MEA_GQA import MEA_GQA
```

<p>
  Step 3. Generate a secret key for the algorithm.
</p>

```python
MEA_GQA.Create_Key()
```

<p>
  Step 4. Encrypt the data.
</p>

```python
stego_result_dir = MEA_GQA.Encryption_MEAGQA(
      input_txt_path=input_text_file,
      input_covers_dir=input_covers_folder,
      output_stego_dir=output_stego_folder)
```

> [!NOTE]
> **`input_text_file`**: The path to the input text file containing the data or secret message you want to encrypt or hide.
>
> **`input_covers_folder`**: The path to the folder containing the source image files used to hide secret data.
>
> **`output_stego_folder`**: The path to the folder containing the destination image files with hidden information.


<p>
  Step 5. Decrypt the data.
</p>

```python
MEA_GQA.Decoding_MEAGQA(output_stego_folder)
```
