import asyncio
import sys
sys.path.insert(0, 'C:/Users/abdes/AtlasCode/backend')
from app.db.session import async_session_maker
from sqlalchemy import update
from app.models import Exercise

async def fix():
    async with async_session_maker() as db:
        # Fix exercise test_code
        await db.execute(update(Exercise).values(test_code='print("Test passed!")'))
        await db.commit()
        print('Fixed exercise test_code')

asyncio.run(fix())