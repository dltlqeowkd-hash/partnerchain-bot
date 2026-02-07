from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os
from database import init_db, create_license, get_license, activate_license, validate_license, get_all_licenses
from models import LicenseCreate, LicenseActivate, LicenseValidate, ValidationResponse, LicenseResponse

app = FastAPI(title="Bot License Server")

# Initialize DB
init_db()

# Setup Templates & Static files (if we add CSS/JS later)
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- API Endpoints ---

@app.post("/admin/generate", response_model=list[LicenseResponse])
def generate_keys(req: LicenseCreate):
    created_keys = []
    for _ in range(req.count):
        key = create_license(req.days_valid, req.memo)
        lic = get_license(key)
        created_keys.append(lic)
    return created_keys

@app.get("/admin/list")
def list_keys():
    return get_all_licenses()

@app.post("/api/activate")
def activate_key(req: LicenseActivate):
    success, msg = activate_license(req.key, req.hwid)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@app.post("/api/validate", response_model=ValidationResponse)
def validate_key(req: LicenseValidate):
    is_valid, msg, remaining, exp_date, memo = validate_license(req.key, req.hwid)
    return ValidationResponse(
        valid=is_valid, 
        message=msg, 
        remaining_days=remaining,
        expiration_date=exp_date,
        memo=memo
    )

# --- Web Dashboard Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    # In a real app, check for auth cookie here
    licenses = get_all_licenses()
    return templates.TemplateResponse("index.html", {"request": request, "licenses": licenses})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
