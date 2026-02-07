from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Admin Schemas ---
class AdminCreate(BaseModel):
    username: str
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

# --- License Schemas ---
class LicenseCreate(BaseModel):
    days_valid: int
    count: int = 1
    memo: Optional[str] = None

class LicenseResponse(BaseModel):
    key_string: str
    expires_at: Optional[datetime]
    memo: Optional[str]

    class Config:
        from_attributes = True

class LicenseVerify(BaseModel):
    key_string: str
    hwid: str

class VerifyResponse(BaseModel):
    valid: bool
    message: str
    expires_at: Optional[str] = None

# --- Version/Update Schema ---
class VersionInfo(BaseModel):
    version: str
    download_url: str
    mandatory: bool = False
