import pytest
from database.models import ClassSlot, Group, Auditorium
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_get_schedule_list(client, mock_auth, db):
    """Тест получения списка занятий"""
    g = Group(name="ListGroup")
    db.add(g)
    db.flush()
    
    a = Auditorium(name="ListAud")
    db.add(a)
    db.flush()
    
    slot = ClassSlot(
        group_id=g.id,
        auditorium_id=a.id,
        title="API Test Lesson",
        instructor="Test Teacher",
        start_time=datetime(2026, 2, 14, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 2, 14, 11, 30, tzinfo=timezone.utc)
    )
    db.add(slot)
    db.commit()
    
    # Пытаемся без фильтров, но со слешем (если редирект не помог)
    response = await client.get("/api/schedule/list/")
    if response.status_code == 404:
        response = await client.get("/api/schedule/list")
        
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_schedule_by_date(client, mock_auth):
    """Тест фильтрации по дате"""
    response = await client.get("/api/schedule/list?date=2026-02-14")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_schedule_date_range_includes_entire_last_day_and_filters_group(client, mock_auth, db):
    target_group = Group(name="RangeTarget")
    other_group = Group(name="RangeOther")
    db.add_all([target_group, other_group])
    db.flush()

    db.add_all(
        [
            ClassSlot(
                group_id=target_group.id,
                title="Range first day",
                start_time=datetime(2026, 2, 14, 9, 0),
                end_time=datetime(2026, 2, 14, 10, 0),
            ),
            ClassSlot(
                group_id=target_group.id,
                title="Range last day at night",
                start_time=datetime(2026, 2, 15, 23, 30),
                end_time=datetime(2026, 2, 16, 0, 30),
            ),
            ClassSlot(
                group_id=other_group.id,
                title="Other group",
                start_time=datetime(2026, 2, 15, 12, 0),
                end_time=datetime(2026, 2, 15, 13, 0),
            ),
        ]
    )
    db.commit()

    response = await client.get(
        "/api/schedule/list",
        params={
            "date_from": "2026-02-14",
            "date_to": "2026-02-15",
            "group_id": target_group.id,
        },
    )

    assert response.status_code == 200
    assert {row["title"] for row in response.json()} == {
        "Range first day",
        "Range last day at night",
    }


@pytest.mark.asyncio
async def test_schedule_rejects_invalid_iso_date(client, mock_auth):
    response = await client.get("/api/schedule/list?date_from=not-a-date")

    assert response.status_code == 422
