import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import os
import shutil
from src.core.config import VAULT_DIR, BACKUP_DIR, MAX_ATTEMPTS
from src.core.vault_manager import VaultManager

class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Vault Manager - Academic Edition")
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

        if not os.path.exists(VAULT_DIR):
            os.makedirs(VAULT_DIR)
            
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

        ttk.Button(self.main_frame, text="Unlock", width=20, command=attempt_unlock).pack(pady=20)
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
        if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
        file = filedialog.askopenfilename(initialdir=BACKUP_DIR)
        if file:
            name = os.path.basename(file).replace("_backup.enc", "")
            shutil.copy(file, os.path.join(VAULT_DIR, f"{name}.enc"))
            messagebox.showinfo("Success", f"Restored vault '{name}'")

    def quit(self):
        if self.manager and os.path.exists(self.manager.path):
            if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
            shutil.copy(self.manager.path, os.path.join(BACKUP_DIR, f"{self.manager.name}_backup.enc"))
        super().quit()
