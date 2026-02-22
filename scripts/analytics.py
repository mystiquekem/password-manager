import math
import secrets
import json
import sys
import statistics
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.crypto.vault_cipher import derive_keys, encrypt_vault

def calculate_entropy(data):
    if not data:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

def hamming_distance(chaine1, chaine2):
    return sum(bin(byte1 ^ byte2).count('1') for byte1, byte2 in zip(chaine1, chaine2))

def bytes_to_bit_array(data):
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return np.array(bits)

def visualize_bitmaps(c1, c2, diff_only=False):
    """Visualize ciphertexts as bit maps and their differences."""
    b1 = bytes_to_bit_array(c1)
    b2 = bytes_to_bit_array(c2)
    
    # Ensure they are the same length for visualization
    min_len = min(len(b1), len(b2))
    b1, b2 = b1[:min_len], b2[:min_len]
    
    # Reshape for visualization (try to make it roughly square)
    side = int(math.sqrt(min_len))
    if side == 0: return
    plot_len = side * side
    
    m1 = b1[:plot_len].reshape((side, side))
    m2 = b2[:plot_len].reshape((side, side))
    diff = (b1[:plot_len] ^ b2[:plot_len]).reshape((side, side))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].imshow(m1, cmap='Greys', interpolation='nearest')
    axes[0].set_title("Ciphertext A (Bit Map)")
    axes[0].axis('off')
    
    axes[1].imshow(m2, cmap='Greys', interpolation='nearest')
    axes[1].set_title("Ciphertext B (Bit Map)")
    axes[1].axis('off')
    
    axes[2].imshow(diff, cmap='Reds', interpolation='nearest')
    axes[2].set_title("Difference Map (XOR)")
    axes[2].axis('off')
    
    plt.tight_layout()
    output_png = root_dir / 'figure' / 'figure_6_statistical_diffusion.png'
    plt.savefig(output_png)
    print(f"Visualization saved to {output_png}")

def run_analytics(trials=100):
    results = []
    results.append("# Báo cáo Phân tích Định lượng & Hình ảnh (Security Analytics & Visualization)")
    results.append(f"Statistical analysis performed over {trials} random trials.\n")

    # 1. Statistical Entropy Analysis
    results.append("## 1. Phân tích Entropy Trung bình (Average Entropy)")
    search_dirs = [root_dir / "vaults", root_dir / "hex_samples"]
    vault_files = []
    for sd in search_dirs:
        if sd.exists():
            vault_files.extend(list(sd.glob("*.enc")))
    
    entropies = []
    if vault_files:
        for vf in vault_files:
            with open(vf, "rb") as f:
                content = f.read()
                ent = calculate_entropy(content)
                entropies.append(ent)
        
        avg_ent = statistics.mean(entropies)
        std_ent = statistics.stdev(entropies) if len(entropies) > 1 else 0
        results.append(f"*   **Số lượng file phân tích**: `{len(vault_files)}`")
        results.append(f"*   **Entropy Trung bình**: `{avg_ent:.4f}` bits/byte")
        results.append(f"*   **Độ lệch chuẩn (STDEV)**: `{std_ent:.4f}`")
    else:
        results.append("*Không tìm thấy file vault nào để phân tích.*")

    # 2. Statistical Avalanche Effect (Multi-trial)
    results.append("\n## 2. Hiệu ứng Thác đổ Thống kê (Statistical Avalanche Effect)")
    
    avalanche_values = []
    
    # Store one pair for visualization
    viz_pair = None

    for i in range(trials):
        rand_pass = secrets.token_hex(16)
        rand_salt = secrets.token_bytes(16)
        aes_key, hmac_key = derive_keys(rand_pass, rand_salt, iterations=100)

        # Use larger plaintexts for better visualization
        base_plaintext = secrets.token_bytes(128) 
        byte_idx = secrets.randbelow(len(base_plaintext))
        bit_idx = secrets.randbelow(8)
        modified_list = list(base_plaintext)
        modified_list[byte_idx] ^= (1 << bit_idx)
        modified_plaintext = bytes(modified_list)
        
        iv1, mac1, c1 = encrypt_vault(base_plaintext, aes_key, hmac_key)
        iv2, mac2, c2 = encrypt_vault(modified_plaintext, aes_key, hmac_key)
        
        min_len = min(len(c1), len(c2))
        hd = hamming_distance(c1[:min_len], c2[:min_len])
        total_bits = min_len * 8
        avalanche_values.append((hd / total_bits) * 100)
        
        if i == 0:
            viz_pair = (c1, c2)

    avg_avalanche = statistics.mean(avalanche_values)
    std_avalanche = statistics.stdev(avalanche_values)
    
    results.append(f"*   **Avalanche Effect Trung bình**: `{avg_avalanche:.2f}%` (Lý tưởng: 50%)")
    results.append(f"*   **Độ lệch chuẩn (STDEV)**: `±{std_avalanche:.2f}%`")
    
    # 3. Visualization section in markdown
    results.append("\n## 3. Minh chứng Hình ảnh (Cryptographic Visualization)")
    results.append("![Statistical Diffusion Proof](../figure/figure_6_statistical_diffusion.png)")
    results.append("\n**Giải thích hình ảnh**:")
    results.append("*   **Ciphertext A/B**: Bản đồ bit của 2 vault có nội dung gốc chỉ khác nhau 1 bit. Bạn có thể thấy chúng trông như nhiễu trắng (vô trị), không có pattern.")
    results.append("*   **Difference Map**: Kết quả XOR giữa 2 bản mã. Màu đỏ bao phủ ~50% diện tích cho thấy sự thay đổi lan tỏa (Diffusion) toàn bộ file thay vì chỉ khu biệt ở 1 block.")

    # Run visualization
    if viz_pair:
        visualize_bitmaps(viz_pair[0], viz_pair[1])

    # Save to file
    output_path = root_dir / "docs" / "analytics_results.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    
    print(f"Analytics & Visualization complete. Results saved to {output_path}")

if __name__ == "__main__":
    run_analytics(trials=100)
