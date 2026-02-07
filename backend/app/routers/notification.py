from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, dependencies

router = APIRouter(tags=["Notifications"])

@router.post("/notifications/send", response_model=schemas.Notification)
def send_notification(notification: schemas.NotificationCreate, user_id: int, current_user: models.User = Depends(dependencies.get_current_superuser), db: Session = Depends(dependencies.get_db)):
    db_notification = models.Notification(**notification.dict(), user_id=user_id)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get("/notifications/my", response_model=List[schemas.Notification])
def read_my_notifications(current_user: models.User = Depends(dependencies.get_current_user), db: Session = Depends(dependencies.get_db)):
    return db.query(models.Notification).filter(models.Notification.user_id == current_user.id).order_by(models.Notification.created_at.desc()).all()

@router.put("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: int, current_user: models.User = Depends(dependencies.get_current_user), db: Session = Depends(dependencies.get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id, models.Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    return {"status": "success"}

@router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, current_user: models.User = Depends(dependencies.get_current_user), db: Session = Depends(dependencies.get_db)):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id, models.Notification.user_id == current_user.id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    return {"status": "deleted"}
