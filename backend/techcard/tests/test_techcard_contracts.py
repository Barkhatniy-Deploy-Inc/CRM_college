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


@pytest.mark.asyncio
async def test_owner_can_read_only_owned_cards(authorized_client, db):
    from database.models_techcard import TechCard

    db.add(TechCard(tema="Owned", owner_id=1))
    db.add(TechCard(tema="Private", owner_id=2))
    db.commit()

    response = await authorized_client.get("/api/techcards")

    assert response.status_code == 200
    assert [card["tema"] for card in response.json()] == ["Owned"]
