import pytest

from routers import techcard_router


@pytest.mark.asyncio
async def test_create_techcard_uses_schedule_instructor_id(authorized_client, monkeypatch):
    """Автозаполнение использует числовой instructor_id из schedule-контракта."""

    async def get_lesson_data(_: int):
        return {"title": "Алгебра", "instructor_id": 42}

    monkeypatch.setattr(techcard_router, "get_lesson_data", get_lesson_data)

    response = await authorized_client.post(
        "/api/techcards",
        json={"tema": "Черновик", "lesson_id": 7, "stages": []},
    )

    assert response.status_code == 201
    assert response.json()["tema"] == "Алгебра"
    assert response.json()["teacher_id"] == 42
