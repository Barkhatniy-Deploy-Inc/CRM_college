import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.dependencies import get_techcard_db, engine_techcard
from database.models_techcard import BaseTechCard
from main import app
from httpx import AsyncClient, ASGITransport

# Использование общего движка из зависимостей (который теперь поддерживает TESTING)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_techcard)

@pytest.fixture(scope="function")
def db() -> Generator:
    BaseTechCard.metadata.create_all(bind=engine_techcard)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        BaseTechCard.metadata.drop_all(bind=engine_techcard)

@pytest.fixture(scope="function")
async def client(db) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_techcard_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
