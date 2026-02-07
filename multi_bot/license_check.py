import uuid
import re
import requests
import sys
import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime

# --- Configuration ---
SERVER_URL = "http://localhost:8000" 

# Ensure license.dat is stored in the same directory as this script (not CWD)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(BASE_DIR, "license.dat")

def get_mac_address():
    """
    Get the MAC address of the computer.
    Returns format: 00:1A:2B:3C:4D:5E
    """
    mac_num = uuid.getnode()
    mac = ':'.join(re.findall('..', '%012x' % mac_num))
    return mac.upper()

def check_license():
    """
    Main entry point for license check.
    """
    hwid = get_mac_address()
    
    # 1. Check existing license file
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                saved_key = f.read().strip()
            
            # 2. Validate with server
            try:
                resp = requests.post(f"{SERVER_URL}/api/validate", json={"key": saved_key, "hwid": hwid}, timeout=3)
                data = resp.json()
                
                print(f"[DEBUG] License Check: {data}") # Debug output
                
                if data.get("valid"):
                    print(f"✅ 인증 성공 (남은 기간: {data.get('remaining_days')}일)")
                    return {
                        "valid": True,
                        "expiration_date": data.get("expiration_date", "Unknown"), 
                        "memo": data.get("memo") or "Unknown", 
                        "days_remaining": data.get("remaining_days", 0)
                    }
                else:
                    msg = data.get("message", "")
                    print(f"❌ 인증 실패: {msg}")
                    
                    if "Expired" in msg or "만료" in msg:
                         # Explicit Expiration Warning
                         root = tk.Tk()
                         root.withdraw()
                         messagebox.showwarning("기간 만료", f"라이선스 유효 기간이 만료되었습니다.\n({msg})\n\n새로운 시리얼 키를 입력해주세요.")
                         root.destroy()
                    
                    # If invalid, fall through to prompt
            except Exception as e:
                print(f"⚠️  서버 연결 실패: {e}")
                # Offline logic or strict block? Strict block for now.
                
        except Exception as e:
            print(f"License file error: {e}")

    # 3. Prompt for Key (GUI)
    root = tk.Tk()
    root.withdraw() # Hide main window
    
    while True:
        key_input = simpledialog.askstring("정품 인증", 
                                         f"제품 키를 입력하세요.\n\n내 식별 ID: {hwid}\n\n(형식: XXXX-XXXX-XXXX-XXXX)")
        
        if not key_input:
            root.destroy()
            return None # User cancelled
            
        key_input = key_input.strip().upper()
        
        # 4. Activate
        try:
            resp = requests.post(f"{SERVER_URL}/api/activate", json={"key": key_input, "hwid": hwid}, timeout=5)
            
            if resp.status_code == 200:
                # Success
                with open(LICENSE_FILE, "w") as f:
                    f.write(key_input)
                
                messagebox.showinfo("인증 성공", "정품 인증이 완료되었습니다.\n프로그램을 시작합니다.")
                root.destroy()
                
                # Re-validate to get details immediately
                return check_license()
            else:
                # Failure
                err_data = resp.json()
                err_msg = err_data.get("message") or err_data.get("detail", "알 수 없는 오류")
                
                if "bound to another PC" in err_msg:
                    err_msg = "이미 다른 PC에서 사용 중인 키입니다."
                elif "Invalid Key" in err_msg:
                    err_msg = "유효하지 않은 키입니다."
                elif "Expired" in err_msg:
                     err_msg = "이미 만료된 키입니다."

                messagebox.showerror("인증 실패", f"오류: {err_msg}")
                # Loop continues to ask again
                
        except Exception as e:
            messagebox.showerror("연결 오류", f"서버에 연결할 수 없습니다.\n{e}")
            root.destroy()
            return None
