import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json, os, sys, base64, shutil
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# ================= CONFIG =================
VAULT_DIR = "vaults"
BACKUP_DIR = "backups"
MAX_ATTEMPTS = 5

os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

failed_attempts = 0
lock_mode = False
backup_done = False

current_vault_name = None
current_data = {}
current_fernet = None

# ================= CRYPTO =================
def derive_key(password: str, salt: bytes) -> Fernet:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)

def encrypt_data(data: dict, fernet: Fernet) -> bytes:
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_data(blob: bytes, fernet: Fernet) -> dict:
    return json.loads(fernet.decrypt(blob).decode())

# ================= VAULT FILE =================
def vault_path(name):
    return os.path.join(VAULT_DIR, f"{name}.enc")

def backup_path(name):
    return os.path.join(BACKUP_DIR, f"{name}_backup.enc")

# ================= LOCK MODE =================
def enter_lock_mode():
    global lock_mode
    lock_mode = True
    show_lock_screen()

def do_backup_and_exit():
    global backup_done
    if backup_done or not current_vault_name:
        sys.exit()

    src = vault_path(current_vault_name)
    if os.path.exists(src):
        shutil.copy(src, backup_path(current_vault_name))

    backup_done = True
    messagebox.showinfo("Backup", "Vault backed up.\nApplication will exit.")
    sys.exit()

# ================= UI CORE =================
root = tk.Tk()
root.title("Password Manager (Cryptography Demo)")
root.geometry("820x520")

main_frame = None

def clear_screen():
    global main_frame
    if main_frame:
        main_frame.destroy()
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

# ================= SCREENS =================
def show_select_vault():
    clear_screen()

    tk.Label(main_frame, text="Select Vault", font=("Arial", 18)).pack(pady=20)

    def create_vault():
        name = simpledialog.askstring("Vault Name", "Enter new vault name:")
        if not name:
            return
        global current_vault_name
        current_vault_name = name
        show_unlock_screen(new=True)

    def open_vault():
        clear_screen()

        tk.Label(main_frame, text="Select Vault to Open", font=("Arial", 16)).pack(pady=20)

        files = [f[:-4] for f in os.listdir(VAULT_DIR) if f.endswith(".enc")]

        if not files:
            tk.Label(main_frame, text="No vaults found.").pack()
            tk.Button(main_frame, text="Return", command=show_select_vault).pack(pady=10)
            return

        listbox = tk.Listbox(main_frame, width=40, height=10)
        listbox.pack(pady=10)

        for v in files:
            listbox.insert(tk.END, v)

        def confirm():
            if not listbox.curselection():
                return
            global current_vault_name
            current_vault_name = listbox.get(listbox.curselection())
            show_unlock_screen(new=False)

        tk.Button(main_frame, text="Open", width=20, command=confirm).pack(pady=8)
        tk.Button(main_frame, text="Return", width=20, command=show_select_vault).pack()

    def restore_backup():
        file = filedialog.askopenfilename(initialdir=BACKUP_DIR)
        if not file:
            return
        name = os.path.basename(file).replace("_backup.enc", "")
        shutil.copy(file, vault_path(name))
        messagebox.showinfo("Restored", f"Backup restored as vault '{name}'")

    tk.Button(main_frame, text="Create Vault", width=30, command=create_vault).pack(pady=8)
    tk.Button(main_frame, text="Open Vault", width=30, command=open_vault).pack(pady=8)
    tk.Button(main_frame, text="Restore Backup", width=30, command=restore_backup).pack(pady=8)
    tk.Label(
    main_frame,
    text="Note: any empty vault will not be stored even if created.",
    font=("Arial", 9, "italic"),
    fg="gray"
).pack(pady=15)

# ---------------- UNLOCK ----------------
def show_unlock_screen(new=False):
    clear_screen()

    tk.Label(main_frame, text=f"Unlock Vault: {current_vault_name}", font=("Arial", 16)).pack(pady=20)
    tk.Label(main_frame, text="Enter Master Password").pack()

    pwd_entry = tk.Entry(main_frame, show="*", width=30)
    pwd_entry.pack(pady=10)

    hint = tk.Label(main_frame, text="(Password is never stored)", font=("Arial", 9, "italic"))
    hint.pack()

    def unlock():
        global failed_attempts, current_data, current_fernet

        password = pwd_entry.get()
        salt = current_vault_name.encode()

        try:
            fernet = derive_key(password, salt)
            if new:
                current_data = {}
            else:
                with open(vault_path(current_vault_name), "rb") as f:
                    blob = f.read()
                current_data = decrypt_data(blob, fernet)

            current_fernet = fernet
            failed_attempts = 0
            show_vault_screen()

        except (InvalidToken, FileNotFoundError):
            failed_attempts += 1
            messagebox.showerror("Error", "Wrong master password")

            if failed_attempts >= MAX_ATTEMPTS:
                enter_lock_mode()

    tk.Button(main_frame, text="Unlock", command=unlock).pack(pady=15)
    tk.Button(main_frame, text="Return", command=show_select_vault).pack()

# ---------------- LOCK ----------------
def show_lock_screen():
    clear_screen()

    tk.Label(main_frame, text="LOCK MODE", fg="red", font=("Arial", 18)).pack(pady=30)
    tk.Label(main_frame, text="Too many failed attempts.").pack(pady=10)

    tk.Button(main_frame, text="Backup Vault", width=25, command=do_backup_and_exit).pack(pady=10)
    tk.Button(main_frame, text="Exit", width=25, command=sys.exit).pack()

# ---------------- VAULT ----------------
def show_vault_screen():
    clear_screen()

    tk.Label(main_frame, text=f"Vault: {current_vault_name}", font=("Arial", 16)).pack(pady=10)

    listbox = tk.Listbox(main_frame, width=60, height=15)
    listbox.pack(pady=10)

    for k in current_data:
        listbox.insert(tk.END, k)

    def save_vault():
        blob = encrypt_data(current_data, current_fernet)
        with open(vault_path(current_vault_name), "wb") as f:
            f.write(blob)

    def add_entry():
        clear_screen()

        tk.Label(main_frame, text="Add Password Entry", font=("Arial", 16)).pack(pady=15)

        tk.Label(main_frame, text="Service").pack()
        service = tk.Entry(main_frame, width=40)
        service.pack()

        tk.Label(main_frame, text="Username").pack()
        username = tk.Entry(main_frame, width=40)
        username.pack()

        tk.Label(main_frame, text="Password").pack()
        password = tk.Entry(main_frame, width=40, show="*")
        password.pack()

        def save():
            if not service.get():
                return
            current_data[service.get()] = {
                "username": username.get(),
                "password": password.get()
            }
            save_vault()
            show_vault_screen()

        tk.Button(main_frame, text="Save", command=save).pack(pady=10)
        tk.Button(main_frame, text="Return", command=show_vault_screen).pack()

    def view_entry():
        if not listbox.curselection():
            return
        key = listbox.get(listbox.curselection())

        clear_screen()
        tk.Label(main_frame, text=key, font=("Arial", 16)).pack(pady=10)

        tk.Label(main_frame, text=f"Username: {current_data[key]['username']}").pack(pady=5)
        tk.Label(main_frame, text=f"Password: {current_data[key]['password']}").pack(pady=5)

        tk.Button(main_frame, text="Return", command=show_vault_screen).pack(pady=20)

    btns = tk.Frame(main_frame)
    btns.pack()

    tk.Button(btns, text="Add Password", width=18, command=add_entry).grid(row=0, column=0, padx=5)
    tk.Button(btns, text="View", width=18, command=view_entry).grid(row=0, column=1, padx=5)
    tk.Button(btns, text="Lock Vault", width=18, command=show_select_vault).grid(row=0, column=2, padx=5)

# ================= START =================
show_select_vault()
root.mainloop()