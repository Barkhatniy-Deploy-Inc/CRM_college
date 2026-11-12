"""Public documentation paths must be reachable through the API gateway."""

import pytest


@pytest.mark.asyncio
async def test_techcard_docs_and_openapi_use_gateway_paths(client):
    docs = await client.get("/api/techcard/docs")
    assert docs.status_code == 200
    assert "/api/techcard/openapi.json" in docs.text

    schema = await client.get("/api/techcard/openapi.json")
    assert schema.status_code == 200
    assert "/api/techcards" in schema.json()["paths"]

    redoc = await client.get("/api/techcard/redoc")
    assert redoc.status_code == 200
    assert "/api/techcard/openapi.json" in redoc.text
