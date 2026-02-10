import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import uuid
import datetime
import json
import os
import requests

# --- CONFIG ---
SERVER_URL = "http://localhost:8000"

# --- GUI APP ---
class KeyGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PartnerChain Admin Tool v1.0")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header = tk.Frame(root, bg="#3f51b5", height=60)
        header.pack(fill="x")
        tk.Label(header, text="🔐 License Key Generator", font=("Arial", 16, "bold"), bg="#3f51b5", fg="white").pack(pady=15)
        
        # Content
        f_main = tk.Frame(root, padx=20, pady=20)
        f_main.pack(fill="both", expand=True)
        
        # Memo / Company Name
        tk.Label(f_main, text="🏢 업체명 / 메모:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.e_memo = tk.Entry(f_main, font=("Arial", 11))
        self.e_memo.pack(fill="x", pady=(5, 15))
        
        # Duration
        tk.Label(f_main, text="📅 유효 기간:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.combo_days = ttk.Combobox(f_main, values=["30일 (1개월)", "60일 (2개월)", "90일 (3개월)", "365일 (1년)", "9999일 (무제한)"], state="readonly", font=("Arial", 10))
        self.combo_days.current(0)
        self.combo_days.pack(fill="x", pady=(5, 15))
        
        # Generate Button
        btn_gen = tk.Button(f_main, text="✨ 시리얼 키 생성", command=self.generate, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        btn_gen.pack(fill="x", pady=10)
        
        # Result Area
        tk.Label(f_main, text="🔑 생성된 키:", font=("Arial", 9)).pack(anchor="w")
        f_res = tk.Frame(f_main)
        f_res.pack(fill="x")
        
        self.e_key = tk.Entry(f_res, font=("Consolas", 11), readonlybackground="white", state="readonly")
        self.e_key.pack(side="left", fill="x", expand=True)
        
        tk.Button(f_res, text="복사", command=self.copy_key, bg="#2196F3", fg="white").pack(side="right", padx=5)
        
        # Status
        self.lbl_status = tk.Label(root, text="준비됨", bd=1, relief=tk.SUNKEN, anchor="w", padx=5, bg="#f0f0f0")
        self.lbl_status.pack(fill="x")
        
    def generate(self):
        memo = self.e_memo.get().strip()
        if not memo:
            messagebox.showwarning("입력 오류", "업체명/메모를 입력해주세요.")
            return
            
        days_str = self.combo_days.get()
        days = int(days_str.split("일")[0])
        
        # Call License Server API
        try:
            payload = {
                "days_valid": days,
                "memo": memo,
                "count": 1
            }
            response = requests.post(f"{SERVER_URL}/admin/generate", json=payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json() # List of keys
                if data and len(data) > 0:
                    new_key = data[0]['key']
                    
                    self.e_key.config(state="normal")
                    self.e_key.delete(0, tk.END)
                    self.e_key.insert(0, new_key)
                    self.e_key.config(state="readonly")
                    
                    # Save to local log file (optional backup)
                    self.log_key(new_key, memo, days)
                    
                    self.lbl_status.config(text=f"✅ 서버 등록 및 키 생성 완료: {memo} ({days}일)")
                else:
                     messagebox.showerror("오류", "서버 응답에 키 데이터가 없습니다.")
            else:
                 messagebox.showerror("서버 오류", f"키 생성 실패 (Status: {response.status_code})")
                 
        except Exception as e:
            messagebox.showerror("연결 실패", f"라이선스 서버에 연결할 수 없습니다.\nMake sure 0. 서버_실행(필수).bat is running!\n\nError: {e}")
            
    # ... (rest of methods)

    def copy_key(self):
        key = self.e_key.get()
        if key:
            self.root.clipboard_clear()
            self.root.clipboard_append(key)
            self.root.update() 
            messagebox.showinfo("복사 완료", "클립보드에 복사되었습니다!")
            
    def log_key(self, key, memo, days):
        try:
            with open("license_gen_log.txt", "a", encoding="utf-8") as f:
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{ts}] {memo} | {days}일 | {key}\n")
        except: pass

if __name__ == "__main__":
    root = tk.Tk()
    if os.name == 'nt':
        root.iconbitmap(default='') # No icon for now
    app = KeyGenApp(root)
    root.mainloop()

