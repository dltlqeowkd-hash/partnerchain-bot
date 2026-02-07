import sqlite3
import os

DB_PATH = "licenses.db"

if not os.path.exists(DB_PATH):
    print(f"Database file {DB_PATH} not found.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("ALTER TABLE licenses ADD COLUMN memo TEXT")
            conn.commit()
            print("✅ Column 'memo' added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️ Column 'memo' already exists.")
            else:
                print(f"❌ Error adding column: {e}")
                
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")
