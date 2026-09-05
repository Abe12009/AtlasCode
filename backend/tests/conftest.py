import pytest
import asyncio
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.main import app
from app.db.session import get_db
from app.models import Base
from app.core.config import get_settings

settings = get_settings()

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_atlascode.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionMaker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestAsyncSessionMaker() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    # Drop first: an interrupted previous run leaves rows behind, and tests that
    # register fixed emails (e.g. newuser@example.com) then fail with 400.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # Seed the test database once at session start
    import sys
    sys.path.insert(0, 'C:/Users/abdes/AtlasCode/backend')
    from app.seed import seed_all
    await seed_all(TestAsyncSessionMaker)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Create a fresh session for each test."""
    async with TestAsyncSessionMaker() as session:
        yield session


@pytest.fixture
async def client():
    """Override get_db to use a fresh session for each request."""
    async def override_get_db():
        async with TestAsyncSessionMaker() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


def _random_suffix():
    return uuid.uuid4().hex[:8]


@pytest.fixture
async def test_user(client):
    suffix = _random_suffix()
    user_data = {
        "email": f"test_{suffix}@example.com",
        "username": f"testuser_{suffix}",
        "password": "password123",
        "preferred_language": "en"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"token": token, "headers": {"Authorization": f"Bearer {token}"}, "data": user_data}


@pytest.fixture
async def second_user(client):
    suffix = _random_suffix()
    user_data = {
        "email": f"test2_{suffix}@example.com",
        "username": f"testuser2_{suffix}",
        "password": "password123",
        "preferred_language": "en"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"token": token, "headers": {"Authorization": f"Bearer {token}"}, "data": user_data}