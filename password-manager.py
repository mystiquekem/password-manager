import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import json, os, sys, base64, shutil
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets

# ================= CONFIG =================
VAULT_DIR = "vaults"
BACKUP_DIR = "backups"
MAX_ATTEMPTS = 5

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ================= CRYPTO LOGIC (Explicit Implementation) =================
class VaultManager:
    def __init__(self, name):
        self.name = name
        self.path = os.path.join(VAULT_DIR, f"{name}.enc")
        self.data = {}
        self.aes_key = None
        self.hmac_key = None

    @staticmethod
    def derive_keys(password: str, salt: bytes):
        """[Session 8] Key Derivation & Stretching"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32, # 16 for AES + 16 for HMAC
            salt=salt,
            iterations=390000,
        )
        full_key = kdf.derive(password.encode())
        # [Pipeline Stage 2] Tách Khóa: 16b AES Key + 16b HMAC Key
        return full_key[:16], full_key[16:]

    def create(self, password):
        """[Session 7] CSPRNG Salt & Key Generation"""
        salt = secrets.token_bytes(16)
        self.aes_key, self.hmac_key = self.derive_keys(password, salt)
        self.data = {}
        self.save(salt)

    def unlock(self, password):
        """[Session 4 & 8] Explicit Authentication & Decryption"""
        if not os.path.exists(self.path):
            raise FileNotFoundError("Vault file not found.")
        
        with open(self.path, "rb") as f:
            salt = f.read(16)
            iv = f.read(16)
            stored_mac = f.read(32) # HMAC-SHA256 tag
            ciphertext = f.read()
        
        # 1. Derive Keys
        self.aes_key, self.hmac_key = self.derive_keys(password, salt)

        # 2. [Session 8] Integrity Check: Verify HMAC
        h = hmac.HMAC(self.hmac_key, hashes.SHA256())
        h.update(ciphertext)
        try:
            h.verify(stored_mac)
        except Exception:
            raise ValueError("Integrity check failed (MAC mismatch).")

        # 3. [Session 4] Decryption: AES-128-CBC
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # 4. [Session 4] Remove PKCS7 Padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        
        self.data = json.loads(plaintext.decode())
        return True

    def save(self, salt=None):
        """[Session 4 & 8] Explicit Encryption & Packaging"""
        if not self.aes_key: return

        # Read salt if not provided (for updates)
        if salt is None:
            with open(self.path, "rb") as f:
                salt = f.read(16)

        # 1. [Session 4] Add PKCS7 Padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(json.dumps(self.data).encode()) + padder.finalize()

        # 2. [Session 4] Encryption: AES-128-CBC with Random IV
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # 3. [Session 8] Tính toán HMAC-SHA256 (Encrypt-then-MAC)
        h = hmac.HMAC(self.hmac_key, hashes.SHA256())
        h.update(ciphertext)
        mac_tag = h.finalize()

        # 4. Packaging: [Salt] + [IV] + [MAC] + [Ciphertext]
        with open(self.path, "wb") as f:
            f.write(salt)
            f.write(iv)
            f.write(mac_tag)
            f.write(ciphertext)

    def add_entry(self, service, username, password):
        self.data[service] = {"username": username, "password": password}
        self.save()

# ================= UI LAYER =================
class PasswordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Vault Manager")
        self.geometry("820x520")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        self.manager = None
        self.failed_attempts = 0
        self.main_frame = None
        
        self.show_select_vault()

    def clear_screen(self):
        if self.main_frame:
            self.main_frame.destroy()
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(fill="both", expand=True)

    def show_select_vault(self):
        self.clear_screen()
        ttk.Label(self.main_frame, text="Password Vaults", font=("Arial", 24, "bold")).pack(pady=30)
        
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Create New Vault", width=30, command=self.create_vault_dialog).pack(pady=5)
        ttk.Button(btn_frame, text="Open Existing Vault", width=30, command=self.show_open_vault).pack(pady=5)
        ttk.Button(btn_frame, text="Restore Backup", width=30, command=self.restore_backup).pack(pady=5)

    def create_vault_dialog(self):
        name = simpledialog.askstring("New Vault", "Enter vault name:")
        if name:
            self.manager = VaultManager(name)
            self.show_unlock_screen(new=True)

    def show_open_vault(self):
        self.clear_screen()
        ttk.Label(self.main_frame, text="Select Vault to Open", font=("Arial", 18)).pack(pady=20)

        files = [f[:-4] for f in os.listdir(VAULT_DIR) if f.endswith(".enc")]
        if not files:
            ttk.Label(self.main_frame, text="No vaults found.").pack()
            ttk.Button(self.main_frame, text="Back", command=self.show_select_vault).pack(pady=10)
            return

        listbox = tk.Listbox(self.main_frame, width=50, height=10, font=("Arial", 10))
        listbox.pack(pady=10)
        for v in files:
            listbox.insert(tk.END, v)

        def confirm():
            if listbox.curselection():
                name = listbox.get(listbox.curselection())
                self.manager = VaultManager(name)
                self.show_unlock_screen(new=False)

        ttk.Button(self.main_frame, text="Unlock Selected", width=20, command=confirm).pack(pady=10)
        ttk.Button(self.main_frame, text="Back", width=20, command=self.show_select_vault).pack()

    def show_unlock_screen(self, new=False):
        self.clear_screen()
        ttk.Label(self.main_frame, text=f"Vault: {self.manager.name}", font=("Arial", 18)).pack(pady=20)
        ttk.Label(self.main_frame, text="Enter Master Password:").pack()

        pwd_entry = ttk.Entry(self.main_frame, show="*", width=40)
        pwd_entry.pack(pady=10)
        pwd_entry.focus()

        def attempt_unlock():
            pwd = pwd_entry.get()
            try:
                if new:
                    self.manager.create(pwd)
                else:
                    self.manager.unlock(pwd)
                self.failed_attempts = 0
                self.show_entries()
            except Exception as e:
                self.failed_attempts += 1
                messagebox.showerror("Error", f"Unlock Failed: {str(e)}")
                if self.failed_attempts >= MAX_ATTEMPTS:
                    messagebox.showwarning("Lockout", "Too many failed attempts. Closing.")
                    self.quit()

        ttk.Button(self.main_frame, text="Go", width=20, command=attempt_unlock).pack(pady=20)
        ttk.Button(self.main_frame, text="Cancel", width=20, command=self.show_select_vault).pack()

    def show_entries(self):
        self.clear_screen()
        ttk.Label(self.main_frame, text=f"Vault: {self.manager.name}", font=("Arial", 16, "bold")).pack(pady=10)

        listbox = tk.Listbox(self.main_frame, width=70, height=12, font=("Arial", 10))
        listbox.pack(pady=10)
        for service in self.manager.data:
            listbox.insert(tk.END, service)

        ctrl_frame = ttk.Frame(self.main_frame)
        ctrl_frame.pack(pady=10)

        ttk.Button(ctrl_frame, text="Add Entry", command=self.add_entry_dialog).grid(row=0, column=0, padx=5)
        ttk.Button(ctrl_frame, text="View Entry", command=lambda: self.view_entry(listbox)).grid(row=0, column=1, padx=5)
        ttk.Button(ctrl_frame, text="Lock", command=self.show_select_vault).grid(row=0, column=2, padx=5)

    def add_entry_dialog(self):
        self.clear_screen()
        ttk.Label(self.main_frame, text="Add New Password", font=("Arial", 18)).pack(pady=20)
        
        fields = {}
        for label in ["Service", "Username", "Password"]:
            ttk.Label(self.main_frame, text=f"{label}:").pack()
            entry = ttk.Entry(self.main_frame, width=40, show="*" if label=="Password" else "")
            entry.pack(pady=5)
            fields[label] = entry

        def save():
            s, u, p = fields["Service"].get(), fields["Username"].get(), fields["Password"].get()
            if s and u and p:
                self.manager.add_entry(s, u, p)
                self.show_entries()

        ttk.Button(self.main_frame, text="Save", width=20, command=save).pack(pady=10)
        ttk.Button(self.main_frame, text="Cancel", width=20, command=self.show_entries).pack()

    def view_entry(self, listbox):
        if not listbox.curselection(): return
        service = listbox.get(listbox.curselection())
        entry = self.manager.data[service]
        messagebox.showinfo(service, f"User: {entry['username']}\nPass: {entry['password']}")

    def restore_backup(self):
        file = filedialog.askopenfilename(initialdir=BACKUP_DIR)
        if file:
            name = os.path.basename(file).replace("_backup.enc", "")
            shutil.copy(file, os.path.join(VAULT_DIR, f"{name}.enc"))
            messagebox.showinfo("Success", f"Restored vault '{name}'")

    def quit(self):
        # Auto-backup on exit if a vault is open
        if self.manager and os.path.exists(self.manager.path):
            shutil.copy(self.manager.path, os.path.join(BACKUP_DIR, f"{self.manager.name}_backup.enc"))
        super().quit()

if __name__ == "__main__":
    app = PasswordApp()
    app.mainloop()
