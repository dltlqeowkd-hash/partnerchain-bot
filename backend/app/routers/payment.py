from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from .. import models, schemas, dependencies

router = APIRouter(
    prefix="/payment",
    tags=["payment"],
    responses={404: {"description": "Not found"}},
)

@router.post("/complete", response_model=schemas.Payment)
def payment_complete(
    payment_data: schemas.PaymentCreate, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    # 1. Simple Validation (Test Mode)
    if payment_data.amount <= 0:
         raise HTTPException(status_code=400, detail="Invalid payment amount")

    # Check for duplicate
    existing = db.query(models.Payment).filter(models.Payment.imp_uid == payment_data.imp_uid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Payment already processed")

    # 2. Use Transaction
    try:
        # Create Payment Record
        db_payment = models.Payment(
            user_id=current_user.id,
            imp_uid=payment_data.imp_uid,
            merchant_uid=payment_data.merchant_uid,
            amount=payment_data.amount,
            status="paid"
        )
        db.add(db_payment)
        
        # 3. Issue License
        license_key = str(uuid.uuid4()).upper()
        expiration = datetime.utcnow() + timedelta(days=30)
        
        db_license = models.License(
            key=license_key,
            owner_id=current_user.id,
            status="active",
            license_type="standard",
            is_trial=False,
            days_valid=30,
            expiration_date=expiration,
            subscription_id=payment_data.merchant_uid,
            memo="Purchased via PortOne"
        )
        db.add(db_license)
        
        # 4. Create Notification
        db_noti = models.Notification(
            user_id=current_user.id,
            title="✅ [구독 완료] 정식 라이선스가 발급되었습니다.",
            content=f"파트너체인 구독을 환영합니다.\n\n발급된 라이선스 키:\n{license_key}\n\n유효 기간: {expiration.strftime('%Y-%m-%d %H:%M')} 까지\n\n[봇 실행 > 로그인] 시 자동으로 적용되거나, 설정 메뉴에서 키를 입력할 수 있습니다."
        )
        db.add(db_noti)
        
        db.commit()
        db.refresh(db_payment)
        return db_payment
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
