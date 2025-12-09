from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from database.database import get_db
from models.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    auth_service = AuthService(db)
    
    # Проверяем, существует ли пользователь
    if auth_service.get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    try:
        # Создаем пользователя
        user_id = auth_service.create_user(data.email, data.password, data.full_name)
        user = auth_service.get_user_by_id(user_id)
        
        # Создаем токен
        access_token = auth_service.create_access_token(data={"user_id": user.id})
        
        # Устанавливаем cookie
        auth_service.set_auth_cookie(response, access_token)
        
        logger.info(f"User registered successfully: {data.email}")
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
    except Exception as e:
        logger.error(f"Registration error for {data.email}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при регистрации пользователя")

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Вход пользователя в систему"""
    auth_service = AuthService(db)
    
    try:
        # Аутентификация пользователя
        user = auth_service.authenticate_user(data.email, data.password)
        if not user:
            logger.warning(f"Failed login attempt for email: {data.email}")
            raise HTTPException(status_code=401, detail="Неверный email или пароль")
        
        # Создаем токен
        access_token = auth_service.create_access_token(data={"user_id": user.id})
        
        # Устанавливаем cookie
        auth_service.set_auth_cookie(response, access_token)
        
        logger.info(f"User logged in successfully: {data.email}")
        
        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {data.email}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при входе в систему")

@router.post("/logout")
async def logout(response: Response):
    """Выход пользователя из системы"""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Успешный выход из системы"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(db: Session = Depends(get_db)):
    """Получение информации о текущем пользователе"""
    # Этот endpoint будет использоваться через middleware
    # который добавит пользователя в request.state
    pass