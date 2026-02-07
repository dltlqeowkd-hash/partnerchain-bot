from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import string
from .. import models, schemas, auth_utils, dependencies

router = APIRouter(tags=["Licenses"])

def generate_license_key():
    chars = string.ascii_uppercase + string.digits
    parts = []
    for _ in range(4):
        parts.append(''.join(secrets.choice(chars) for _ in range(4)))
    return '-'.join(parts)

@router.post("/licenses/", response_model=schemas.License)
def create_license(license_data: schemas.LicenseCreate, current_user: models.User = Depends(dependencies.get_current_superuser), db: Session = Depends(dependencies.get_db)):
    key = generate_license_key()
    new_license = models.License(
        key=key,
        owner_id=current_user.id, # Currently admin owns it, later transfer logic
        license_type=license_data.license_type,
        days_valid=license_data.days_valid,
        memo=license_data.memo,
        status="unused"
    )
    db.add(new_license)
    db.commit()
    db.refresh(new_license)
    return new_license

@router.post("/licenses/validate")
def validate_license(key: str, hwid: str, db: Session = Depends(dependencies.get_db)):
    license = db.query(models.License).filter(models.License.key == key).first()
    
    if not license:
        raise HTTPException(status_code=404, detail="Invalid License Key")
        
    if license.status == "revoked":
        raise HTTPException(status_code=403, detail="License Revoked")
        
    if license.status == "expired":
        raise HTTPException(status_code=403, detail="License Expired")

    # First time activation
    if license.status == "unused":
        license.status = "active"
        license.hwid = hwid
        license.expiration_date = datetime.utcnow() + timedelta(days=license.days_valid)
        db.commit()
        return {"status": "activated", "days_remaining": license.days_valid, "expiration_date": license.expiration_date}
        
    # Already active
    if license.status == "active":
        if license.hwid != hwid:
            raise HTTPException(status_code=403, detail=f"HWID Mismatch. Bound to {license.hwid[-4:] if license.hwid else 'Unknown'}")
        
        # Check expiration
        if license.expiration_date and datetime.utcnow() > license.expiration_date:
            license.status = "expired"
            db.commit()
            raise HTTPException(status_code=403, detail="License Expired")
            
        remaining = (license.expiration_date - datetime.utcnow()).days
        return {"status": "valid", "days_remaining": remaining, "expiration_date": license.expiration_date}
    
    raise HTTPException(status_code=400, detail="Unknown Error")

@router.get("/licenses/my", response_model=list[schemas.License])
def read_my_licenses(current_user: models.User = Depends(dependencies.get_current_user), db: Session = Depends(dependencies.get_db)):
    return current_user.licenses
