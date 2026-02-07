from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Requests ---
class LicenseCreate(BaseModel):
    days_valid: int
    memo: Optional[str] = None
    count: int = 1

class LicenseActivate(BaseModel):
    key: str
    hwid: str  # Hardware ID (MAC address or UUID)

class LicenseValidate(BaseModel):
    key: str
    hwid: str

# --- Responses ---
class LicenseResponse(BaseModel):
    key: str
    status: str  # 'unused', 'active', 'expired', 'revoked'
    days_valid: int
    expiration_date: Optional[datetime] = None
    memo: Optional[str] = None
    created_at: datetime

class ValidationResponse(BaseModel):
    valid: bool
    message: str
    remaining_days: int = 0
    expiration_date: Optional[datetime] = None
    memo: Optional[str] = None
