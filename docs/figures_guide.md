# Các Loại Biểu Đồ & Hình Ảnh Cần Thiết Cho Báo Cáo Crypto

Để báo cáo đạt điểm cao và thể hiện đúng tính chất của môn Nhập môn Mật mã (Introduction to Cryptography), hệ thống báo cáo của nhóm **BẮT BUỘC** phải có các Figure sau đây. Những Figure này minh họa chính xác cấu trúc code *mới nhất* của nhóm: tách biệt hoàn toàn module và tự code các primitive (AES, HMAC, PBKDF2).

---

## 1. Dòng chảy Mật mã (Cryptographic Flow Diagram)

Đây là biểu đồ quan trọng nhất môn học để chứng minh nhóm hiểu lý thuyết. Gồm 2 phần chính tương ứng với hàm `encrypt_vault` và `decrypt_vault` trong file `src/crypto/vault_cipher.py`.

### Figure 1.A: Sơ đồ Mã hóa (Encryption Flow)
*   **Mục đích**: Giải thích sơ đồ tạo khóa từ Master Password và luồng mã hóa Encrypt-then-MAC.
*   **Điểm tương ứng trong code**: `src/crypto/vault_cipher.py` $\rightarrow$ hàm `derive_keys` và `encrypt_vault`.
*   **Nội dung vẽ (Flowchart)**:
    1.  `Master Password` + `Random Salt (16 bytes)` $\longrightarrow$ `PBKDF2-HMAC-SHA256 (390k iterations)` $\longrightarrow$ **Key (32 bytes)**.
    2.  Tách 32 bytes Key ra: 16 bytes dùng làm `AES_Key`, 16 bytes dùng làm `HMAC_Key`.
    3.  `Plaintext (JSON)` + `PKCS7 Padding` $\longrightarrow$ `AES-128 (CBC mode)` + `IV (16 bytes random)` $\longrightarrow$ **Ciphertext**.
    4.  `Ciphertext` $\longrightarrow$ đưa vào băm `HMAC-SHA256` (dùng `HMAC_Key`) $\longrightarrow$ **MAC tag** (32 bytes).
    5.  Nối các phần lại: `[Salt] + [IV] + [MAC] + [Ciphertext]` $\longrightarrow$ Ghi ra file `.enc`.

### Figure 1.B: Sơ đồ Giải mã & Xác thực (Decryption & Verification Flow)
*   **Mục đích**: Giải thích cách hệ thống phát hiện file bị sửa đổi (đảm bảo Integrity).
*   **Điểm tương ứng trong code**: `src/crypto/vault_cipher.py` $\rightarrow$ hàm `decrypt_vault`.
*   **Nội dung vẽ (Flowchart)**:
    1.  Đọc file `.enc`: Tách lấy `[Salt]`, `[IV]`, `[MAC_Stored]`, và `[Ciphertext]`.
    2.  `Master Password` + `[Salt]` $\longrightarrow$ Tính lại **Key 32 bytes** $\longrightarrow$ Tách ra `AES_Key` và `HMAC_Key`.
    3.  Lấy `[Ciphertext]` đưa qua `HMAC-SHA256` (dựa trên `HMAC_Key`) để tính ra `MAC_Calculated`.
    4.  So sánh: `MAC_Calculated` == `[MAC_Stored]`?
        *   Nếu **Khác nhau**: Trả về Lỗi toàn vẹn (Integrity Error) $\longrightarrow$ Vứt bỏ, từ chối giải mã nội dung.
        *   Nếu **Giống nhau**: Đưa `[Ciphertext]` + `[IV]` qua `AES-128 (CBC mod)` $\longrightarrow$ Xóa `PKCS7 Padding` $\longrightarrow$ Trả về **Plaintext** (JSON an toàn).

---

## 2. Thiết kế Cấu trúc Dữ liệu (Data Structure Diagram)

### Figure 2: Cấu trúc File Vault (Vault File Format)
*   **Mục đích**: Lấy điểm phần Session 7 và 8.
*   **Nội dung vẽ (Block Diagram)**: Vẽ một dải bộ nhớ chia làm 4 khối, giống y hệt lúc nối file trong code:
    *   Khối 1: `Salt` (16 bytes, Random, Không mã hóa). Lý do: Để tái tạo Khóa mà không bị tấn công Rainbow Table đa file.
    *   Khối 2: `IV` (16 bytes, Random, Không mã hóa). Lý do: Yêu cầu bắt buộc của Mode AES-CBC.
    *   Khối 3: `HMAC_Tag` (32 bytes). Lý do: Bảo vệ toàn vẹn cho dữ liệu ở khối 4.
    *   Khối 4: `Encrypted Data` (Tùy biến độ dài, Mã hóa bằng AES-CBC).

---


---

## 3. Bằng chứng Thực nghiệm (Bắt buộc)

### Figure 3: Biểu đồ Đánh giá Trade-off Kích thước/Thời gian (KDF Benchmark)
*   **Nội dung**: Chèn file ảnh `kdf_benchmark_results.png` đã được sinh ra bởi file `benchmark.py`.
*   **Giải thích trong báo cáo**: Phân tích sự cân bằng giữa số vòng lặp PBKDF2 (Tính an toàn chống brute-force) và thời gian thực thi thuật toán (Trải nghiệm người dùng) $\rightarrow$ Chọn điểm $N=390.000$ (tốn ~75ms).

### Figure 5: Hex Dump (Confusion & Diffusion)
*   **Cách làm**: Mở file `.enc` trong thư mục `vaults/` bằng lệnh `hexdump -C vaults/<tên file>.enc` hoặc màn hình Notepad++ dạng Hex. Chụp một bức ảnh mớ bòng bong đó.
*   **Trình bày**: Cho thấy dù tạo 2 Vault có mật khẩu và nội dung y hệt nhau, file kết quả vẫn không thể đoán trước được nhờ sức mạnh của CSPRNG Salt và Random IV.
