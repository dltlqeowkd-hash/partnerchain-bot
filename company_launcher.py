import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import re
try:
    from mac_config import ALLOWED_MACS
except ImportError:
    ALLOWED_MACS = [] # Default to block if config missing, or [] effectively blocks nothing? 
    # Use empty list to indicate no config found. Logic below will handle empty list.
    pass

def verify_device():
    """Checks if the current machine's MAC address is in the allowed list."""
    if not ALLOWED_MACS:
        # If no MACs are configured, you might want to allow all temporarily OR block all.
        # Given user wants security, strict mode by default?
        # But for first run safetey, strict is better.
        # But wait, if ALLOWED_MACS is empty, it blocks everyone.
        # User instructed to add MACs. So Blocking is correct.
        pass

    try:
        # Get all MAC addresses using getmac
        # Using CP949 for Korean Windows support
        cmd = "getmac /v /fo csv"
        result = subprocess.check_output(cmd, shell=True).decode('cp949', errors='ignore')
        
        # Regex to extract MACs (XX-XX-XX-XX-XX-XX)
        current_macs = set()
        iterator = re.finditer(r'((?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})', result)
        for match in iterator:
            mac = match.group(1).upper().replace(':', '-')
            current_macs.add(mac)
            
        # Check against allowed list
        # If ANY of the current machine's MACs are in the allowed list, PERMIT.
        is_allowed = False
        for mac in current_macs:
            if mac in ALLOWED_MACS:
                is_allowed = True
                break
        
        if not is_allowed:
            root = tk.Tk()
            root.withdraw()
            mac_str = "\n".join(list(current_macs))
            messagebox.showerror("인증 실패 (Access Denied)", 
                                 f"등록되지 않은 기기입니다.\n프로그램을 실행할 수 없습니다.\n\n[내 MAC 주소]\n{mac_str}\n\n관리자에게 위 주소를 전달하여 등록 요청하세요.")
            root.destroy()
            sys.exit()

    except Exception as e:
        # If check fails (e.g. getmac command missing), fail safe?
        # Better to fail secure.
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("보안 오류", f"보안 검증 중 오류가 발생했습니다.\n{e}")
        root.destroy()
        sys.exit()
# Configuration
BOT_SCRIPT = "final_bot.py"
def find_chrome_path():
    """Finds the Google Chrome executable path."""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    # 1. Check strict paths
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    # 2. Check detected registry/system path
    # (Optional: Implementation using winreg could go here but file checks are usually enough)
    
    return None

CHROME_PATH = find_chrome_path()
if not CHROME_PATH:
    # Use default if not found, but warn? Or just let it fail later?
    # Better to fail early or default to standard x64 path
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

def launch_bot(expiration_date="무제한 (회사용)"):
    # 0. Security Check
    verify_device()

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
        chrome_cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
            f"--user-data-dir={CHROME_USER_DATA}",
            "--remote-allow-origins=*",  # Fix for newer Chrome versions
            "--disable-gpu",             # Stability for VMs
            "--no-first-run",
            "--no-default-browser-check"
        ]
        subprocess.Popen(chrome_cmd)
        print("Waiting for Chrome to initialize...")
        import time
        for i in range(8): # Wait 8 seconds (increased from 3)
            print(f"Loading... {8-i}")
            time.sleep(1)
    except Exception as e:
        messagebox.showwarning("Chrome Warning", f"Could not launch Chrome automatically.\n{e}\nPlease make sure Chrome is running with remote debugging.")

    # 3. Launch Bot (Directly call main)
    print("Launching Bot UI...")
    try:
        final_bot.main(expiration_date)
    except Exception as e:
        messagebox.showerror("Bot Error", f"Critical Error running bot:\n{e}")

if __name__ == "__main__":
    launch_bot()
