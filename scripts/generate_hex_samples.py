import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.core.vault_manager import VaultManager

def generate_samples():
    sample_dir = "hex_samples"
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)

    password = "password123"
    content = {"secret": "This is a secret message"}

    # Create first vault
    vm1 = VaultManager("vault1")
    vm1.path = os.path.join(sample_dir, "vault1.enc")
    vm1.create(password)
    vm1.data = content
    vm1.save()
    print(f"Created {vm1.path}")

    # Create second vault (identical content and password)
    vm2 = VaultManager("vault2")
    vm2.path = os.path.join(sample_dir, "vault2.enc")
    vm2.create(password)
    vm2.data = content
    vm2.save()
    print(f"Created {vm2.path}")

if __name__ == "__main__":
    generate_samples()
