from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # [추가] 로그인 아이디
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # PartnerChain Specific Fields
    contact_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    business_number = Column(String, nullable=True) # Optional
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    licenses = relationship("License", back_populates="owner")
    logs = relationship("BotLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # status: unused, active, expired, revoked
    status = Column(String, default="unused")
    
    # license_type: trial, standard, premium
    license_type = Column(String, default="standard")
    is_trial = Column(Boolean, default=False)
    
    # Subscription Link
    subscription_id = Column(String, nullable=True) # From PortOne/Stripe
    
    days_valid = Column(Integer, default=30)
    expiration_date = Column(DateTime, nullable=True)
    hwid = Column(String, nullable=True)
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="licenses")

class BotLog(Base):
    __tablename__ = "bot_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    level = Column(String, default="INFO")
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    imp_uid = Column(String, unique=True, index=True)
    merchant_uid = Column(String, unique=True, index=True)
    amount = Column(Integer)
    status = Column(String) # paid, failed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payments")
