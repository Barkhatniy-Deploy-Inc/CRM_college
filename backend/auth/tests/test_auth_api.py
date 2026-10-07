import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_register_user(client):
    """Тест успешной регистрации пользователя"""
    payload = {
        "email": "test_user@example.com",
        "password": "strongpassword123",
        "full_name": "Test User"
    }
    response = await client.post("/api/auth/register", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["email"] == payload["email"]
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Тест регистрации с уже существующим email"""
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "First User"
    }
    await client.post("/api/auth/register", json=payload)
    
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "уже существует" in response.json()["detail"]


@pytest.mark.asyncio
async def test_public_registration_cannot_assign_admin_role(client):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "self_admin@example.com",
            "password": "password123",
            "full_name": "Self Admin",
            "role": "admin",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_login_success(client):
    """Тест успешного входа"""
    payload = {
        "email": "login@example.com",
        "password": "correct_password",
        "full_name": "Login User"
    }
    await client.post("/api/auth/register", json=payload)
    
    login_data = {"email": payload["email"], "password": payload["password"]}
    response = await client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_logout(client, db):
    """Тест выхода из системы (проверка флага is_revoked)"""
    from database.models import RefreshToken
    payload = {"email": "logout@example.com", "password": "password123", "full_name": "Logout User"}
    reg_resp = await client.post("/api/auth/register", json=payload)
    token = reg_resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/api/auth/logout", headers=headers)
    
    # Проверка, что все токены пользователя отозваны
    tokens = db.query(RefreshToken).all()
    for t in tokens:
        assert t.is_revoked is True
