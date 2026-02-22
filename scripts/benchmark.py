import sys
import time
import secrets
import json
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.crypto.vault_cipher import derive_keys, encrypt_vault, decrypt_vault

def benchmark_kdf(iterations_list, password="master_password", salt=b"fixed_salt_16byte"):
    results = []
    print(f"{'Iterations':<15} | {'Time (ms)':<10}")
    print("-" * 30)
    
    for i in iterations_list:
        start_time = time.perf_counter()
        
        # 1. Derive Keys with explicit iteration count
        aes_key, hmac_key = derive_keys(password, salt, iterations=i)
        
        # 2. Encrypt & Authenticate
        data = {"test": "data" * 10}
        plaintext = json.dumps(data).encode()
        iv, mac_tag, ciphertext = encrypt_vault(plaintext, aes_key, hmac_key)
        
        # 3. Verify & Decrypt
        decrypt_vault(ciphertext, iv, mac_tag, aes_key, hmac_key)
        
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        results.append(duration_ms)
        print(f"{i:<15,} | {duration_ms:<10.2f}")
    
    return results

def plot_results(iterations, times):
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, times, marker='o', linestyle='-', color='r')
    plt.xscale('log')
    plt.xlabel('Number of Iterations (log scale)')
    plt.ylabel('Time (ms)')
    plt.title('Modular Crypto Pipeline Performance')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    # Annotate points
    for i, txt in enumerate(times):
        plt.annotate(f"{txt:.1f}ms", (iterations[i], times[i]), textcoords="offset points", xytext=(0,10), ha='center')
        
    plt.savefig('kdf_benchmark_results.png')
    print("\nUpdated chart saved as 'kdf_benchmark_results.png'")

if __name__ == "__main__":
    test_iterations = [1000, 10000, 100000, 400000, 1000000]
    print("Starting Modular Crypto Pipeline Benchmark...\n")
    times = benchmark_kdf(test_iterations)
    
    try:
        plot_results(test_iterations, times)
    except Exception as e:
        print(f"\nPlotting failed: {e}")
