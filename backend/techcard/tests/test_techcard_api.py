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
    response = await client.get("/api/techcard/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_techcard_list_requires_auth(client):
    """Список техкарт недоступен без токена (401 или 503 без SECRET_KEY)."""
    response = await client.get("/api/techcards")
    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_503_SERVICE_UNAVAILABLE,
    ]


@pytest.mark.asyncio
async def test_techcard_download_requires_auth(client):
    """Скачивание техкарты недоступно без токена."""
    response = await client.get("/api/techcards/download/1")
    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_503_SERVICE_UNAVAILABLE,
    ]
