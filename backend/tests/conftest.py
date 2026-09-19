import pytest
import asyncio
import uuid
from httpx import ASGITransport, AsyncClient
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


@pytest.fixture(autouse=True)
def _generous_auth_rate_limits(monkeypatch):
    """httpx's ASGITransport reports every test request as coming from the
    same fixed IP (127.0.0.1) -- see its default `client` tuple -- and the
    widely-shared `test_user`/`second_user` fixtures call /auth/register on
    nearly every test in this session-scoped-DB suite, so the *real*
    per-IP register/login limits would trip from ordinary test-suite volume
    alone, not from anything an individual test is doing wrong. Raise them
    here so only a test that explicitly wants to exercise the 429 path
    monkeypatches its own limit back down (see test_auth.py), the same
    pattern password-reset's per-email limit test already uses.
    """
    monkeypatch.setattr(settings, "auth_login_rate_limit_per_email_per_hour", 100_000)
    monkeypatch.setattr(settings, "auth_login_rate_limit_per_ip_per_hour", 100_000)
    monkeypatch.setattr(settings, "auth_register_rate_limit_per_ip_per_hour", 100_000)
    monkeypatch.setattr(settings, "password_reset_rate_limit_per_ip_per_hour", 100_000)


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
def db_session_factory():
    """For tests that need several independent, concurrently-live sessions
    (e.g. simulating N separate requests racing each other against the same
    DB) rather than the single session db_session hands out -- each call
    opens its own connection against the same test database."""
    return TestAsyncSessionMaker


@pytest.fixture
async def client():
    """Override get_db to use a fresh session for each request."""
    async def override_get_db():
        async with TestAsyncSessionMaker() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def duel_ws():
    """A WebSocket-capable client for the Duel Arena tests, over the same
    in-process ASGI app + test DB as the `client` fixture.

    starlette==0.35.1's own TestClient can't be used for this: its
    WebSocket support hard-codes an httpx.Client(app=...) call that
    httpx>=0.28 (pinned here) removed in favor of transport=. httpx-ws's
    ASGIWebSocketTransport is the one already-compatible way to drive a
    real WebSocket handshake against this app in-process without standing
    up a real network server or touching either pinned version.

    Returns a `connect(path)` async context manager -- `async with
    connect(f"/duels/ws/{duel_id}?ticket={ticket}") as ws: ...` -- yielding
    an httpx_ws WebSocket session with the usual send_json/receive_json
    API. A rejected handshake (see app.api.duels.duel_websocket's
    pre-accept `websocket.close(code=...)` calls) surfaces as
    httpx_ws.WebSocketDisconnect(code, reason) from the `async with` itself.

    Deliberately NOT an async fixture that holds one shared transport open
    across the whole test (that shape hit `RuntimeError: Attempted to exit
    cancel scope in a different task than it was entered in` at teardown --
    an anyio task-group edge case in how pytest-asyncio drives async
    fixture finalizers). Each connect() call owns a fully self-contained
    transport/client/socket that opens and closes within one `async with`
    in the *test's own task*, sidestepping that entirely.
    """
    from contextlib import asynccontextmanager

    from httpx_ws import aconnect_ws
    from httpx_ws.transport import ASGIWebSocketTransport

    async def override_get_db():
        async with TestAsyncSessionMaker() as session:
            yield session

    @asynccontextmanager
    async def connect(path: str):
        app.dependency_overrides[get_db] = override_get_db
        async with ASGIWebSocketTransport(app=app) as transport:
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                async with aconnect_ws(path, client=ac) as ws:
                    yield ws

    return connect


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