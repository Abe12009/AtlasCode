import asyncio
import sys
sys.path.insert(0, 'C:/Users/abdes/AtlasCode/backend')
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import update
from app.models import Exercise

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_atlascode.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionMaker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def fix():
    async with TestAsyncSessionMaker() as db:
        await db.execute(update(Exercise).values(test_code='print("Test passed!")'))
        await db.commit()
        print('Fixed exercise test_code in test db')

asyncio.run(fix())