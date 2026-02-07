from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수에서 DATABASE_URL 읽기 (Railway는 자동으로 제공)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# PostgreSQL URL 형식 변환 (Railway는 postgres://로 시작, SQLAlchemy는 postgresql:// 필요)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite일 경우에만 check_same_thread 옵션 사용
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
