from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from dependencies import require_roles

router = APIRouter(prefix="/api/schedule/notifications", tags=["🔔 Уведомления"])

@router.post("/subscribe-telegram")
async def subscribe_telegram_ep(telegram_id: str, u: dict = Depends(require_roles("admin", "moderator", "teacher", "student")), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == u["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден в сервисе расписания")
    user.telegram_id = telegram_id
    db.commit()
    return {"message": "Telegram подписка активирована", "telegram_id": telegram_id}
