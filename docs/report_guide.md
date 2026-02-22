# Hướng Dẫn Viết Báo Cáo Môn Introduction to Cryptography

Báo cáo cho môn Mật mã học (Introduction to Cryptography) cần tập trung vào **cơ sở lý thuyết toán học/mật mã**, **cách thức áp dụng thuật toán**, và **phân tích an toàn**, thay vì sa đà vào cấu trúc code (Code Structure) hay các module phần mềm thông thường.

Dưới đây là Outline chuẩn học thuật theo best practice dành cho project "Design and Implementation of a Secure Password Manager with Explicit Cryptographic Primitives":

---

## Chương 1: Introduction (Giới thiệu)
*   **Bối cảnh (Context)**: Tầm quan trọng của Password Manager trong thời đại số. Đây là một chủ đề điển hình để áp dụng các kiến thức về an toàn thông tin và mật mã học vào thực tế.
*   **Vấn đề (Problem Statement)**: Nguy cơ từ việc lưu trữ mật khẩu không an toàn. Sự cần thiết của việc hiểu rõ các cơ chế bảo vệ dữ liệu ở mức độ primitives thay vì chỉ sử dụng các thư viện black-box (thư viện đóng gói sẵn không rõ cơ chế bên trong).
*   **Mục tiêu học tập & Đề tài (Objectives)**: 
    *   **Áp dụng lý thuyết**: Vận dụng các nguyên thủy mật mã (Cryptographic Primitives) đã học như AES, HMAC, PBKDF2 để xây dựng một giải pháp lưu trữ an toàn.
    *   **Thực thi "White-box"**: Xây dựng hệ thống một cách tường minh, cho phép kiểm soát và hiểu rõ từng bước của luồng xử lý dữ liệu (Encryption Pipeline).
    *   **Đánh giá & Phân tích**: Thực hành đánh giá tính an toàn và hiệu năng của hệ thống dựa trên các tiêu chuẩn quốc tế (NIST, FIPS), từ đó củng cố kiến thức chuyên môn.
    *   **Kỹ năng triển khai**: Hoàn thiện kỹ năng lập trình an toàn (Secure Coding) và tư duy thiết kế hệ thống có tính bảo mật cao.

## Chương 2: Theoretical Background (Cơ sở Lý thuyết)
*Đây là chương quan trọng nhất để chứng minh kiến thức môn học. Bạn cần trình bày lý thuyết nền tảng dựa trên các tiêu chuẩn và nghiên cứu uy tín.*

### 2.1. Symmetric-key Encryption (Mã hóa khóa đối xứng)
*   **Tiêu chuẩn AES**: Giới thiệu thuật toán Rijndael theo tiêu chuẩn **FIPS PUB 197** [2]. Giải thích cấu trúc SPN (Substitution-Permutation Network).
*   **Chế độ vận hành (Block Cipher Modes)**:
    *   Dựa trên **NIST SP 800-38A** [3], trình bày cơ chế CBC (Cipher Block Chaining).
    *   Lý do chọn CBC so với ECB: IV (Initialization Vector) đảm bảo "semantic security" (tính bí mật ngữ nghĩa), giúp che giấu các mẫu dữ liệu lặp lại.
*   **Cơ chế đệm**: Sử dụng PKCS#7 (RFC 2315) để đảm bảo dữ liệu đầu vào là bội số của block size (16 bytes).

### 2.2. Key Derivation Functions (Hàm dẫn xuất khóa)
*   **Vấn đề Shannon Entropy**: Giải thích lý do mật khẩu người dùng (low entropy) không thể dùng trực tiếp làm khóa (theo **NIST SP 800-132** [4]).
*   **Giải thuật PBKDF2**:
    *   Tham chiếu **RFC 2898 (PKCS #5)** [5].
    *   **Iteration Count**: Cơ chế stretching để chống tấn công Brute-force/Dictionary offline.
    *   **Salt**: Sử dụng Salt ngẫu nhiên (tối thiểu 128 bit theo SP 800-132) để kháng tấn công Rainbow Tables bằng cách tạo ra các hash space riêng biệt cho cùng một mật khẩu.

### 2.3. Authenticated Encryption (Mã hóa xác thực)
*   **Tính toàn vẹn (Integrity)**: Thuật toán HMAC-SHA256 dựa trên tiêu chuẩn **FIPS 198-1** [1].
*   **Generic Composition Paradigm**: Phân tích 3 mô hình từ nghiên cứu của **Bellare & Namprempre (2000)** [6] và **Hugo Krawczyk (2001)** [7]:
    *   *Encrypt-and-MAC (E&M)*: Dùng trong SSH.
    *   *MAC-then-Encrypt (MtE)*: Dùng trong SSL/TLS.
    *   *Encrypt-then-MAC (EtM)*: Dùng trong IPsec.
*   **Lựa chọn EtM**: Chứng minh tại sao EtM là mô hình duy nhất đạt được tính an toàn cao nhất (**INT-CTXT** - Integrity of Ciphertexts) và kháng được các cuộc tấn công như Padding Oracle, thay vì MtE (mô hình của SSL) vốn đã bị chứng minh là yếu hơn về mặt lý thuyết bởi Krawczyk.

---
## Danh mục Tài liệu Tham khảo (Citations)
[1] NIST (2008). *FIPS 198-1: The Keyed-Hash Message Authentication Code (HMAC)*.
[2] NIST (2001). *FIPS 197: Advanced Encryption Standard (AES)*.
[3] NIST (2001). *SP 800-38A: Recommendation for Block Cipher Modes of Operation*.
[4] NIST (2010). *SP 800-132: Recommendation for Password-Based Key Derivation*.
[5] IETF (2000). *RFC 2898: PKCS #5: Password-Based Cryptography Specification Version 2.0*.
[6] M. Bellare & C. Namprempre (2000/2007). *Authenticated Encryption: Relations among notions and analysis of the generic composition paradigm*.
[7] Hugo Krawczyk (2001). *The Order of Encryption and Authentication for Protecting Communications (Or: How Secure is SSL?)*.

## Chương 3: Methodology (Kiến trúc Mật mã & Triển khai)
*Chương này mô tả cách bạn áp dụng lý thuyết ở Chương 2 vào luồng hoạt động của ứng dụng. Tuyệt đối không nhúng code structure (file/folder) vào đây.*
*   **3.1. Cryptographic Pipeline (Luồng Mật mã học)**:
    *   Sơ đồ tổng quan (Flowchart) quá trình từ Master Password -> PBKDF2 -> Tách khóa (AES Key & HMAC Key).
        *Gợi ý: Chèn hình `figure/figure_1a_encryption_flow.png` và `figure/figure_1b_decryption_flow.png` vào đây để minh họa.*
    *   **Biện minh thiết kế**: Giải thích tại sao việc tách khóa (Key Splitting) là cần thiết để đảm bảo tính độc lập giữa mã hóa và xác thực theo khuyến nghị của **Bellare & Namprempre** [6].
    *   Quá trình mã hóa (Encryption phase): Sinh IV ngẫu nhiên, padding, AES-CBC.
    *   Quá trình xác thực (Authentication phase): Sinh MAC tag từ Ciphertext và IV (Mô hình EtM).
*   **3.2. Vault Data Structure (Cấu trúc dữ liệu mã hóa)**:
    *   Định dạng file nhị phân đầu ra: `[16-byte Salt] + [16-byte IV] + [32-byte MAC] + [Ciphertext]`.
        *Gợi ý: Chèn hình `figure/figure_2_file_format.png` vào phần này để minh họa trực quan cấu trúc file.*
    *   **Tuân thủ tiêu chuẩn**: Cấu trúc này tuân thủ **NIST SP 800-132 (Section 5.4 - Option 2)** [4] về việc lưu trữ các tham số dẫn xuất khóa (Salt) và dữ liệu bảo vệ (IV, MAC) cùng với bản mã.
    *   Quy trình nạp thẻ và giải mã an toàn (Xác thực MAC trước khi giải mã để tránh rò rỉ thông tin qua lỗi giải mã).

## Chương 4: Results, Benchmarks & Security Analysis (Đánh giá và Phân tích an toàn)
*   **4.1. KDF Benchmarking**:
    *   Đo đạc thời gian trễ của PBKDF2 với các giá trị iteration khác nhau.
    *   Trình bày đồ thị Latency vs Iterations.
    *   **Lý giải (Justification)**: Dựa trên khuyến nghị của **NIST SP 800-132 (Section 5.2)** [4], giải thích việc chọn số vòng lặp đủ lớn để tăng chi phí tấn công offline ròng (Work Factor) trong khi vẫn đảm bảo trải nghiệm người dùng (Latency < 1s).
*   **4.2. Security Proofs / Attack Resistance (Phân tích Kháng tấn công)**:
    *   *Brute-force Offline*: Hiệu quả bị triệt tiêu bởi cơ chế "key stretching" của PBKDF2 (**RFC 2898** [5]).
    *   *Rainbow Table / Dictionary Attack*: Bị ngăn chặn hoàn toàn bởi Salt ngẫu nhiên (tối thiểu 128 bit theo **SP 800-132** [4]).
    *   *Statistical Patterns*: Chặn bởi AES-CBC kết hợp Random IV. Tính chất khuếch tán (Cryptographic Diffusion) được chứng minh thông qua sự thay đổi hoàn toàn của bản mã dù bản tin gốc chỉ khác biệt 1 bit (**FIPS 197** [2]).
        *Gợi ý: Chèn hình `figure/figure_5a_hex_map.png`, `figure/figure_5b_hex_map.png` và `figure/figure_6_statistical_diffusion.png` vào đây để chứng minh.*
    *   *Data Tampering / Integrity Attacks*: Nhờ mô hình Encrypt-then-MAC, mọi nỗ lực sửa đổi dữ liệu trái phép đều bị phát hiện ở tầng HMAC mà không cần giải mã. Đây là ưu thế vượt trội về mặt lý thuyết so với các lỗi bảo mật của SSL/TLS khi sử dụng MtE (**Hugo Krawczyk** [7]).

## Chương 5: Conclusion (Kết luận)
*   Tóm tắt những giá trị thực tiễn hệ thống đạt được (áp dụng thành công các nguyên thủy mật mã cơ bản để xây dựng hệ thống an toàn).
*   Những hướng phát triển (VD: Đổi sang Argon2id kháng GPU, thêm mã hóa bảo vệ bộ nhớ RAM).

---
**Lưu ý quan trọng cho nhóm viết báo cáo**:
1. KHÔNG dán cấu trúc thư mục (`tree /src`) vào báo cáo.
2. KHÔNG dán code thuần Python vào. Nếu cần mô tả thuật toán, hãy dùng **Mã giả (Pseudocode)** hoặc trình bày bằng các phương trình toán học/sơ đồ khối.
3. Mọi công cụ, tham số (như AES-128, SHA-256) phải có lý do (Justification) rõ ràng dưa trên kiến thức đã học.
