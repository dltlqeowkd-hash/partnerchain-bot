import sqlite3
import secrets
import string
from datetime import datetime, timedelta

DB_PATH = "licenses.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'unused', -- unused, active, expired, revoked
            days_valid INTEGER NOT NULL,
            expiration_date TIMESTAMP,
            hwid TEXT,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_key_string():
    # Format: XXXX-XXXX-XXXX-XXXX
    chars = string.ascii_uppercase + string.digits
    parts = []
    for _ in range(4):
        parts.append(''.join(secrets.choice(chars) for _ in range(4)))
    return '-'.join(parts)

def create_license(days_valid, memo=""):
    key = generate_key_string()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO licenses (key, days_valid, memo, status) VALUES (?, ?, ?, 'unused')", 
              (key, days_valid, memo))
    conn.commit()
    conn.close()
    return key

def get_license(key):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM licenses WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def activate_license(key, hwid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if exists
    c.execute("SELECT * FROM licenses WHERE key = ?", (key,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return False, "Invalid Key"
    
    status = row[1] # status column
    days_valid = row[2] # days_valid column
    current_hwid = row[4] # hwid column
    
    if status == 'revoked':
        conn.close()
        return False, "Key Revoked"
        
    if status == 'active':
        if current_hwid == hwid:
            conn.close()
            return True, "Already Active on this machine"
        else:
            conn.close()
            # [CRITICAL SECURITY] Prevent reusing key on different machine
            return False, f"Error: Key is already bound to another PC (HWID ends in {current_hwid[-4:]}). Cannot transfer."
            
    if status == 'unused':
        # Activate now
        exp_date = datetime.now() + timedelta(days=days_valid)
        c.execute("UPDATE licenses SET status = 'active', hwid = ?, expiration_date = ? WHERE key = ?", 
                  (hwid, exp_date, key))
        conn.commit()
        conn.close()
        return True, "Activation Successful"
        
    return False, "Unknown Error"

def validate_license(key, hwid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, hwid, expiration_date, memo FROM licenses WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False, "Invalid Key", 0, None, None
        
    status, registered_hwid, exp_date_str, memo = row
    
    if status != 'active':
        return False, f"Key is {status}", 0, None, memo
        
    if registered_hwid != hwid:
        return False, "Hardware ID Mismatch", 0, None, memo
        
    # Check expiration
    if exp_date_str:
        exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d %H:%M:%S.%f")
        if datetime.now() > exp_date:
            return False, "License Expired", 0, exp_date, memo
        
        remaining = (exp_date - datetime.now()).days
        return True, "Valid", remaining, exp_date, memo
        
    return True, "Valid (Lifetime)", 9999, None, memo

def get_all_licenses():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM licenses ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]
