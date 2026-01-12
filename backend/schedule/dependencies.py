from fastapi import Depends, HTTPException, Header, Cookie, status
from typing import Optional
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from services.auth import decode_token, get_user_by_id

async def get_current_user(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    token = access_token or (authorization.split()[1] if authorization and " " in authorization else None)
    if not token:
        raise HTTPException(status_code=401, detail="Не аутентифицирован")
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
        
    user = get_user_by_id(payload.get("user_id"), db)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
        
    return user
