from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Token 
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    contact_name: str
    phone_number: str
    company_name: str
    business_number: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    # Details
    contact_name: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    business_number: Optional[str] = None
    
    # Free Trial
    trial_days: int
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    subscription_status: str

    class Config:
        orm_mode = True

# License
class LicenseBase(BaseModel):
    days_valid: int = 30
    memo: Optional[str] = None
    license_type: str = "standard"
    is_trial: bool = False
    subscription_id: Optional[str] = None

class LicenseCreate(LicenseBase):
    pass

class License(LicenseBase):
    id: int
    key: str
    owner_id: int
    status: str
    hwid: Optional[str] = None
    expiration_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True

# BotLog
class BotLogBase(BaseModel):
    level: str = "INFO"
    message: str

class BotLogCreate(BotLogBase):
    pass

class BotLog(BotLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Notification
class NotificationBase(BaseModel):
    title: str
    content: str
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    imp_uid: str
    merchant_uid: str
    amount: int
    status: str

class PaymentCreate(BaseModel):
    imp_uid: str
    merchant_uid: str
    amount: int

class Payment(PaymentBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# ChatMessage
class ChatMessageBase(BaseModel):
    message: str

class ChatMessageCreate(ChatMessageBase):
    guest_id: Optional[str] = None

class ChatMessage(ChatMessageBase):
    id: int
    user_id: Optional[int] = None
    guest_id: Optional[str] = None
    is_admin: bool
    is_read: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserWithDetails(User):
    licenses: List[License] = []
    logs: List[BotLog] = []
    notifications: List[Notification] = []
    payments: List[Payment] = []

