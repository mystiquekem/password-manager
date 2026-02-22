# Secure Vault Manager - Introduction to Cryptography Project

Dự án này là lõi hệ thống quản lý mật khẩu được thiết kế để minh họa các khái niệm cốt lõi trong môn học **Nhập môn Mật mã (Introduction to Cryptography)**. Thay vì sử dụng các thư viện "black-box" cao cấp, project này triển khai tường minh các cơ chế mã hóa và xác thực tầng thấp để phục vụ mục đích học thuật và báo cáo.

---

## 🏛 Cấu trúc Thư mục (Project Architecture)

Project được tổ chức theo mô hình Modular để tách biệt rõ ràng giữa giao diện, nghiệp vụ và lõi mật mã:

```text
password-manager/
├── src/
│   ├── crypto/
│   │   └── vault_cipher.py   <-- [LÕI MẬT MÃ] Chứa AES-CBC, HMAC, PKCS7, PBKDF2
│   ├── core/
│   │   ├── config.py         <-- [CẤU HÌNH] Chứa các hằng số (Iterations, Salt size...)
│   │   └── vault_manager.py  <-- [LOGIC] Quản lý lưu trữ file và dữ liệu JSON
│   └── ui/
│       └── app_window.py     <-- [GIAO DIỆN] Sử dụng Tkinter/TTK
├── main.py                   <-- [ENTRYPOINT] Điểm khởi chạy ứng dụng
├── benchmark.py              <-- [THỰC NGHIỆM] Script đo hiệu năng KDF
├── docs/                     <-- Tài liệu hướng dẫn báo cáo và pipeline
└── pyproject.toml            <-- Quản lý dependency bằng uv
```

---

## 🔐 Thiết kế Hệ mật (Cryptographic Design Patterns)

Hệ thống áp dụng các Design Patterns chuẩn trong mật mã học (đối chiếu với Slide bài giảng):

1.  **Key Stretching (Session 8)**: Sử dụng **PBKDF2-HMAC-SHA256** với 390.000 vòng lặp để biến Master Password thành khóa 32-byte. Khóa này sau đó được **tách đôi (Key Splitting)**: 16-byte cho mã hóa và 16-byte cho xác thực.
2.  **Authenticated Encryption (Session 4 & 8)**: Áp dụng mô hình **Encrypt-then-MAC**. Dữ liệu được mã hóa bằng **AES-128-CBC** trước, sau đó mới tính toán **HMAC-SHA256** trên bản mã để đảm bảo tính toàn vẹn (Integrity).
3.  **Unique salts (Session 7)**: Mỗi Vault được tạo ra với một **16-byte Salt ngẫu nhiên** riêng biệt, giúp chống lại tấn công Rainbow Table.
4.  **Deterministic vs Non-deterministic**: Sử dụng **Random IV (128-bit)** cho mỗi lần lưu file, đảm bảo cùng một nội dung lưu lại nhiều lần sẽ cho ra bản mã hoàn toàn khác nhau.

---

## 🚀 Cài đặt và Chạy ứng dụng

Dự án này sử dụng công cụ quản lý package hiện đại `uv` để tối ưu hóa hiệu năng và môi trường.

### 1. Cài đặt `uv` (Nếu chưa có)
Trên macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Hoặc dùng Homebrew: `brew install uv`

Trên Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Kéo code về và Cài đặt môi trường
Sau khi đã có code trong máy, hãy thực hiện:
```bash
# Di chuyển vào thư mục project
cd password-manager

# Tự động tạo venv và cài đặt mọi dependency (cryptography, matplotlib)
uv sync
```

### 3. Chạy ứng dụng
Để khởi động giao diện quản lý mật khẩu:
```bash
uv run main.py
```

### 4. Chạy thực nghiệm (Benchmark)
Để lấy số liệu Iterations vs Time phục vụ báo cáo:
```bash
uv run benchmark.py
```

---

## 📊 Phân tích Thực nghiệm
Dự án bao gồm script `benchmark.py` giúp tạo ra file biểu đồ `kdf_benchmark_results.png`. Biểu đồ này phân tích sự đánh đổi (Trade-off) giữa tính bảo mật (số vòng lặp KDF) và trải nghiệm người dùng (Work Factor), một phần quan trọng trong yêu cầu của môn học.

---
**Nhóm thực hiện**: [Tên nhóm của bạn]
**Môn học**: Introduction to Cryptography
