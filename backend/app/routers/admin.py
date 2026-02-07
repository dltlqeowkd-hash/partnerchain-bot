from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from .. import models, schemas, dependencies

router = APIRouter(prefix="/admin", tags=["Admin"])

# 관리자 유저 검증 함수
async def get_current_admin_user(current_user: models.User = Depends(dependencies.get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/users", response_model=List[schemas.User])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    """관리자용: 모든 유저 조회"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.UserWithDetails)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    """관리자용: 특정 유저 상세 조회"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}/trial")
def update_user_trial(
    user_id: int,
    trial_days: int,
    db: Session = Depends(dependencies.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    """관리자용: 유저 무료 체험 기간 수정"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 체험 기간 업데이트
    user.trial_days = trial_days
    if user.trial_start_date:
        user.trial_end_date = user.trial_start_date + timedelta(days=trial_days)
    else:
        # 체험을 아직 시작하지 않은 경우 지금 시작
        user.trial_start_date = datetime.now()
        user.trial_end_date = user.trial_start_date + timedelta(days=trial_days)
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Trial period updated successfully",
        "user_id": user.id,
        "trial_days": user.trial_days,
        "trial_end_date": user.trial_end_date
    }

@router.put("/users/{user_id}/subscription")
def update_user_subscription_status(
    user_id: int,
    status: str,  # trial, active, expired
    db: Session = Depends(dependencies.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    """관리자용: 유저 구독 상태 변경"""
    if status not in ["trial", "active", "expired"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be one of: trial, active, expired")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.subscription_status = status
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Subscription status updated successfully",
        "user_id": user.id,
        "subscription_status": user.subscription_status
    }

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(dependencies.get_db),
    admin: models.User = Depends(get_current_admin_user)
):
    """관리자용: 통계 데이터"""
    total_users = db.query(models.User).count()
    trial_users = db.query(models.User).filter(models.User.subscription_status == "trial").count()
    active_users = db.query(models.User).filter(models.User.subscription_status == "active").count()
    expired_users = db.query(models.User).filter(models.User.subscription_status == "expired").count()
    
    # 체험 종료 임박 유저 (1일 이내)
    now = datetime.now()
    expiring_soon = db.query(models.User).filter(
        models.User.subscription_status == "trial",
        models.User.trial_end_date != None,
        models.User.trial_end_date <= now + timedelta(days=1),
        models.User.trial_end_date > now
    ).count()
    
    return {
        "total_users": total_users,
        "trial_users": trial_users,
        "active_users": active_users,
        "expired_users": expired_users,
        "expiring_soon": expiring_soon
    }
