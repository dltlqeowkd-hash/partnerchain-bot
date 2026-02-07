import models, schemas, crud, database
from sqlalchemy.orm import Session
import os
import sys

# Ensure we are in the right directory context if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Starting Full Stack Debug...")

try:
    # 1. Init DB
    print("1. Initializing Database...")
    models.Base.metadata.create_all(bind=database.engine)
    print("   Database OK.")

    # 2. Create Session
    db = database.SessionLocal()
    
    # 3. Try Creating Admin (Mocking the server logic)
    print("2. Testing Admin Creation logic...")
    username = "debug_admin"
    password = "password123"
    
    admin = crud.get_admin(db, username)
    if not admin:
        print("   Creating new admin...")
        crud.create_admin(db, schemas.AdminCreate(username=username, password=password))
        print("   Admin created.")
    else:
        print("   Admin already exists.")
        
    # 4. Try Verify Password
    print("3. Testing Password Verification...")
    admin = crud.get_admin(db, username)
    if crud.verify_password(password, admin.hashed_password):
        print("   Password Verify OK.")
    else:
        print("   Password Verify FAILED.")

    print("SUCCESS: logic seems fine.")
    
except Exception as e:
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
finally:
    try: db.close()
    except: pass
