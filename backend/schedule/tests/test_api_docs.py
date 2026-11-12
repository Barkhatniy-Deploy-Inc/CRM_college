"""Public documentation paths must be reachable through the API gateway."""

import pytest


@pytest.mark.asyncio
async def test_schedule_docs_and_openapi_use_gateway_paths(client):
    docs = await client.get("/api/schedule/docs")
    assert docs.status_code == 200
    assert "/api/schedule/openapi.json" in docs.text

    schema = await client.get("/api/schedule/openapi.json")
    assert schema.status_code == 200
    assert "/api/schedule/list" in schema.json()["paths"]

    redoc = await client.get("/api/schedule/redoc")
    assert redoc.status_code == 200
    assert "/api/schedule/openapi.json" in redoc.text
