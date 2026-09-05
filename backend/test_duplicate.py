import asyncio
import sys
sys.path.insert(0, 'C:/Users/abdes/AtlasCode/backend')
from httpx import AsyncClient
from app.main import app
from app.db.session import get_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models import Base
from seed import seed_data
from app.core.config import get_settings

settings = get_settings()
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_atlascode.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionMaker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def test():
    async with TestAsyncSessionMaker() as session:
        from seed import seed_data
        await seed_data(TestAsyncSessionMaker)
    
    async def get_db_override():
        async with TestAsyncSessionMaker() as session:
            yield session
    
    from app.main import app
    from app.db.session import get_db
    app.dependency_overrides[get_db] = get_db_override
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        response = await client.post("/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
            "preferred_language": "en"
        })
        print("Register: " + str(response.status_code))
        token = response.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        
        # First submission
        response = await client.post("/exercises/1/submit", headers=headers, json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        print("First submit: " + str(response.status_code))
        result = response.json()
        print("First result: " + str(result))
        
        # Second submission
        response = await client.post("/exercises/1/submit", headers=headers, json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        print("Second submit: " + str(response.status_code))
        result = response.json()
        print("Second result: " + str(result))

asyncio.run(test())