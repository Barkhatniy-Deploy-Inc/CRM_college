"""Public documentation paths must be reachable through the API gateway."""

import pytest


@pytest.mark.asyncio
async def test_auth_docs_and_openapi_use_gateway_paths(client):
    docs = await client.get("/api/auth/docs")
    assert docs.status_code == 200
    assert "/api/auth/openapi.json" in docs.text

    schema = await client.get("/api/auth/openapi.json")
    assert schema.status_code == 200
    assert "/api/auth/login" in schema.json()["paths"]

    redoc = await client.get("/api/auth/redoc")
    assert redoc.status_code == 200
    assert "/api/auth/openapi.json" in redoc.text
