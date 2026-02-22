import time
import secrets
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import matplotlib.pyplot as plt

def benchmark_kdf(iterations_list, password="master_password", salt=b"fixed_salt_16byte"):
    results = []
    print(f"{'Iterations':<15} | {'Time (ms)':<10}")
    print("-" * 30)
    
    for i in iterations_list:
        start_time = time.perf_counter()
        
        # 1. PBKDF2 Key Derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=i,
        )
        full_key = kdf.derive(password.encode())
        aes_key = full_key[:16]
        hmac_key = full_key[16:]
        
        # 2. Simulated AES-CBC + HMAC (matching password-manager.py)
        data = {"test": "data" * 10}
        plaintext = json.dumps(data).encode()
        
        # Padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        # Encrypt
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # HMAC
        h = hmac.HMAC(hmac_key, hashes.SHA256())
        h.update(ciphertext)
        h.finalize()
        
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
    plt.title('Explicit Crypto Pipeline Performance vs. Iterations')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    
    # Annotate points
    for i, txt in enumerate(times):
        plt.annotate(f"{txt:.1f}ms", (iterations[i], times[i]), textcoords="offset points", xytext=(0,10), ha='center')
        
    plt.savefig('kdf_benchmark_results.png')
    print("\nUpdated chart saved as 'kdf_benchmark_results.png'")

if __name__ == "__main__":
    test_iterations = [1000, 10000, 100000, 400000, 1000000]
    print("Starting Explicit Crypto Pipeline Benchmark...\n")
    times = benchmark_kdf(test_iterations)
    
    try:
        plot_results(test_iterations, times)
    except Exception as e:
        print(f"\nPlotting failed: {e}")
