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

<p>
  Step 5. Decrypt the data.
</p>

```python
MEA_GQA.Decoding_MEAGQA(output_stego_folder)
```


> [!NOTE]
> **`input_text_file`**: The path to the input text file containing the data or secret message you want to encrypt or hide.
>
> **`input_covers_folder`**: The path to the folder containing the source image files used to hide secret data.
>
> **`output_stego_folder`**: The path to the folder containing the destination image files with hidden information.


<h3 align="left">
  <span style="color:#8B4513;">
    <b>Theoretical framework of the proposed study</b>
  </span>
</h3>

<h2 align="center">
  <span style="color:#8B4513;">
    <b>Mô hình mã hóa mô - đun trên dữ liệu đường truyền cải tiến (MEA-GQA)</b>
  </span>
</h2>

<p align="center">
  <img src="Images/MEA_TC.png" width="800">
  <br>
  <i>Kiến trúc mô hình mã hóa mô - đun trên dữ liệu đường truyền cải tiến (MEA-GQA) </i>
</p>


## Đóng góp chính của nghiên cứu

Nghiên cứu này kế thừa cấu trúc nền tảng của thuật toán MEA (Modular Encryption Algorithm) của IJSRNSC - Author: P.Sri Ram Chandra, G. Venkateswara Rao, G.V. Swamy và đề xuất các cải tiến nhằm nâng cao độ an toàn mật mã (bằng việc mở rộng trường khóa) cũng như tối ưu hóa khả năng ứng dụng trong lĩnh vực giấu tin ảnh số. Các đóng góp chính bao gồm:

<mark>1. Cải tiến cơ chế hoán vị ban đầu trên trường hữu hạn</mark>
- Thay thế cơ chế hoán vị cố định của MEA gốc bằng phép biến đổi tuyến tính trên trường hữu hạn, kết hợp ma trận khả nghịch và phần tử sinh.
- Hiệu quả: Mở rộng đáng kể không gian khóa, tăng tính ngẫu nhiên của quá trình hoán vị và nâng cao khả năng chống phân tích tuyến tính nhờ duy trì tính đơn ánh của phép ánh xạ.

<mark>2. Trộn dữ liệu qua các phép XOR cùng giải thuật M-Box</mark>
- Hòa trộn và che giấu cấu trúc dữ liệu thông qua phép XOR với ma trận khóa, kết hợp các phép ánh xạ Logarithm, Exponentials và Substitution Box.
- Hàm M-Box: Xây dựng cơ chế ánh xạ phi tuyến biến 4 giá trị hexadecimal thành 2 giá trị hexadecimal, không tồn tại phép nghịch đảo, dựa trên các phép toán trên trường Galois ($GF$).

<mark>3. Tầng hoán vị phi tuyến bậc hai sau mã hóa</mark>
- Áp dụng phép biến đổi phi tuyến ngay sau khi tạo bản mã bằng MEA để tăng cường tính hỗn loạn (confusion) và khả năng khuếch tán (diffusion).
- Hiệu quả: Phá vỡ các quan hệ tuyến tính còn tồn tại trong bản mã, làm gia tăng độ phức tạp của cấu trúc mã hóa và nâng cao khả năng chống lại các phương pháp phân tích mật mã (cryptanalysis).

<mark>4. Tích hợp cơ chế giấu tin ảnh RGBA sử dụng LSB kết hợp DES</mark>
- Mô hình bảo vệ đa lớp: Phân mảnh bản mã và nhúng trực tiếp vào kênh Alpha của ảnh RGBA.
- Quản lý dữ liệu: Thông tin tiêu đề (header) của mỗi ảnh được mã hóa bằng thuật toán DES để quản lý chính xác số lượng và thứ tự các phân đoạn.
- Cơ chế nhúng: Nhúng dữ liệu theo quy tắc mã hóa 3 mức trên giá trị Alpha, giúp bảo đảm khôi phục dữ liệu chính xác $100\%$, duy trì chất lượng thị giác của ảnh mang tin (cover image) và tăng cường độ an toàn trong lưu trữ cũng như truyền tải.


<h3 align="left">
  <span style="color:#8B4513;">
    <b>1. Quá trình sinh khóa</b>
  </span>
</h3>

Không gian khóa tổng thể của hệ thống được biểu diễn bởi tập hợp:
<h5 align="center">
  <span style="color:#8B4513;">
    $$\mathcal{K} = \{S_1, S_2, \dots, S_{36}, p, g, P, B, D\}$$
  </span>
</h5>

Trong đó, các ma trận $S_{1 \to 35}$ được sinh từ tập tham số $n = [n_1, n_2, \dots, n_{35}]$ theo công thức tương ứng.

| Tham số | Mô tả | Vai trò |
| :--- | :--- | :--- |
| $[n_1, n_2, \dots, n_{35}]$ | 35 giá trị nguyên $n_i$ được sử dụng để sinh tương ứng 35 ma trận tam thức $[S_1, S_2, \dots, S_{35}]$ theo công thức tổng quát. | Xác định tập ma trận tam thức phục vụ các phép biến đổi mật mã, đồng thời cho phép tái tạo ma trận từ tham số $n_i$ thay vì phải lưu trữ trực tiếp các ma trận. |
| $S_{36}, p, g$ | $p$ và $g$ là các tham số nguyên tố của hệ mật; $S_{36}$ là ma trận được sinh từ nhóm tuyến tính tổng quát $GL(3, \mathbb{F}_p)$. | Xác lập không gian tham số và cấu trúc đại số cho các phép biến đổi, góp phần bảo đảm tính khả nghịch của hệ mật. |
| $P, B$ | $P$ là số nguyên dương và $B$ là tham số thỏa mãn điều kiện $B > 15 + 225P$. | Xác định miền tham số và các điều kiện ràng buộc cần thiết cho quá trình biến đổi và xử lý bản mã. |
| $D = 64\text{ bit}$ | Độ dài khóa được sử dụng trong thành phần mật mã DES, với kích thước 64 bit. | Xác định kích thước khóa và không gian khóa tương ứng của hệ thống. |

<h3 align="left">
  <span style="color:#8B4513;">
    <b>2. Cải tiến cơ chế hoán vị ban đầu trên trường hữu hạn</b>
  </span>
</h3>

Giả sử $p$ là một số nguyên tố lớn ($p > 255$), $g$ là phần tử sinh của nhóm nhân hữu hạn $\mathbb{F}_p^\times$ và $S_{36} = S \in GL(3, \mathbb{F}_p)$ là một ma trận khả nghịch được sử dụng làm khóa bí mật của hệ mật. Theo định nghĩa của nhóm tuyến tính tổng quát $GL(3, \mathbb{F}_p)$, ma trận $S$ phải thỏa mãn điều kiện $\det(S) \not\equiv 0 \pmod p$. Điều kiện này bảo đảm sự tồn tại của ma trận nghịch đảo $S^{-1}$ sao cho $S S^{-1} \equiv I_3 \pmod p$, trong đó $I_3$ là ma trận đơn vị cấp $3 \times 3$. Tính khả nghịch của $S$ bảo đảm mọi phép biến đổi thực hiện trên dữ liệu đều có thể được khôi phục một cách duy nhất thông qua khóa bí mật tương ứng.

**Đầu vào (Input):** Chuỗi bản rõ (*Plaintext*) được chia thành các khối gồm 9 ký tự. Mỗi khối 9 ký tự tương ứng với $9 \times 8 = 72\text{ bit}$ dữ liệu.

$$X^{(1)} = \begin{bmatrix} 
x_{00} & x_{01} & x_{02} \\ 
x_{10} & x_{11} & x_{12} \\ 
x_{20} & x_{21} & x_{22} 
\end{bmatrix}$$

trong đó $a_{00}$ đến $a_{22}$ là các giá trị ASCII của 9 ký tự tương ứng, được biểu diễn ở dạng Hexadecimal (cơ số 16). Nhờ cách biểu diễn này, ma trận thông điệp có thể được xây dựng trực tiếp từ các khối dữ liệu dạng hexadecimal, tạo điều kiện thuận lợi cho việc thực hiện các phép biến đổi đại số trên trường hữu hạn $\mathbb{F}_p$ trong các bước mã hóa tiếp theo.

$$A^{(2)} = \text{Enc}_{GL(3, \mathbb{F}_p)}(X^{(1)}, g, S) = \begin{bmatrix} 
a_{00} & a_{01} & a_{02} \\ 
a_{10} & a_{11} & a_{12} \\ 
a_{20} & a_{21} & a_{22} 
\end{bmatrix}$$

#### Quy trình mã hóa – giải mã của giai đoạn hoán vị đầu giải thuật MEA tăng cường

| Bước | Mã hóa: $\text{Enc}_{GL(3, \mathbb{F}_p)}(X, g, S)$ | Giải mã: $\text{Dec}_{GL(3, \mathbb{F}_p)}(X, g, S)$ |
| :---: | :--- | :--- |
| **1** | Cho ma trận $X = (x_{ij})$ | Nhận bản mã $Y$ |
| **2** | Tính $M = [g^{x_{ij}} \bmod p]$ | Tính $M' = S^{-1}YS$ |
| **3** | Tính $Y = SMS^{-1}$ | Tính $X = [\log_g(M'_{ij})] \bmod (p - 1)$ |

<h3 align="left">
  <span style="color:#8B4513;">
    <b>3. Trộn dữ liệu qua các pha XoR</b>
  </span>
</h3>

## Quy trình xử lý các Pha mã hóa

**Pha I: Lặp 16 lần thực hiện với trường khóa S từ 4 đến 35**

Lặp tuần tự i = 1 đến $16$ thực hiện các bước sau:

| Vòng | Bước | Tên phép toán | Mô tả |
| :---: | :---: | :--- | :--- |
| **I.1 - Vòng 1**<br>*(Khóa S chẵn: i = 2i + 2)* | 1 | Phép XOR với khóa | $A^{(3)} = A^{(2)} \oplus K_i$ |
| | 2 | Phép nén lần 1 qua hộp M-Box | $A^{(4)} = \text{M-Box}(A^{(3)}, K_i)$ |
| | 3 | Bảng logarit (Log Table) | $A^{(5)} = \log(A^{(4)})$ |
| **I.2 - Vòng 2**<br>*(Khóa S lẻ: i = 2i + 3)* | 1 | Phép XOR với khóa mới | $A^{(6)} = A^{(5)} \oplus K_i$ |
| | 2 | Phép nén lần 2 qua hộp M-Box | $A^{(7)} = \text{M-Box}(A^{(6)}, K_i)$ |
| | 3 | Bảng mũ (Exponential Table) | $A^{(8)} = \exp(A^{(7)})$ |

<br>

**Pha II: Lặp 3 lần thực hiện với trường khóa S từ 1 đến 3**
Lặp tuần tự j = 1 đến 3 thực hiện các bước sau:

| STT | Tên phép toán | Mô tả |
| :---: | :--- | :--- |
| 1 | Phép XOR với khóa tam thức | $A^{(9)} = A^{(8)} \oplus K_j$ |
| 2 | Hoán vị hàng (Row Interchange) | $R_m \leftarrow R_{(m+1) \bmod 3}, \quad 0 \le m \le 2$<br>*(Hàng m được thay thế bằng hàng kế tiếp theo chu kỳ $\bmod 3$)* |
| 3 | Phép thay thế byte (Sub-Bytes) | $A^{(11)} = \text{S-Box}(A^{(10)})$ |

**Chuyển đổi sang giá trị thập lục phân:** $A^{(12)} = \text{Hexadecimal}(A^{(11)})$.

## Giải thuật sinh bảng tra M-Box

Thông qua các phép nén phi tuyến trên trường hữu hạn, M-Box triệt tiêu hoàn toàn hàm ngược toán học trực tiếp. Điều này khiến việc khôi phục lại dữ liệu gốc từ đầu ra là không thể thực hiện về mặt tính toán, vô hiệu hóa hoàn toàn các đòn tấn công giải mã ngược ngay cả khi kẻ tấn công sở hữu siêu máy tính.

- Đầu vào (Input): Một khối gồm 4 chữ số Hexadecimal.
- Đầu ra (Output): Một khối gồm 2 chữ số Hexadecimal.

- Bước 1: Biểu diễn dưới dạng nhị phân (ví dụ: 2ACF): Mỗi chữ số Hexadecimal được biểu diễn bằng 4 bit nhị phân. (Ví dụ: F = 1111)
- Bước 2: Chia dãy bit thành hai phần và biểu diễn dưới dạng đa thức: Chia dãy 16 bit thành 2 phần bằng nhau, mỗi phần gồm 8 bits. Quy định 8 bits trái (left) là $A^{(1)}$, 8 bits phải (right) là $B^{(1)}$. (Ví dụ: 2ACF được tách ra $A^{(1)} = \text{2A} = 00101010$, $B^{(1)} = \text{CF} = 11001111$)
- Bước 3: Tra cứu khóa từ ma trận $S_{3 \times 3}$ và thực hiện phép toán với dữ liệu: Giá trị khóa 8 bits $K_{i,j}$ được tra cứu từ ma trận khóa $S_{3 \times 3}$ với chỉ số hàng $i = p \bmod 3$ và chỉ số cột $j = g \bmod 3$: $$K_{i,j} = S[p \bmod 3, g \bmod 3]$$. Sau đó, các khối dữ liệu $A^{(1)}$ và $B^{(1)}$ thực hiện phép nhân trường Galois với khóa tương ứng: $$A^{(2)}(x) = \left( A^{(1)}(x) \cdot K_i(x) \right) \bmod G(x)$$ và $$B^{(2)}(x) = \left( B^{(1)}(x) \cdot K_j(x) \right) \bmod G(x)$$ với $G(x) = x^8 + x^4 + x^3 + x + 1$ (tương ứng mã 0x11B).
- Bước 4: Kiểm tra bit thứ 7 của kết quả và dịch bit có điều kiện: Kiểm tra bit thứ 7 (giá trị 0x80) của dữ liệu. Nếu bit thứ 7 là 1 ($A^{(2)} \text{ AND } \text{0x80} \neq 0$), thực hiện dịch trái 1 bit và khử tràn bằng phép XOR với đa thức 0x11B: $$A^{(3)} = (A^{(2)} \ll 1) \oplus \text{0x11B}$$ (tương tự cho $B^{(3)} = (B^{(2)} \ll 1) \oplus \text{0x11B}$). Ngược lại, nếu bit thứ 7 là 0, giữ nguyên giá trị $A^{(3)} = A^{(2)}$ và $B^{(3)} = B^{(2)}$.
- Bước 5: Nhân hai đa thức: Thực hiện phép nhân hai đa thức vừa thu được bằng phép nhân đa thức thông thường (không rút gọn theo modulo ở bước này), do đó kết quả là một đa thức bậc cao (thường lớn hơn 8): $$P(x) = A^{(3)} \times B^{(3)}$$
- Bước 6: Chọn các hạng tử có hệ số lẻ và chia modulo 11B: Từ đa thức kết quả $P(x)$, chỉ giữ lại các hạng tử có hệ số lẻ (bỏ các hệ số chẵn và bỏ hệ số, chỉ giữ phần lũy thừa của $x$). Ví dụ nếu biểu thức thu được là $x^{12} + x^{11} + x^{10} + x^9 + 2x^8 + 2x^7 + 2x^6 + 2x^5 + 2x^4 + 2x^3 + x^2 + x$, thì biểu thức với các hệ số lẻ là $x^{12} + x^{11} + x^{10} + x^9 + x^2 + x$. Biểu thức tương tự khi bỏ qua hệ số (đưa về hệ số 1) là $x^{12} + x^{10} + x^9 + x^5 + x$ và tiến hành chia cho 11B, tức là $x^8 + x^4 + x^3 + x + 1$ kết quả thu được $x^5 + x^3 + x^2 + x + 1$.
- Bước 7: Chuyển đổi biểu thức đa thức kết quả sang dạng nhị phân và hexadecimal. Ví dụ $x^5 + x^3 + x^2 + x + 1$ tương đương $00101111$ tương đương 2F.

<h3 align="left">
  <span style="color:#8B4513;">
    <b>4. Hoán vị phi tuyến bậc hai sau quá trình mã hóa</b>
  </span>
</h3>

Sau bước trộn dữ liệu qua các pha XOR tồn tại $\mathcal{N}$ ma trận $3 \times 3$: $A_n^{(12)}$ với $n \in [1, 2, \dots, \mathcal{N}]$. Nếu $\mathcal{N}$ là số lẻ thì thêm $A_{\mathcal{N}+1}$ vào cuối, ngược lại giữ nguyên.

Làm phẳng và ghép tuần tự các ma trận lại với nhau: $$\mathcal{W} \longrightarrow \text{vec}(A_n^{(12)})^T \longrightarrow [a_{00}^1, a_{01}^1, a_{02}^1 \dots a_{22}^1, a_{00}^2, a_{01}^2, a_{02}^2 \dots a_{22}^2 \dots a_{00}^{\mathcal{N}}, a_{01}^{\mathcal{N}}, a_{02}^{\mathcal{N}} \dots a_{22}^{\mathcal{N}}, \dots]$$. Với mỗi giá trị $a_x^y$ là tổ hợp 2 giá trị hex được tách thành tập 2 giá trị hex riêng biệt $(h_{\text{left}}, h_{\text{right}})$ tiến hành tính toán:

$$\begin{aligned}
\text{Khối 1: } & (x_1, x_2, x_3, x_4) = (\underbrace{h_1, h_2}_{a_{00}^1}, \underbrace{h_3, h_4}_{a_{01}^1}) \longrightarrow y_1 \longrightarrow A_1^{(13)} = \text{Binary}(y_1) \\
\text{Khối 2: } & (x_1, x_2, x_3, x_4) = (\underbrace{h_5, h_6}_{a_{02}^1}, \underbrace{h_7, h_8}_{a_{03}^1}) \longrightarrow y_2 \longrightarrow A_2^{(13)} = \text{Binary}(y_2) \\
\text{Khối 3: } & (x_1, x_2, x_3, x_4) = (\underbrace{h_9, h_{10}}_{a_{10}^1}, \underbrace{h_{11}, h_{12}}_{a_{11}^1}) \longrightarrow y_3 \longrightarrow A_3^{(13)} = \text{Binary}(y_3) \\
\text{Khối 4: } & (x_1, x_2, x_3, x_4) = (\underbrace{h_{13}, h_{14}}_{a_{12}^1}, \underbrace{h_{15}, h_{16}}_{a_{20}^1}) \longrightarrow y_4 \longrightarrow A_4^{(13)} = \text{Binary}(y_4) \\
& \dots \\
\text{Khối n: } & (x_1, x_2, x_3, x_4) = (\underbrace{h_{13}, h_{14}}_{a_{21}^n}, \underbrace{h_{15}, h_{16}}_{a_{22}^n}) \longrightarrow y_n \longrightarrow A_n^{(13)} = \text{Binary}(y_n)
\end{aligned}$$

Ghép tuần tự các giá trị nhị phân ta được chuỗi nhị phân mã hóa Text với hàm hoán vị phi tuyến bậc 2 được định nghĩa bên dưới: $$A^{(13)} = A_1^{(13)} A_2^{(13)} A_3^{(13)} \dots A_n^{(13)}$$. Hàm mã hóa thành phần: Xét bài toán mã hóa một bộ dữ liệu gồm bốn thành phần $(x_1, x_2, x_3, x_4)$ thành một số nguyên duy nhất $y$. Giả sử miền giá trị của các phần tử dữ liệu đầu vào được giới hạn bởi $x_i \in \mathbb{Z}$ và $0 \le x_i \le 15$ với mọi $i \in \{1, 2, 3, 4\}$. Chọn một hằng số nguyên dương $P \in \mathbb{Z}^+$. Hàm mã hóa thành phần $g(x) : \mathbb{Z}^+ \to \mathbb{Z}^+$ được định nghĩa như sau: $$g(x) = x + P x^2$$. Để đảm bảo khả năng đảo ngược cấu trúc mã hóa mà không xảy ra hiện tượng chồng lấn giá trị (aliasing), ta chọn cơ số mã hóa $B \in \mathbb{Z}^+$ thỏa mãn điều kiện nghiêm ngặt: $B > \max_{0 \le x \le 15} g(x) = 15 + 225P$. Khi đó, giá trị mã hóa tổng hợp $y : (\mathbb{Z}^+)^4 \to \mathbb{Z}^+$ của bộ dữ liệu theo hệ cơ số $B$ được xác định thông qua tổ hợp tuyến tính lũy thừa $$y = g(x_1) + B \cdot g(x_2) + B^2 \cdot g(x_3) + B^3 \cdot g(x_4)$$. Triển khai tường minh bằng cách thay thế $g(x_i)$, ta thu được biểu thức đa thức đại số: $$y = (x_1 + P x_1^2) + B(x_2 + P x_2^2) + B^2(x_3 + P x_3^2) + B^3(x_4 + P x_4^2) = \sum_{i=1}^{4} x_i B^{i-1} + P \sum_{i=1}^{4} x_i^2 B^{i-1}$$

Do điều kiện ràng buộc $g(x_i) < B$ với mọi $i$, các giá trị $g(x_i)$ đóng vai trò tương tự như các chữ số đại diện độc lập trong hệ cơ số $B$. Hệ quả là, ta hoàn toàn có thể bóc tách ngược một cách tuần tự các thành phần $g(x_i)$ từ bậc cao xuống bậc thấp bằng phép toán lấy phần nguyên $\lfloor \cdot \rfloor$. Giá trị $y$ sinh ra nằm trong khoảng $y \in [0, B^4 - 1]$. Vì đã chứng minh được $y < B^4$, số bit tối đa cần thiết để biểu diễn mọi giá trị của $y$ được cố định hoàn toàn theo công thức: $$k = \lceil \log_2(B^4) \rceil = \lceil 4 \log_2 B \rceil \quad (\text{bits})$$

Hàm giải mã: Sau khi trích xuất được giá trị $d_i = g(x_i)$, ta thực hiện giải phương trình bậc hai đối với biến số $x_i$: $P x_i^2 + x_i - d_i = 0$. Tuy nhiên, do điều kiện biên ban đầu quy định dữ liệu đầu vào $x_i \ge 0$ và tham số $P \in \mathbb{Z}^+$, nghiệm ứng với dấu trừ ($\frac{-1-\sqrt{\Delta}}{2P}$) luôn cho giá trị âm và bị loại. Vì vậy, ta thu được công thức khôi phục nghiệm duy nhất:

$$x_i = \frac{-1 + \sqrt{1 + 4 P d_i}}{2P}$$

| Bước ($i$) | Giá trị trích xuất $d_i$ | Phần dư kế tiếp $r$ | Giá trị khôi phục $x_i$ |
| :---: | :---: | :---: | :---: |
| 1 | $d_4 = \lfloor \frac{y}{B^3} \rfloor$ | $r_3 = y - d_4 B^3$ | $x_4 = \frac{-1 + \sqrt{1 + 4 P d_4}}{2P}$ |
| 2 | $d_3 = \lfloor \frac{r_3}{B^2} \rfloor$ | $r_2 = r_3 - d_3 B^2$ | $x_3 = \frac{-1 + \sqrt{1 + 4 P d_3}}{2P}$ |
| 3 | $d_2 = \lfloor \frac{r_2}{B} \rfloor$ | $r_1 = r_2 - d_2 B$ | $x_2 = \frac{-1 + \sqrt{1 + 4 P d_2}}{2P}$ |
| 4 | $d_1 = r_1$ | — | $x_1 = \frac{-1 + \sqrt{1 + 4 P d_1}}{2P}$ |

<h3 align="left">
  <span style="color:#8B4513;">
    <b>5. Cơ sở giấu ảnh trong kênh màu RGBA</b>
  </span>
</h3>

Một ảnh màu kỹ thuật số thông thường có thể được biểu diễn dưới dạng một hàm rời rạc: $I : \Omega \to \{0, 1, \dots, 255\}^3$ trong đó $\Omega = \{(x, y) \mid 0 \le x < H, 0 \le y < W\}$ đại diện cho tập hợp tọa độ pixel của ảnh có chiều cao $H$ và chiều rộng $W$. $I(x, y) = [R(x, y), G(x, y), B(x, y)]$ là vector biểu diễn cường độ của ba kênh màu thành phần bao gồm: Đỏ (Red), Lục (Green), và Lam (Blue). Khi mở rộng sang không gian màu RGBA, mỗi điểm ảnh được bổ sung thêm một kênh độ trong suốt (Alpha): $I'(x, y) = [R(x, y), G(x, y), B(x, y), A(x, y)]$ với $A(x, y) \in [0, 255]$ là giá trị xác định độ mờ đục (opacity) của điểm ảnh tại tọa độ $(x, y)$.

Giả sử thông điệp cần giấu $M$ là một chuỗi ký tự bất kỳ. Trước khi thực hiện nhúng, thông điệp này được mã hóa sang chuỗi nhị phân dưới dạng $M_b = (b_1, b_2, b_3, \dots, b_L)$, $b_i \in \{0, 1\}$ với $L = 8 \times \text{len}(M)$ là tổng số bit cần giấu. Mỗi bit $b_i$ sẽ được ánh xạ tương ứng vào một pixel $(x_i, y_i)$ cụ thể trên ảnh.

Bước 1: Phân chia thông điệp theo kích thước ảnh: Đối với một ảnh có kích thước $H \times W$, tổng số lượng điểm ảnh khả dụng được tính bằng $N_{\text{pixels}} = H \cdot W$. Để dành không gian cho thông tin điều khiển, kích thước tối đa của phần phân đoạn dữ liệu $L'$ trong mỗi ảnh được xác định bởi công thức $L' = N_{\text{pixels}} - 64$. Giả sử toàn bộ thông điệp nhị phân $M$ có độ dài tổng cộng là $L_M$. Số lượng phân đoạn ảnh $n$ cần thiết để phân tán thông điệp được tính bằng phép lấy trần $n = \lceil \frac{L_M}{L'} \rceil$. Khi đó, phân đoạn thứ $i$ (với $i = 1, 2, \dots, n$) của thông điệp được trích xuất bằng kỹ thuật cắt chuỗi $M_i = M[(i - 1)L' : \min(iL', L_M)]$.

Bước 2: Sinh cấu trúc khối thông tin điều khiển (Header): Trong 64 pixel đầu tiên của mỗi ảnh, hệ thống cấu trúc 64 bit dữ liệu điều khiển nhằm phục vụ cho giải thuật giải mã, bao gồm: (1) Với 32 bit đầu tiên: Biểu diễn nhị phân của tổng số lượng ảnh $N$ được phát đi trong toàn bộ quá trình truyền thông; (2) Với 32 bit tiếp theo: Biểu diễn nhị phân của số thứ tự chỉ mục $i$ của phân đoạn thông điệp được lưu trữ trong chính ảnh hiện tại. Cấu trúc phân bổ thông tin điều khiển tổng quát được biểu diễn dưới dạng sơ đồ bit như sau:

$$\begin{aligned}
\text{Header}_{\text{image}} = \underbrace{bit_1 bit_2 \dots bit_{32}}_{\text{Tổng số lượng ảnh } N} \quad \underbrace{bit_{33} bit_{34} \dots bit_{64}}_{\text{Chỉ mục ảnh hiện tại } i}
\end{aligned}$$

Bước 3: Sử dụng mật mã DES mã hóa 64 bits chỉ mục: Để tăng cường tính bảo mật, thuật toán sử dụng hệ mã hóa đối xứng DES (Data Encryption Standard) để mã hóa toàn bộ 64 bit của khối Header này trước khi nhúng. Phần không gian pixel còn lại của ảnh sẽ được dùng để lưu trữ nội dung thông điệp thực tế.

Bước 4: Nguyên lý nhúng dữ liệu thông điệp: Thuật toán áp dụng kỹ thuật thay thế bit ít quan trọng nhất (Least Significant Bit - LSB) nhưng được tùy biến để chỉ tác động lên kênh Alpha ($A$). Nhằm đảm bảo tính vô hình về mặt thị giác đối với mắt người, giá trị của kênh Alpha được duy trì tiệm cận mức bão hòa 255 theo quy tắc hàm phân tách sau:

$$\begin{aligned}
A'(x_i, y_i) &= 253, && \text{if the pixel does not contain data} \\
A'(x_i, y_i) &= 254, && \text{if embedding bit } b_i = 0 \\
A'(x_i, y_i) &= 255, && \text{if embedding bit } b_i = 1
\end{aligned}$$

Sau khi nhúng, mô hình biểu diễn của ảnh đã mã hóa trở thành $I'_{\text{encoded}}(x, y) = [R(x, y), G(x, y), B(x, y), A'(x, y)]$. Dung lượng giấu tin cực đại $C$ tính bằng bit trên một thực thể ảnh tuần theo giới hạn hình học $C = H \times W \quad (\text{bits})$.
