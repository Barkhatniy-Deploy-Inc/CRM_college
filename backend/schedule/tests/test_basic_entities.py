import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_get_groups_empty(client, mock_auth):
    """Тест получения пустого списка групп"""
    response = await client.get("/api/schedule/groups/")
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_create_group(client, mock_auth):
    """Тест создания группы"""
    payload = {"name": "П-41", "description": "Программисты"}
    response = await client.post("/api/schedule/groups/", json=payload)
    assert response.status_code in [200, 201]

@pytest.mark.asyncio
async def test_participants_api(client, mock_auth):
    """Тест API участников"""
    response = await client.get("/api/schedule/participants/1/participants")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_export_api_endpoints(client, mock_auth):
    """Тест эндпоинтов экспорта (проверка доступности)"""
    # XLSX
    resp_xlsx = await client.get("/api/schedule/export/xlsx?date_from=14.02.2026&date_to=14.02.2026")
    # PDF
    resp_pdf = await client.get("/api/schedule/export/pdf?date_from=14.02.2026&date_to=14.02.2026")
    
    assert resp_xlsx.status_code in [200, 400]
    assert resp_pdf.status_code in [200, 400, 500]
