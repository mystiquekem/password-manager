# Các Loại Biểu Đồ & Hình Ảnh Cần Thiết Cho Báo Cáo Crypto

Để báo cáo đạt điểm cao và thể hiện đúng tính chất của môn Nhập môn Mật mã (Introduction to Cryptography), ngoài biểu đồ Benchmark (đánh giá hiệu năng) đã có, hệ thống báo cáo của nhóm **BẮT BUỘC** phải có các Figure sau đây. Những Figure này giúp rạch ròi giữa việc "chỉ import thư viện" và việc "hiểu rõ kiến trúc mật mã bên dưới."

---

## 1. Dòng chảy Mật mã (Cryptographic Flow Diagram)

Đây là biểu đồ quan trọng nhất môn học để chứng minh nhóm hiểu lý thuyết.

### Figure 1.A: Sơ đồ Mã hóa (Encryption Flow)
*   **Mục đích**: Giải thích sơ đồ tạo khóa từ Master Password và luồng mã hóa Encrypt-then-MAC.
*   **Nội dung vẽ (Flowchart)**:
    1.  `Master Password` + `Random Salt (16 bytes)` $\longrightarrow$ `PBKDF2-HMAC-SHA256 (390k iterations)` $\longrightarrow$ **Key (32 bytes)**.
    2.  Tách 32 bytes Key ra: 16 bytes dùng làm `AES_Key`, 16 bytes dùng làm `HMAC_Key`.
    3.  `Plaintext (JSON)` + `Padding` $\longrightarrow$ `AES-128 (CBC mode)` + `IV (16 bytes random)` $\longrightarrow$ **Ciphertext**.
    4.  `Ciphertext` $\longrightarrow$ `HMAC-SHA256` (dùng `HMAC_Key`) $\longrightarrow$ **MAC tag**.
    5.  Nối các phần lại: `[Salt] + [IV] + [MAC] + [Ciphertext]` $\longrightarrow$ Ghi ra file `.enc`.
*   *(Biểu đồ này tương đương với các sơ đồ "Key Generation" và "Block Cipher" trong Slide Session 4 và 8).*

### Figure 1.B: Sơ đồ Giải mã & Xác thực (Decryption & Verification Flow)
*   **Mục đích**: Giải thích cách hệ thống phát hiện file bị sửa đổi (đảm bảo Integrity).
*   **Nội dung vẽ (Flowchart)**:
    1.  Đọc file: Tách `[Salt]`, `[IV]`, `[MAC]`, và `[Ciphertext]`.
    2.  `Master Password` + `[Salt]` $\longrightarrow$ Tính lại **Key (32 bytes)** $\longrightarrow$ Tách ra `AES_Key` và `HMAC_Key`.
    3.  Lấy `[Ciphertext]` đưa qua `HMAC-SHA256` (dựa trên `HMAC_Key`) để tính ra `New_MAC`.
    4.  So sánh: `New_MAC` == `[MAC]` cũ?
        *   Nếu **False**: Trả về Lỗi toàn vẹn (Integrity Error / InvalidToken) $\longrightarrow$ Dừng giải mã.
        *   Nếu **True**: Đưa `[Ciphertext]` + `[IV]` qua `AES-128 (CBC mod)` $\longrightarrow$ Remove Padding $\longrightarrow$ Trả về **Plaintext**.

---

## 2. Thiết kế Cấu trúc Dữ liệu (Data Structure Diagram)

### Figure 2: Cấu trúc File Vault (Vault File Format)
*   **Mục đích**: Minhh họa cách các thành phần mật mã được lưu trữ trên ổ cứng vật lý.
*   **Nội dung vẽ (Block Diagram)**: Vẽ một hình chữ nhật dài chia làm 4 khúc:
    *   Khối 1: `Salt` (16 bytes, Random, Plaintext)
    *   Khối 2: `IV` (16 bytes, Random, Plaintext) - *(Do dùng AES-CBC cần IV)*
    *   Khối 3: `HMAC_Tag` (32 bytes, Hash) - đảm bảo Integrity.
    *   Khối 4: `Encrypted Data` (Độ dài tùy ý, AES-CBC Ciphertext).
*   **Lời bình**: Giải thích rằng Salt và IV không cần phải giấu (như Slide quy định), nhưng chúng cấm không được lặp lại.

---

## 3. System Design (Phần cứng & Kiến trúc - Môn SE)

### Figure 3: Biểu đồ Lớp (UML Class Diagram)
*   **Mục đích**: Minh chứng mã nguồn được tổ chức tốt.
*   **Nội dung vẽ (UML)**: (Giống mẫu tôi đã mớm ở file Code Review trước đó).
    *   Class `PasswordApp`: Xử lý giao diện (Tkinter), gọi các hàm từ VaultManager.
    *   Class `VaultManager`: Quản lý logic file I/O, đóng gói các logic khóa mã và dịch vụ. Chứa các tham số tĩnh cấu hình crypto.

---

## 4. Bằng chứng Thực nghiệm (Bắt buộc)

Ngoài cái Hình Benchmark tôi đã làm, các bạn CẦN CHỤP MÀN HÌNH các "Proof of concept":

### Figure 4: Hex Dump để thấy hiệu ứng Confusion/Diffusion
*   **Nội dung chụp**: Mở 2 cái file `.enc` được tạo ra bằng CÙNG MỘT MẬT KHẨU nhưng khác thời điểm (hoặc mở bằng Notepad++ / Hex Editor).
*   **Giải thích**: Dù mật khẩu giống nhau và Nội dung giống nhau, nhưng Ciphertext nhìn hoàn toàn khác biệt. Lý do: do **Random Salt** và **Random IV**. Điều này triệt tiêu hoàn toàn nhược điểm "Deterministic" của thuật toán (tương tự như công kích trong Session 4).

### Figure 5: Màn hình bắt lỗi "InvalidToken" (Chặn chỉnh sửa file)
*   **Nội dung chụp**: Bạn mở file `.enc` bằng Notepad, sửa bừa 1 ký tự, lưu lại. Xong mở App lên nhập đúng mật khẩu. App sẽ văng lỗi đỏ chót: "Invalid Master Password hoặc File Bị Hỏng".
*   **Giải thích**: Đây là bằng chứng sống động nhất cho cơ chế MAC (Message Authentication Code) đề cập trong Session 8.
