import secrets
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from src.core.config import KDF_ITERATIONS

def derive_keys(password: str, salt: bytes, iterations: int = KDF_ITERATIONS):
    """[Session 8] Key Derivation & Stretching"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # 16 for AES + 16 for HMAC
        salt=salt,
        iterations=iterations,
    )
    full_key = kdf.derive(password.encode())
    # [Pipeline Stage 2] Tách Khóa: 16b AES Key + 16b HMAC Key
    return full_key[:16], full_key[16:]

def encrypt_vault(data_bytes: bytes, aes_key: bytes, hmac_key: bytes):
    """[Session 4 & 8] Explicit Encryption & Authentication"""
    # 1. [Session 4] Add PKCS7 Padding
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()

    # 2. [Session 4] Encryption: AES-128-CBC with Random IV
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # 3. [Session 8] Tính toán HMAC-SHA256 (Encrypt-then-MAC)
    h = hmac.HMAC(hmac_key, hashes.SHA256())
    h.update(ciphertext)
    mac_tag = h.finalize()

    return iv, mac_tag, ciphertext

def decrypt_vault(ciphertext: bytes, iv: bytes, stored_mac: bytes, aes_key: bytes, hmac_key: bytes):
    """[Session 4 & 8] Explicit Authentication & Decryption"""
    # 1. [Session 8] Integrity Check: Verify HMAC
    h = hmac.HMAC(hmac_key, hashes.SHA256())
    h.update(ciphertext)
    h.verify(stored_mac) # Throws exclusion if mismatch

    # 2. [Session 4] Decryption: AES-128-CBC
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    # 3. [Session 4] Remove PKCS7 Padding
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()
