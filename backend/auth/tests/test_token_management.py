import pytest
import time
from services.token_service import create_token_pair, refresh_access_token, revoke_refresh_token
from database.models import User, UserRole, RefreshToken

@pytest.mark.asyncio
async def test_refresh_token_flow(db):
    """Тест жизненного цикла refresh токена"""
    unique_email = f"token_{time.time()}@test.ru"
    user = User(email=unique_email, password_hash="hash", full_name="Token User", role=UserRole.STUDENT)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token, refresh_token_str = create_token_pair(user, db, ip_address="127.0.0.1")
    assert refresh_token_str is not None
    
    new_access, new_refresh, refreshed_user = refresh_access_token(refresh_token_str, db)
    assert new_access is not None
    assert refreshed_user.id == user.id
    
    revoke_refresh_token(refresh_token_str, db)
    
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as excinfo:
        refresh_access_token(refresh_token_str, db)
    assert excinfo.value.status_code == 401

@pytest.mark.asyncio
async def test_token_refresh_api(client):
    """Тест API обновления access токена через refresh токен"""
    unique_email = f"api_refresh_{time.time()}@test.ru"
    payload = {"email": unique_email, "password": "testpassword123", "full_name": "API Refresh"}
    reg_resp = await client.post("/api/auth/register", json=payload)
    
    # Проверяем, что регистрация прошла успешно
    assert reg_resp.status_code == 201
    refresh_token = reg_resp.json()["refresh_token"]
    
    client.cookies.set("refresh_token", refresh_token)
    response = await client.post("/api/auth/refresh")
    
    assert response.status_code == 200
    assert "access_token" in response.json()
