import json
import os
import secrets
from src.core.config import VAULT_DIR
from src.crypto.vault_cipher import derive_keys, encrypt_vault, decrypt_vault

class VaultManager:
    def __init__(self, name):
        self.name = name
        self.path = os.path.join(VAULT_DIR, f"{name}.enc")
        self.data = {}
        self.aes_key = None
        self.hmac_key = None

    def create(self, password):
        """[Session 7] CSPRNG Salt & Key Generation"""
        salt = secrets.token_bytes(16)
        self.aes_key, self.hmac_key = derive_keys(password, salt)
        self.data = {}
        self.save(salt)

    def unlock(self, password):
        """[Session 4 & 8] Explicit Authentication & Decryption"""
        if not os.path.exists(self.path):
            raise FileNotFoundError("Vault file not found.")
        
        with open(self.path, "rb") as f:
            salt = f.read(16)
            iv = f.read(16)
            stored_mac = f.read(32)
            ciphertext = f.read()
        
        self.aes_key, self.hmac_key = derive_keys(password, salt)
        
        try:
            plaintext = decrypt_vault(ciphertext, iv, stored_mac, self.aes_key, self.hmac_key)
            self.data = json.loads(plaintext.decode())
            return True
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def save(self, salt=None):
        if not self.aes_key: return

        if salt is None:
            with open(self.path, "rb") as f:
                salt = f.read(16)

        data_bytes = json.dumps(self.data).encode()
        iv, mac_tag, ciphertext = encrypt_vault(data_bytes, self.aes_key, self.hmac_key)

        with open(self.path, "wb") as f:
            f.write(salt)
            f.write(iv)
            f.write(mac_tag)
            f.write(ciphertext)

    def add_entry(self, service, username, password):
        self.data[service] = {"username": username, "password": password}
        self.save()
