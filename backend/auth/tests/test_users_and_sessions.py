import pytest
from fastapi import status
from database.models import UserRole, User
import time

@pytest.mark.asyncio
async def test_update_user_profile(client):
    """Тест обновления профиля пользователя"""
    unique_email = f"update_{time.time()}@example.com"
    payload = {
        "email": unique_email,
        "password": "password123",
        "full_name": "Before Update"
    }
    reg_resp = await client.post("/api/auth/register", json=payload)
    token = reg_resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"full_name": "After Update"}
    response = await client.put("/api/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "After Update"

@pytest.mark.asyncio
async def test_get_sessions(client):
    """Тест получения списка активных сессий"""
    unique_email = f"sessions_{time.time()}@example.com"
    payload = {
        "email": unique_email,
        "password": "password123",
        "full_name": "Session User"
    }
    reg_resp = await client.post("/api/auth/register", json=payload)
    token = reg_resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/auth/sessions", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1

@pytest.mark.asyncio
async def test_admin_get_user_by_id(client, db):
    """Тест получения пользователя по ID (админом)"""
    from services.security import hash_password
    unique_admin = f"admin_get_{time.time()}@college.ru"
    unique_user = f"user_get_{time.time()}@college.ru"
    admin = User(email=unique_admin, password_hash=hash_password("adminpass"), 
                 full_name="Admin", role=UserRole.ADMIN, is_active=True)
    user = User(email=unique_user, password_hash=hash_password("userpass"), 
                full_name="User", role=UserRole.STUDENT, is_active=True)
    db.add(admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    login_resp = await client.post("/api/auth/login", json={"email": unique_admin, "password": "adminpass"})
    token = login_resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/users/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == unique_user

@pytest.mark.asyncio
async def test_admin_search_with_filters(client, db):
    """Тест расширенного поиска пользователей с фильтрами"""
    from services.security import hash_password
    unique_admin = f"admin_search_{time.time()}@college.ru"
    admin = User(email=unique_admin, password_hash=hash_password("adminpass"), 
                 role=UserRole.ADMIN, is_active=True, full_name="Admin Search")
    db.add(admin)
    db.commit()
    
    login_resp = await client.post("/api/auth/login", json={"email": unique_admin, "password": "adminpass"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Поиск по роли
    response = await client.get("/api/users?role=admin", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    
    # Поиск по активности
    response = await client.get("/api/users?is_active=true", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1

@pytest.mark.asyncio
async def test_deactivate_user(client, db):
    """Тест деактивации пользователя администратором через PUT"""
    from services.security import hash_password
    unique_admin = f"admin_deact_{time.time()}@college.ru"
    unique_user = f"user_deact_{time.time()}@college.ru"
    admin = User(email=unique_admin, password_hash=hash_password("adminpass"), 
                 role=UserRole.ADMIN, is_active=True, full_name="Admin")
    user = User(email=unique_user, password_hash=hash_password("userpass"), 
                role=UserRole.STUDENT, is_active=True, full_name="User")
    db.add(admin)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    login_resp = await client.post("/api/auth/login", json={"email": unique_admin, "password": "adminpass"})
    token = login_resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.put(f"/api/users/{user.id}", json={"is_active": False}, headers=headers)
    assert response.status_code == 200
    
    db.refresh(user)
    assert user.is_active is False
