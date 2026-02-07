import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import pyperclip # For copy to clipboard

SERVER_URL = "http://localhost:8001"

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("License Key Generator")
        self.root.geometry("400x350")
        
        # Login State
        self.token = None
        
        # 1. Login Frame
        self.f_login = tk.LabelFrame(root, text="Admin Login")
        self.f_login.pack(padx=10, pady=5, fill="x")
        
        tk.Label(self.f_login, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.e_user = tk.Entry(self.f_login)
        self.e_user.insert(0, "debug_admin") # Default for convenience
        self.e_user.grid(row=0, column=1)
        
        tk.Label(self.f_login, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.e_pass = tk.Entry(self.f_login, show="*")
        self.e_pass.insert(0, "password123") # Default for convenience
        self.e_pass.grid(row=1, column=1)
        
        self.btn_login = tk.Button(self.f_login, text="Login", command=self.login)
        self.btn_login.grid(row=2, column=0, columnspan=2, pady=5)
        
        # 2. Key Gen Frame
        self.f_gen = tk.LabelFrame(root, text="Generate Key")
        self.f_gen.pack(padx=10, pady=5, fill="both", expand=True)
        
        tk.Label(self.f_gen, text="Days Valid:").grid(row=0, column=0, padx=5, pady=5)
        self.e_days = tk.Entry(self.f_gen)
        self.e_days.insert(0, "30")
        self.e_days.grid(row=0, column=1)
        
        tk.Label(self.f_gen, text="Memo:").grid(row=1, column=0, padx=5, pady=5)
        self.e_memo = tk.Entry(self.f_gen)
        self.e_memo.insert(0, "Customer A")
        self.e_memo.grid(row=1, column=1)
        
        self.btn_gen = tk.Button(self.f_gen, text="Generate Key", command=self.generate, state="disabled", bg="#dddddd")
        self.btn_gen.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Result Area
        self.lbl_result = tk.Label(self.f_gen, text="Key will appear here", fg="gray", font=("Consolas", 10))
        self.lbl_result.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.btn_copy = tk.Button(self.f_gen, text="Copy to Clipboard", command=self.copy_key, state="disabled")
        self.btn_copy.grid(row=4, column=0, columnspan=2)

    def login(self):
        user = self.e_user.get()
        pwd = self.e_pass.get()
        
        try:
            resp = requests.post(f"{SERVER_URL}/token", data={"username": user, "password": pwd})
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                messagebox.showinfo("Success", "Login Successful!")
                self.btn_gen.config(state="normal", bg="#4CAF50", fg="white")
                self.f_login.config(text=f"Logged in as: {user}")
            else:
                messagebox.showerror("Error", f"Login Failed: {resp.text}")
        except Exception as e:
            messagebox.showerror("Network Error", f"Could not connect to server.\nMake sure server is running on port 8000.\n{e}")

    def generate(self):
        if not self.token: return
        
        try:
            days = int(self.e_days.get())
            memo = self.e_memo.get()
            
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "days_valid": days,
                "count": 1,
                "memo": memo
            }
            
            resp = requests.post(f"{SERVER_URL}/admin/generate_keys", json=data, headers=headers)
            if resp.status_code == 200:
                key_info = resp.json()[0]
                self.generated_key = key_info["key_string"]
                self.lbl_result.config(text=self.generated_key, fg="blue")
                self.btn_copy.config(state="normal")
            else:
                messagebox.showerror("Error", f"Generation Failed: {resp.text}")
                
        except ValueError:
            messagebox.showerror("Error", "Days must be a number")
        except Exception as e:
            messagebox.showerror("Error", f"{e}")

    def copy_key(self):
        if hasattr(self, 'generated_key'):
            pyperclip.copy(self.generated_key)
            messagebox.showinfo("Copied", "Key copied to clipboard!")

if __name__ == "__main__":
    # Check for requests/pyperclip
    try:
        import requests
        import pyperclip
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pyperclip"])
        import requests, pyperclip

    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
