import os

# ================= CONFIG =================
VAULT_DIR = "vaults"
BACKUP_DIR = "backups"
MAX_ATTEMPTS = 5

# PBKDF2 Constants
KDF_ALGORITHM = "SHA256"
KDF_ITERATIONS = 390000
SALT_SIZE = 16

# AES-CBC Constants
AES_KEY_SIZE = 16
IV_SIZE = 16

# HMAC Constants
HMAC_SIZE = 32

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
