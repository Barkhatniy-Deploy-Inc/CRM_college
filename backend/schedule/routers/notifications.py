from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import TelegramSubscriptionRequest, User
from dependencies import get_current_user

router = APIRouter(prefix="/api/schedule/notifications", tags=["🔔 Уведомления"])

@router.post("/subscribe-telegram")
async def subscribe_telegram_ep(
    payload: TelegramSubscriptionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Сохраняет Telegram ID текущего аутентифицированного пользователя."""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден в сервисе расписания")
    user.telegram_id = payload.telegram_id
    db.commit()
    return {"message": "Telegram подписка активирована", "telegram_id": payload.telegram_id}
