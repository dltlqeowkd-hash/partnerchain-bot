from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas
import uuid
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# --- Admin Logic ---
def get_admin(db: Session, username: str):
    return db.query(models.Admin).filter(models.Admin.username == username).first()

def create_admin(db: Session, admin: schemas.AdminCreate):
    hashed_password = pwd_context.hash(admin.password)
    db_admin = models.Admin(username=admin.username, hashed_password=hashed_password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- License Logic ---
def generate_keys(db: Session, key_data: schemas.LicenseCreate):
    created_keys = []
    for _ in range(key_data.count):
        # Generate a random key (e.g. A1B2-C3D4-E5F6-G7H8)
        raw_key = str(uuid.uuid4()).upper().replace("-", "")[:16] 
        formatted_key = "-".join([raw_key[i:i+4] for i in range(0, len(raw_key), 4)])
        
        expires_at = datetime.utcnow() + timedelta(days=key_data.days_valid)
        
        db_license = models.LicenseKey(
            key_string=formatted_key,
            expires_at=expires_at,
            memo=key_data.memo
        )
        db.add(db_license)
        created_keys.append(db_license)
    
    db.commit()
    for key in created_keys:
        db.refresh(key)
    return created_keys

def check_license(db: Session, verify_data: schemas.LicenseVerify):
    license_obj = db.query(models.LicenseKey).filter(models.LicenseKey.key_string == verify_data.key_string).first()
    
    if not license_obj:
        return False, "Invalid Key"
    
    if not license_obj.is_active:
        return False, "Blocked Key"
    
    if license_obj.expires_at and license_obj.expires_at < datetime.utcnow():
        return False, "Expired Key"
    
    # HWID Check
    if license_obj.hwid is None:
        # First use -> Bind HWID
        license_obj.hwid = verify_data.hwid
        license_obj.last_login = datetime.utcnow()
        db.commit()
        return True, "Registered New Device"
    elif license_obj.hwid != verify_data.hwid:
        return False, "HWID Mismatch (Key already used on another PC)"
    
    # Success
    license_obj.last_login = datetime.utcnow()
    db.commit()
    return True, "Valid"
