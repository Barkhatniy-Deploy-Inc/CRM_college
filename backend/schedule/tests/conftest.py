import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.database import Base, get_db
from main import app
from httpx import AsyncClient, ASGITransport
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
async def client(db) -> Generator:
    # Инициализация кэша для тестов
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache-test")
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Включаем follow_redirects=True для стабильности тестов
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def mock_auth(monkeypatch):
    """Мок для зависимостей авторизации.

    Роутеры используют `dependencies.get_current_user`, поэтому переопределяем
    именно её (а не `routers.auth.get_current_user`).
    """
    from dependencies import get_current_user

    class MockUser:
        def __init__(self):
            self.id = 1
            self.email = "test@test.ru"
            self.role = "admin"
            self.is_active = True

    async def mock_get_current_user():
        return MockUser()

    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)
