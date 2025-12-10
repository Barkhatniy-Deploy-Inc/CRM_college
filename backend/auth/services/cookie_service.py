"""Сервис для работы с cookies"""
from fastapi import Response
from core.config import settings


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """
    Установка cookies с токенами авторизации
    
    Args:
        response: FastAPI Response объект
        access_token: JWT access токен
        refresh_token: JWT refresh токен
    """
    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        path="/"
    )
    
    # Refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        path="/"
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Удаление cookies авторизации
    
    Args:
        response: FastAPI Response объект
    """
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

