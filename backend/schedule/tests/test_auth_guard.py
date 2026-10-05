import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_schedule_mutation_requires_auth(client):
    """Создание группы без токена auth-сервиса запрещено."""
    response = await client.post("/api/schedule/groups/", json={"name": "БезТокена"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_relations_mutation_requires_auth(client):
    """Создание предмета без токена auth-сервиса запрещено."""
    response = await client.post("/api/relations/subjects", json={"name": "БезТокена"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_participants_mutation_requires_auth(client):
    """Изменение участников без токена запрещено."""
    response = await client.post("/api/schedule/participants/1/participants", json={"user_id": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
