from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import models, schemas, auth_utils, dependencies

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    # Check Username
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check Email
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth_utils.get_password_hash(user.password)
    
    # 무료 체험 자동 활성화 (기본 3일)
    trial_start = datetime.now()
    trial_end = trial_start + timedelta(days=3)
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        contact_name=user.contact_name,
        phone_number=user.phone_number,
        company_name=user.company_name,
        business_number=user.business_number,
        # 무료 체험 설정
        trial_days=3,
        trial_start_date=trial_start,
        trial_end_date=trial_end,
        subscription_status="trial"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    # form_data.username will carry the actual username now
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = auth_utils.timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/find-id")
def find_id(email: str, db: Session = Depends(dependencies.get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Security: Don't reveal if email exists or not, but for dev we return 404 or success
        # In production, always return "If email exists, we sent the ID"
        return {"status": "sent", "message": "If email exists, ID has been sent."}
    
    # SIMULATION: Send Email
    print(f"[SMTP SIMULATION] To: {email}, Content: Your ID is '{user.username}'")
    
    return {"status": "sent", "message": f"ID sent to {email} (Simulated)"}

@router.post("/reset-password-request")
def reset_password_request(username: str, email: str, db: Session = Depends(dependencies.get_db)):
    user = db.query(models.User).filter(models.User.username == username, models.User.email == email).first()
    if not user:
        return {"status": "sent", "message": "If account exists, reset link has been sent."}
    
    # SIMULATION: Generate Verification Code
    code = "123456" 
    print(f"[SMTP SIMULATION] To: {email}, Content: Verification Code '{code}'")
    
    return {"status": "sent", "message": f"Verification code sent to {email} (Simulated)"}

@router.get("/users/me", response_model=schemas.UserWithDetails)
def read_users_me(current_user: models.User = Depends(dependencies.get_current_user)):
    return current_user
