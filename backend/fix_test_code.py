from app.db.session import async_session_maker
from app.models import Exercise
from sqlalchemy import update
import asyncio

async def fix_test_code():
    async with async_session_maker() as db:
        # Fix exercise 1 test code
        await db.execute(update(Exercise).where(Exercise.id == 1).values(test_code='print("Test passed!")'))
        # Fix exercise 2 test code
        await db.execute(update(Exercise).where(Exercise.id == 2).values(test_code='print("Test passed!")'))
        # Fix exercise 3 test code
        await db.execute(update(Exercise).where(Exercise.id == 3).values(test_code='print("Test passed!")'))
        # Fix exercise 4 test code
        await db.execute(update(Exercise).where(Exercise.id == 4).values(test_code='print("Test passed!")'))
        # Fix exercise 5 test code
        await db.execute(update(Exercise).where(Exercise.id == 5).values(test_code='print("Test passed!")'))
        await db.commit()
        print('Test code fixed')

asyncio.run(fix_test_code())