from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from dependencies import get_current_user

router = APIRouter(prefix="/api/schedule/notifications", tags=["🔔 Уведомления"])

@router.post("/subscribe-telegram")
async def subscribe_telegram_ep(telegram_id: str, u: User = Depends(get_current_user), db: Session = Depends(get_db)):
    u.telegram_id = telegram_id
    db.commit()
    return {"message": "Telegram подписка активирована", "telegram_id": telegram_id}
