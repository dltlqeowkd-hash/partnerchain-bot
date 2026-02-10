import sys
import os
import uuid
import json
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox

# 설정
SERVER_URL = "http://localhost:8001"
LICENSE_FILE = "license.dat"
BOT_SCRIPT = "multi_bot.py"

def get_hwid():
    """하드웨어 ID 가져오기 (MAC 주소 기반)"""
    return str(uuid.getnode())

def save_license(key):
    """라이선스 키 저장"""
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(key)

def load_license():
    """저장된 라이선스 키 불러오기"""
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def verify_and_launch(key_entry, root):
    """라이선스 검증 및 봇 실행"""
    key = key_entry.get().strip()
    if not key:
        messagebox.showerror("오류", "라이선스 키를 입력해주세요.")
        return

    hwid = get_hwid()
    
    try:
        response = requests.post(f"{SERVER_URL}/verify", json={"key_string": key, "hwid": hwid})
        data = response.json()
        
        if data.get("valid"):
            messagebox.showinfo("인증 성공", f"라이선스 인증 완료!\\n만료일: {data.get('expires_at')}")
            save_license(key)
            root.destroy() # 런처 닫기
            launch_bot(data.get('expires_at')) # 봇 실행
        else:
            messagebox.showerror("인증 실패", f"라이선스 인증 실패:\\n{data.get('message')}")
            
    except Exception as e:
        messagebox.showerror("서버 오류", f"인증 서버에 연결할 수 없습니다.\\n{e}\\n\\n라이선스 서버가 실행 중인지 확인해주세요.")


CHROME_PATH = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
CHROME_DEBUG_PORT = 9222
CHROME_USER_DATA = r"C:\\chrometemp"

def install_dependencies():
    """필요한 라이브러리 자동 설치"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager", "requests"])
        return True
    except subprocess.CalledProcessError:
        return False

import multi_bot # 봇 모듈 import

def launch_bot(expiration_date=None):
    """봇 실행"""
    # 1. 의존성 확인/설치
    if not getattr(sys, 'frozen', False):
        try:
            import selenium
            import webdriver_manager
        except ImportError:
            print("필요한 라이브러리가 없습니다. 설치 중...")
            if install_dependencies():
                print("라이브러리 설치 완료!")
            else:
                messagebox.showerror("오류", "라이브러리 설치 실패 (selenium, webdriver-manager).\\n수동으로 설치해주세요: pip install selenium webdriver-manager")
                return

    # 2. Chrome 디버그 모드로 실행
    print("Chrome 디버그 모드 시작 중...")
    try:
        chrome_cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
            f"--user-data-dir={CHROME_USER_DATA}"
        ]
        subprocess.Popen(chrome_cmd)
        print("Chrome 초기화 대기 중...")
        import time
        time.sleep(3) 
    except Exception as e:
        messagebox.showwarning("Chrome 경고", f"Chrome을 자동으로 실행할 수 없습니다.\\n{e}\\n\\nChrome이 디버그 모드로 실행 중인지 확인하세요.")

    # 3. 봇 실행
    print("봇 UI 실행 중...")
    try:
        multi_bot.main(expiration_date)
    except Exception as e:
        messagebox.showerror("봇 오류", f"봇 실행 중 오류가 발생했습니다:\\n{e}")


def main():
    """메인 런처 UI"""
    saved_key = load_license()
    
    root = tk.Tk()
    root.title("네이버 쇼핑 봇 - 라이선스 인증")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # 타이틀
    title_label = tk.Label(root, text="🔐 라이선스 인증", font=("맑은 고딕", 14, "bold"))
    title_label.pack(pady=15)
    
    # 설명
    desc_label = tk.Label(root, text="시리얼 키를 입력해주세요:", font=("맑은 고딕", 10))
    desc_label.pack(pady=5)
    
    # 키 입력창
    key_entry = tk.Entry(root, width=40, font=("맑은 고딕", 10))
    key_entry.pack(pady=10)
    
    if saved_key:
        key_entry.insert(0, saved_key)
        
    # 로그인 버튼
    btn = tk.Button(
        root, 
        text="✓ 인증 및 시작", 
        command=lambda: verify_and_launch(key_entry, root),
        font=("맑은 고딕", 11, "bold"),
        bg="#0066cc",
        fg="white",
        padx=20,
        pady=10,
        cursor="hand2"
    )
    btn.pack(pady=15)
    
    # 안내 문구
    info_label = tk.Label(root, text="※ 라이선스 서버(localhost:8001)가 실행 중이어야 합니다", 
                          font=("맑은 고딕", 8), fg="gray")
    info_label.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    main()
