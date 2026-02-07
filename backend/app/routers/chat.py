from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, dependencies

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/messages", response_model=schemas.ChatMessage)
def send_message(
    message: schemas.ChatMessageCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user_optional)
):
    """메시지 전송 (로그인/비로그인 모두 가능)"""
    db_message = models.ChatMessage(
        user_id=current_user.id if current_user else None,
        guest_id=message.guest_id if not current_user else None,
        message=message.message,
        is_admin=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # TODO: 텔레그램 봇으로 관리자에게 알림 전송
    
    return db_message

@router.get("/messages", response_model=List[schemas.ChatMessage])
def get_messages(
    limit: int = 50,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user_optional)
):
    """내 메시지 조회 (로그인 사용자 또는 guest_id로 조회)"""
    if current_user:
        messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.user_id == current_user.id
        ).order_by(models.ChatMessage.created_at.desc()).limit(limit).all()
    else:
        # 비로그인 사용자는 빈 리스트 반환
        messages = []
    
    return messages

@router.get("/messages/guest/{guest_id}", response_model=List[schemas.ChatMessage])
def get_guest_messages(
    guest_id: str,
    limit: int = 50,
    db: Session = Depends(dependencies.get_db)
):
    """Guest 메시지 조회 (비로그인 사용자용)"""
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.guest_id == guest_id
    ).order_by(models.ChatMessage.created_at.desc()).limit(limit).all()
    
    return messages

@router.put("/messages/{message_id}/read")
def mark_message_as_read(
    message_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user_optional)
):
    """메시지 읽음 표시"""
    message = db.query(models.ChatMessage).filter(
        models.ChatMessage.id == message_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
    
    return {"message": "Message marked as read"}

# 관리자용 API
@router.get("/admin/messages", response_model=List[schemas.ChatMessage])
def get_all_messages_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    admin: models.User = Depends(dependencies.get_current_admin_user)
):
    """관리자용: 모든 채팅 메시지 조회"""
    messages = db.query(models.ChatMessage).order_by(
        models.ChatMessage.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return messages

@router.post("/admin/reply/{user_id}", response_model=schemas.ChatMessage)
def admin_reply(
    user_id: int,
    message: schemas.ChatMessageBase,
    db: Session = Depends(dependencies.get_db),
    admin: models.User = Depends(dependencies.get_current_admin_user)
):
    """관리자용: 사용자에게 답변"""
    db_message = models.ChatMessage(
        user_id=user_id,
        message=message.message,
        is_admin=True
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message
