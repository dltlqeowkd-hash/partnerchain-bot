from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, license, notification, payment, version, admin, chat
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PartnerChain Backend API",
    description="Backend for Auth, License, Notification, and Logging",
    version="1.0.0"
)

# CORS (Frontend Integration)
# 환경 변수에서 허용된 origin 읽기 (쉼표로 구분)
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000,http://localhost:8000")
origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(license.router)
app.include_router(notification.router)
app.include_router(payment.router)
app.include_router(version.router)
app.include_router(admin.router)
app.include_router(chat.router)
# app.include_router(log.router) # Will add later

@app.get("/")
def read_root():
    return {"message": "Naver Bot Backend API is running!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
