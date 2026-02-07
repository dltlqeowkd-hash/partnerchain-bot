from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base
import datetime

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class LicenseKey(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    key_string = Column(String, unique=True, index=True)  # The Serial Key (e.g. ABCD-1234...)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Usage Tracking
    hwid = Column(String, nullable=True) # Hardware ID of the user's PC
    last_login = Column(DateTime, nullable=True)
    memo = Column(String, nullable=True) # Note for Admin (e.g. "Sold to John")
