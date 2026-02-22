# Tài liệu: Áp dụng kiến thức từ Slide vào Project Password Manager

Dưới đây là bảng đối chiếu giữa lý thuyết trong các Session slides của giảng viên và các cải tiến thực tế đã được áp dụng vào codebase mới.

---

## 1. Đối chiếu Lý thuyết & Thực hành

| Session | Chủ đề Slide | Kiến thức áp dụng | Vị trí trong Code / Thực nghiệm |
| :--- | :--- | :--- | :--- |
| **Session 4** | Symmetric Cryptography | **Mã hóa AES**: Sử dụng AES-256 thông qua Fernet. | Class `VaultManager`, hàm `save()` và `unlock()`. |
| **Session 4** | Operation Modes | **Lựa chọn Mode**: Giải thích tại sao dùng AES-CBC (hoặc GCM) tốt hơn AES-ECB. | [Stage 1] trong pipeline thực nghiệm. |
| **Session 7** | Hash Function | **Salt (Muối)**: Chuyển từ "Static Salt" (tên vault) sang "Random Salt" (16 bytes ngẫu nhiên). | Class `VaultManager`, hàm `create()`: `secrets.token_bytes(16)`. |
| **Session 7** | Hash Function | **Collision Resistance**: Giải thích tại sao Master Password cần có entropy cao để tránh trùng lập hash. | [Stage 4] trong pipeline thực nghiệm. |
| **Session 8** | MACs & HMAC | **Integrity (Tính toàn vẹn)**: Fernet tự động đính kèm HMAC để phát hiện file bị sửa đổi. | Hàm `unlock()`: Bắt lỗi `InvalidToken` chính là bắt lỗi sai HMAC. |
| **Session 8** | Key Establishment | **PBKDF2 (KDF)**: Sử dụng hàm băm lặp đi lặp lại để "kéo dài" mật khẩu yếu thành key mạnh. | Hàm `derive_key()`: Sử dụng `PBKDF2HMAC` với SHA256. |
| **Session 8** | Key Freshness | **Iteration Count**: Phân tích số vòng lặp tối ưu ($10^6$) để chống brute-force. | Script `benchmark.py` dùng để đo hiệu năng thực tế. |

---

## 2. Chi tiết các cải tiến so với bản "cũ"

### A. Cơ chế quản lý Salt (Slide Session 7)
*   **Cũ**: Dùng tên vault làm salt. Điều này vi phạm tính ngẫu nhiên, nếu 2 người đặt tên vault giống nhau và mật khẩu giống nhau thì key sẽ giống hệt nhau.
*   **Mới**: Mỗi vault khi tạo ra sẽ sinh 16 bytes ngẫu nhiên bằng `secrets.token_bytes(16)`. Salt này được ghi vào **đầu file** mã hóa. Khi giải mã, code sẽ đọc 16 bytes đầu tiên này để làm salt.
*   **Ý nghĩa**: Tuân thủ nguyên tắc "Unique Salt" trong Slide Session 7.

### B. Cơ chế Key Stretching (Slide Session 8)
*   **Cũ**: Code gọi PBKDF2 một cách cứng nhắc.
*   **Mới**: Tách riêng hàm `derive_key` và xây dựng script `benchmark.py` để chứng minh lý thuyết về **Work Factor**.
*   **Ý nghĩa**: Giúp nhóm có số liệu thực nghiệm để giải thích trong báo cáo về việc đánh đổi giữa *Bảo mật (Số vòng lặp)* và *UX (Thời gian chờ)*.

### C. Tính Toàn vẹn - Integrity (Slide Session 8)
*   **Cũ**: Chỉ đơn giản là bắt lỗi giải mã chung chung.
*   **Mới**: Giải thích rõ cơ chế của `Fernet` là sự kết hợp của AES-CBC và **HMAC**.
*   **Ý nghĩa**: Khi giải thích UML hoặc trả lời câu hỏi giảng viên, nhóm có thể tự tin nói rằng hệ thống đạt được cả 2 mục tiêu: **Confidentiality** (Bảo mật) và **Integrity** (Toàn vẹn).

---

## 3. Hướng dẫn sử dụng tài liệu này
Nhóm có thể copy bảng ở Mục 1 để làm phần **"Mapping Theory to Implementation"** trong báo cáo. Các mục A, B, C ở Mục 2 dùng để viết phần **"Design Decisions"** hoặc **"Security Analysis"**.