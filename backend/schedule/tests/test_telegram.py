import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from fastapi import status

# Убедимся, что используется тестовая БД
os.environ["DATABASE_PATH"] = "./test_database.db"

# Импорты теперь абсолютные относительно текущей директории (backend)
from backend.main import app
from database.database import init_db

# --- Фикстуры для тестов ---

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Создает и очищает тестовую базу данных перед и после тестов."""
    db_path = "./test_database.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()
    yield
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def client() -> TestClient:
    """Фикстура для создания HTTP клиента."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    """Фикстура для создания аутентифицированного клиента."""
    user_data = {
        "email": "telegram_test@example.com",
        "password": "password123",
        "full_name": "Telegram Test User"
    }
    client.post("/api/auth/register", json=user_data)
    
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/auth/login", json=login_data)
    
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client

# --- Тесты Telegram ---

def test_subscribe_telegram_notification(authenticated_client: TestClient):
    """Тест подписки на Telegram уведомления."""
    telegram_id = "123456789" # Пример Telegram ID
    response = authenticated_client.post(f"/api/notifications/subscribe-telegram?telegram_id={telegram_id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Telegram подписка активирована"
    assert response.json()["telegram_id"] == telegram_id
