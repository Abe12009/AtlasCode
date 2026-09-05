import sys
sys.path.insert(0, '.')
import asyncio
from httpx import AsyncClient
from app.main import app

async def test():
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Register user
        response = await client.post('/auth/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123',
            'preferred_language': 'en'
        })
        token = response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Start project
        start_response = await client.post('/projects/1/start', headers=headers)
        print(f'Start project: {start_response.status_code}')
        print(f'Start response: {start_response.json()}')
        
        # Submit task
        code = '''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return "Error: Division by zero"

print(add(2, 3))'''
        
        response = await client.post('/projects/1/submit-task', headers=headers, json={
            'task_id': 1,
            'code': code
        })
        print(f'Submit task: {response.status_code}')
        print(f'Submit response: {response.json()}')

asyncio.run(test())