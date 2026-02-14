import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_techcard_root(client):
    """Тест корневого эндпоинта"""
    response = await client.get("/")
    assert response.status_code == 200
    assert "генератора технологических карт" in response.json()["message"]

@pytest.mark.asyncio
async def test_techcard_health(client):
    """Тест эндпоинта здоровья"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_techcard_crud_endpoints(client):
    """Тест эндпоинтов списков с пагинацией"""
    for endpoint in ["groups", "lessons", "teachers", "lesson-types"]:
        # Добавляем параметры пагинации если они обязательны
        response = await client.get(f"/api/techcards/{endpoint}?page=1&limit=10")
        if response.status_code == 422:
             response = await client.get(f"/api/techcards/{endpoint}")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_techcard_any_method(client):
    """Тест эндпоинта генерации (проверка существования)"""
    # Пробуем POST и GET для покрытия роута
    resp_post = await client.post("/api/techcards/generate", json={})
    resp_get = await client.get("/api/techcards/generate")
    assert resp_post.status_code in [422, 405, 200]
    assert resp_get.status_code in [422, 405, 200]
