import uuid
import os
import socket

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    mac = get_mac_address()
    hostname = socket.gethostname()
    ip = get_ip_address()
    
    filename = "my_mac_address.txt"
    
    content = f"""
PC Info Collection
------------------
Hostname : {hostname}
IP Addr  : {ip}
MAC Addr : {mac}
------------------
"""
    print(content)
    
    with open(filename, "w", encoding='utf-8') as f:
        f.write(mac) # Write ONLY the MAC address cleanly for easy copying, or full info?
        # User said "save to notepad", usually for copy-paste.
        # Let's save JUST the MAC address in one file for easy copy, 
        # and maybe a detail file?
        # Let's stick to saving the MAC address clearly.
    
    # Let's overwrite with detailed info or just MAC?
    # "실행하면 바로 그 PC의 MACID가 자동으로 메모장에 저장되게"
    # To prevent confusion, let's save user-friendly info.
    
    with open(filename, "w", encoding='utf-8') as f:
        f.write(f"MAC: {mac}\n")
        f.write(f"PC: {hostname}\n")
        f.write(f"IP: {ip}")

    print(f"✅ Saved to {filename}")
    os.system(f"notepad {filename}") # Open it immediately for them to see

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
