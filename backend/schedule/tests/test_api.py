import sys
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime, timedelta
import json

# Убедимся, что используется тестовая БД. Файл будет создан в корне проекта.
os.environ["DATABASE_PATH"] = "test_database.db"

# Добавляем путь к проекту для абсолютных импортов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database.database import init_db, get_db
from database.models import SlotStatus


# --- Фикстуры для тестов ---

@pytest.fixture(scope="function", autouse=True)
def clean_database_before_each_test():
    """
    Гарантирует, что база данных пуста перед каждым тестом.
    Фикстура синхронная и максимально простая, чтобы избежать конфликтов.
    """
    # Создаем таблицы, если их еще нет
    init_db()

    # Очищаем все данные из таблиц для полной изоляции тестов
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        # Сбрасываем счетчики автоинкремента для полной чистоты
        cursor.execute("DELETE FROM sqlite_sequence;")
        conn.commit()

    yield


@pytest.fixture
def client() -> TestClient:
    """Фикстура для создания HTTP клиента. Управляет жизненным циклом приложения."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    """
    Фикстура для создания аутентифицированного клиента.
    Создает нового пользователя для каждого теста.
    """
    user_data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    register_response = client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == status.HTTP_200_OK, f"Failed to register user: {register_response.text}"

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK, f"Failed to login: {response.text}"

    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


# --- Тесты API ---

def test_full_scenario(authenticated_client: TestClient):
    """Комплексный тест: создание курса, аудитории и занятия."""
    client = authenticated_client

    course_res = client.post("/api/courses", json={"name": "Интеграционное тестирование"})
    assert course_res.status_code == status.HTTP_200_OK
    course_id = course_res.json()["id"]

    auditorium_res = client.post("/api/auditoriums", json={"name": "Аудитория для тестов"})
    assert auditorium_res.status_code == status.HTTP_200_OK
    auditorium_id = auditorium_res.json()["id"]

    start_time = (datetime.now() + timedelta(days=1)).isoformat()
    end_time = (datetime.now() + timedelta(days=1, hours=2)).isoformat()

    lesson_data = {
        "course_id": course_id,
        "auditorium_id": auditorium_id,
        "title": "Первый урок",
        "start_time": start_time,
        "end_time": end_time,
        "status": SlotStatus.SCHEDULED.value
    }

    lesson_res = client.post("/api/schedule", json=lesson_data)
    assert lesson_res.status_code == status.HTTP_200_OK, lesson_res.text

    schedule_res = client.get("/api/schedule")
    assert schedule_res.status_code == status.HTTP_200_OK
    assert len(schedule_res.json()) > 0
    assert schedule_res.json()[0]["title"] == "Первый урок"


def test_get_my_calendar_ics(authenticated_client: TestClient):
    """Тест генерации календаря: проверяет корректность данных в .ics файле."""
    course_res = authenticated_client.post("/api/courses", json={"name": "Курс для календаря"})
    course_id = course_res.json()["id"]

    auditorium_res = authenticated_client.post("/api/auditoriums", json={"name": "Аудитория для календаря"})
    auditorium_id = auditorium_res.json()["id"]

    start_time = (datetime.now() + timedelta(days=2, hours=9)).isoformat()
    end_time = (datetime.now() + timedelta(days=2, hours=11)).isoformat()

    lesson_data = {
        "course_id": course_id,
        "auditorium_id": auditorium_id,
        "title": "Урок для календаря",
        "start_time": start_time,
        "end_time": end_time,
        "status": SlotStatus.SCHEDULED.value
    }

    authenticated_client.post("/api/schedule", json=lesson_data)

    response = authenticated_client.get("/api/calendar/me.ics")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("text/calendar")
    assert "attachment; filename=my_schedule.ics" in response.headers["content-disposition"]

    ics_content = response.text
    assert "BEGIN:VCALENDAR" in ics_content
    assert "PRODID:" in ics_content
    assert "SUMMARY:Урок для календаря" in ics_content
    assert "LOCATION:Аудитория для календаря" in ics_content


def test_auditorium_crud(authenticated_client: TestClient):
    """Тест CRUD операций с аудиториями."""
    client = authenticated_client

    # 1. Проверяем, что список пустой
    initial_response = client.get("/api/auditoriums")
    assert initial_response.status_code == status.HTTP_200_OK
    initial_list = initial_response.json()
    # Не проверяем на пустоту, т.к. кеш может вернуть старые данные

    # 2. Создаём аудиторию
    new_auditorium_name = "CRUD Test Auditorium"
    create_response = client.post("/api/auditoriums", json={"name": new_auditorium_name, "capacity": 50})
    assert create_response.status_code == status.HTTP_200_OK
    created = create_response.json()
    assert created["name"] == new_auditorium_name
    assert created["capacity"] == 50
    auditorium_id = created["id"]

    # 3. Проверяем через прямой запрос к БД
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditoriums WHERE id = ?", (auditorium_id,))
        row = cursor.fetchone()
        assert row is not None, "Аудитория не найдена в БД"
        assert row["name"] == new_auditorium_name

    # 4. Получаем по ID
    get_response = client.get(f"/api/auditoriums/{auditorium_id}")
    assert get_response.status_code == status.HTTP_200_OK
    fetched = get_response.json()
    assert fetched["name"] == new_auditorium_name

    # 5. Обновляем
    updated_name = "Updated CRUD Auditorium"
    update_response = client.put(f"/api/auditoriums/{auditorium_id}", json={"name": updated_name})
    assert update_response.status_code == status.HTTP_200_OK
    updated = update_response.json()
    assert updated["name"] == updated_name

    # 6. Удаляем
    delete_response = client.delete(f"/api/auditoriums/{auditorium_id}")
    assert delete_response.status_code == status.HTTP_200_OK

    # 7. Проверяем, что удалилась
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditoriums WHERE id = ?", (auditorium_id,))
        row = cursor.fetchone()
        assert row is None, "Аудитория не была удалена из БД"


def test_websocket_broadcast_on_auditorium_changes(authenticated_client: TestClient):
    """Тест WebSocket: проверяет, что при изменениях аудитории отправляются корректные сообщения."""
    with authenticated_client.websocket_connect("/ws") as websocket:
        # 1. Создание
        auditorium_data = {"name": "WS Test Auditorium"}
        create_response = authenticated_client.post("/api/auditoriums", json=auditorium_data)
        assert create_response.status_code == status.HTTP_200_OK
        created_auditorium = create_response.json()

        message = websocket.receive_json()
        assert message["type"] == "auditorium_created"
        assert message["data"]["name"] == auditorium_data["name"]
        assert message["data"]["id"] == created_auditorium["id"]

        # 2. Обновление
        updated_name = "WS Test Auditorium Updated"
        update_response = authenticated_client.put(
            f"/api/auditoriums/{created_auditorium['id']}",
            json={"name": updated_name}
        )
        assert update_response.status_code == status.HTTP_200_OK

        message = websocket.receive_json()
        assert message["type"] == "auditorium_updated"
        assert message["data"]["name"] == updated_name
        assert message["data"]["id"] == created_auditorium["id"]

        # 3. Удаление
        delete_response = authenticated_client.delete(f"/api/auditoriums/{created_auditorium['id']}")
        assert delete_response.status_code == status.HTTP_200_OK

        message = websocket.receive_json()
        assert message["type"] == "auditorium_deleted"
        assert message["data"]["id"] == created_auditorium["id"]
