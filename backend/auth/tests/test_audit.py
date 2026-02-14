import pytest
import time
from database.models import AuditAction, AuditLog

@pytest.mark.asyncio
async def test_audit_logging(client, db):
    """Тест автоматического логирования действий в аудит"""
    unique_email = f"audit_{time.time()}@example.com"
    payload = {
        "email": unique_email,
        "password": "password123",
        "full_name": "Audit User"
    }
    await client.post("/api/auth/register", json=payload)
    
    logs = db.query(AuditLog).all()
    assert len(logs) >= 1
    registration_log = next((log for log in logs if log.action == AuditAction.USER_CREATED), None)
    assert registration_log is not None

@pytest.mark.asyncio
async def test_get_audit_logs_admin(client, db):
    """Тест получения логов аудита администратором"""
    from services.security import hash_password
    from database.models import User, UserRole
    
    unique_admin = f"admin_audit_{time.time()}@college.ru"
    admin = User(
        email=unique_admin,
        password_hash=hash_password("adminpass"),
        full_name="Audit Admin",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    db.commit()
    
    login_resp = await client.post("/api/auth/login", json={
        "email": unique_admin,
        "password": "adminpass"
    })
    token = login_resp.json()["access_token"]
    
    # Исправленный эндпоинт
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/users/audit-log/all", headers=headers)
    
    assert response.status_code == 200
    assert "logs" in response.json()
