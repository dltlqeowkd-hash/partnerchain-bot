from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import models, schemas, crud, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth Routes (Admin) ---
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Simple admin check for now (In prod, use proper auth flow)
    # For demo purposes, we will auto-create admin if not exists
    admin = crud.get_admin(db, form_data.username)
    if not admin:
        # Auto-register first user as admin for simplicity in setup
        if db.query(models.Admin).count() == 0:
            crud.create_admin(db, schemas.AdminCreate(username=form_data.username, password=form_data.password))
            admin = crud.get_admin(db, form_data.username)
    
    if not admin or not crud.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": admin.username, "token_type": "bearer"}

# --- Admin Routes ---
@app.post("/admin/generate_keys", response_model=list[schemas.LicenseResponse])
def generate_license_keys(key_data: schemas.LicenseCreate, token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")), db: Session = Depends(get_db)):
    # In real app, verify token here
    return crud.generate_keys(db, key_data)

# --- Public Client Routes ---
@app.post("/verify", response_model=schemas.VerifyResponse)
def verify_license(verify_data: schemas.LicenseVerify, db: Session = Depends(get_db)):
    is_valid, message = crud.check_license(db, verify_data)
    
    # Calculate expiry string if valid
    exp_str = None
    if is_valid:
        lic = db.query(models.LicenseKey).filter(models.LicenseKey.key_string == verify_data.key_string).first()
        if lic and lic.expires_at:
            exp_str = lic.expires_at.strftime("%Y-%m-%d")

    return {"valid": is_valid, "message": message, "expires_at": exp_str}

@app.get("/version", response_model=schemas.VersionInfo)
def check_version():
    # Hardcoded for now. In future, this can read from a DB or file.
    return {
        "version": "1.0.0",
        "download_url": "https://example.com/download/v1.0.0.zip", # Placeholder
        "mandatory": True
    }

@app.get("/")
def read_root():
    return {"status": "Server is running"}
