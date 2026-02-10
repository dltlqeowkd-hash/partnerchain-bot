import sys
import os
import uuid
import json
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox

# 스크립트 디렉토리를 Python 경로에 추가
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from auto_updater import auto_update_check

# Configuration
def load_config():
    config_path = "bot_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}

config = load_config()
SERVER_URL = config.get("server_url", "http://localhost:8001")
LICENSE_FILE = "license.dat"
BOT_SCRIPT = "final_bot.py" # The actual bot script

def get_hwid():
    # Simple HWID based on MAC address (node)
    # In production, use wmi or disk serial for better security
    return str(uuid.getnode())

def save_license(key):
    with open(LICENSE_FILE, "w") as f:
        f.write(key)

def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, "r") as f:
            return f.read().strip()
    return None

def verify_and_launch(key_entry, root):
    key = key_entry.get().strip()
    if not key:
        messagebox.showerror("Error", "Please enter a license key.")
        return

    hwid = get_hwid()
    
    try:
        response = requests.post(f"{SERVER_URL}/verify", json={"key_string": key, "hwid": hwid})
        data = response.json()
        
        if data.get("valid"):
            messagebox.showinfo("Success", f"License Verified!\nExpires: {data.get('expires_at')}")
            save_license(key)
            root.destroy() # Close launcher
            launch_bot(data.get('expires_at')) # Run the bot with expiration info
        else:
            messagebox.showerror("Failed", f"License verification failed:\n{data.get('message')}")
            
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server.\n{e}")


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_DEBUG_PORT = 9222
CHROME_USER_DATA = r"C:\chrometemp"

def install_dependencies():
    """Attempt to install missing dependencies automatically."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager", "requests"])
        return True
    except subprocess.CalledProcessError:
        return False

import final_bot # Import the bot module

def launch_bot(expiration_date=None):
    # 1. Check/Install Dependencies (Skip if frozen/compiled)
    if not getattr(sys, 'frozen', False):
        try:
            import selenium
            import webdriver_manager
        except ImportError:
            print("Required libraries not found. Installing...")
            if install_dependencies():
                print("Dependencies installed successfully!")
            else:
                messagebox.showerror("Error", "Failed to install dependencies (selenium, webdriver-manager).\nPlease run: pip install selenium webdriver-manager")
                return

    # 2. Launch Chrome Debugger
    print("Starting Chrome in Debug Mode...")
    try:
        # Check if Chrome is already running on this port (optional, but good practice)
        # For simplicity, just try to launch it. If it's already running, it might just open a new window or do nothing.
        chrome_cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
            f"--user-data-dir={CHROME_USER_DATA}"
        ]
        subprocess.Popen(chrome_cmd)
        print("Waiting for Chrome to initialize...")
        # root is already destroyed by the caller, so just wait
        import time
        time.sleep(3) 
    except Exception as e:
        messagebox.showwarning("Chrome Warning", f"Could not launch Chrome automatically.\n{e}\nPlease make sure Chrome is running with remote debugging.")

    # 3. Launch Bot (Directly call main)
    print("Launching Bot UI...")
    try:
        final_bot.main(expiration_date)
    except Exception as e:
        messagebox.showerror("Bot Error", f"Critical Error running bot:\n{e}")


def main():
    # 1. 자동 업데이트 체크 (프로그램 시작 시 최우선)
    print("=" * 50)
    print("프로그램 시작 - 업데이트 확인 중...")
    print("=" * 50)
    auto_update_check()
    
    # 2. 라이선스 체크
    saved_key = load_license()
    
    # If we have a saved key, try auto-login (Optional, for now just show it)
    
    root = tk.Tk()
    root.title("Bot Launcher")
    root.geometry("300x150")
    
    tk.Label(root, text="Enter Serial Key:").pack(pady=10)
    
    key_entry = tk.Entry(root, width=30)
    key_entry.pack(pady=5)
    
    if saved_key:
        key_entry.insert(0, saved_key)
        
    btn = tk.Button(root, text="Login & Start", command=lambda: verify_and_launch(key_entry, root))
    btn.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()
