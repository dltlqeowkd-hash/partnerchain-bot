import uuid
import re
import requests
import sys
import os
import json
from datetime import datetime

# --- Configuration ---
# In production, change this to your real server IP/Domain
SERVER_URL = "http://localhost:8000" 

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
    1. Check if license.dat exists.
    2. If exists, validate with server.
    3. If not exists or invalid, prompt user for key.
    4. Activate key with server.
    5. Save key if successful.
    """
    license_file = "license.dat"
    hwid = get_mac_address()
    
    # 1. Check existing license file
    if os.path.exists(license_file):
        try:
            with open(license_file, "r") as f:
                saved_key = f.read().strip()
            
            # 2. Validate with server
            try:
                resp = requests.post(f"{SERVER_URL}/api/validate", json={"key": saved_key, "hwid": hwid}, timeout=5)
                data = resp.json()
                
                if data.get("valid"):
                    print(f"✅ License Verified. Days remaining: {data.get('remaining_days')}")
                    # Return metadata dict instead of just True
                    return {
                        "valid": True,
                        "expiration_date": data.get("expiration_date", "Unknown"), # Server might need to send this
                        "memo": data.get("memo", "Unknown"), # Server might need to send this
                        "days_remaining": data.get("remaining_days", 0)
                    }
                else:
                    print(f"❌ License Invalid: {data.get('message')}")
                    # If invalid, logic continues to prompt for new key
            except Exception as e:
                print(f"⚠️  Server Connection Failed: {e}")
                print("   (Allowing offline access temporarily or blocking? For security: Block)")
                return None # Strict mode
                
        except Exception as e:
            print(f"Error reading license file: {e}")

    # 3. Prompt for Key (CLI or GUI)
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    
    root = tk.Tk()
    root.withdraw() # Hide main window
    
    while True:
        key_input = simpledialog.askstring("License Required", 
                                         f"Enter Serial Key to activate this PC.\n\nYour HWID: {hwid}\n\n(Key Format: XXXX-XXXX-XXXX-XXXX)")
        
        if not key_input:
            return None # User cancelled
            
        key_input = key_input.strip().upper()
        
        # 4. Activate
        try:
            resp = requests.post(f"{SERVER_URL}/api/activate", json={"key": key_input, "hwid": hwid}, timeout=5)
            
            if resp.status_code == 200:
                # Success
                with open(license_file, "w") as f:
                    f.write(key_input)
                messagebox.showinfo("Success", "Activation Successful!\nLicense is now bound to this PC.")
                root.destroy()
                
                # Re-validate to get details
                return check_license()
            else:
                # Failure
                err_msg = resp.json().get("detail", "Unknown Error")
                messagebox.showerror("Activation Failed", f"Server says: {err_msg}")

                
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to license server.\n{e}")
            return False
