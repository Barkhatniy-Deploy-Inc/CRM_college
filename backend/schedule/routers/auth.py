from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import RegisterRequest, TokenResponse, UserResponse, LoginRequest, User
from services.auth import create_user, get_user_by_email, verify_password, create_access_token, set_auth_cookie, get_user_by_id
from dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["🔐 Авторизация (Legacy)"])

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    if get_user_by_email(data.email, db):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    user_id = create_user(data.email, data.password, data.full_name, db)
    token = create_access_token({"user_id": user_id})
    user_info = get_user_by_id(user_id, db)
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user=UserResponse.from_orm(user_info))

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = get_user_by_email(data.email, db)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    token = create_access_token({"user_id": user.id})
    set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user=UserResponse.from_orm(user))

@router.get("/me", response_model=UserResponse)
async def get_me(u: User = Depends(get_current_user)):
    return u

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Вы успешно вышли из системы"}
