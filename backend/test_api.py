import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://127.0.0.1:8000/health')
        print(r.status_code, r.json())
        
        # Test registration
        r = await client.post('http://127.0.0.1:8000/auth/register', json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password123',
            'preferred_language': 'en'
        })
        print('Register:', r.status_code, r.text)
        
        # Test login
        r = await client.post('http://127.0.0.1:8000/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        print('Login:', r.status_code, r.json())
        token = r.json()['access_token']
        
        # Test /auth/me
        headers = {'Authorization': f'Bearer {token}'}
        r = await client.get('http://127.0.0.1:8000/auth/me', headers=headers)
        print('Auth me:', r.status_code, r.json())
        
        # Test /auth/profile
        r = await client.get('http://127.0.0.1:8000/auth/profile', headers=headers)
        print('Profile:', r.status_code, r.json())
        
        # Test courses
        headers = {'Authorization': f'Bearer {token}'}
        r = await client.get('http://127.0.0.1:8000/courses', headers=headers)
        print('Courses:', r.status_code, r.json())
        
        # Test dashboard
        r = await client.get('http://127.0.0.1:8000/dashboard', headers=headers)
        print('Dashboard:', r.status_code, r.text)
        
        # Test lessons
        r = await client.get('http://127.0.0.1:8000/lessons/1', headers=headers)
        print('Lesson 1:', r.status_code, r.json())
        
        # Test exercise run
        r = await client.post('http://127.0.0.1:8000/exercises/1/run', headers=headers, json={
            'code': 'print("Hello, World!")',
            'exercise_id': 1
        })
        print('Exercise Run:', r.status_code, r.json())
        
        # Test exercise submit
        r = await client.post('http://127.0.0.1:8000/exercises/1/submit', headers=headers, json={
            'code': 'print("Hello, World!")',
            'exercise_id': 1
        })
        print('Exercise Submit:', r.status_code, r.text)
        
        # Test course progress
        r = await client.get('http://127.0.0.1:8000/courses/1/progress', headers=headers)
        print('Course Progress:', r.status_code, r.json())
        
        # Test lesson progress
        r = await client.get('http://127.0.0.1:8000/lessons/1/progress', headers=headers)
        print('Lesson Progress:', r.status_code, r.json())
        
        # Test start lesson
        r = await client.post('http://127.0.0.1:8000/lessons/1/start', headers=headers)
        print('Start Lesson:', r.status_code, r.json())
        
        # Test projects
        r = await client.get('http://127.0.0.1:8000/projects', headers=headers)
        print('Projects:', r.status_code, r.json())
        
        # Test project detail
        r = await client.get('http://127.0.0.1:8000/projects/1', headers=headers)
        print('Project 1:', r.status_code, r.json())
        
        # Test project progress
        r = await client.get('http://127.0.0.1:8000/projects/1/progress', headers=headers)
        print('Project Progress:', r.status_code, r.json())
        
        # Test visual compile
        r = await client.post('http://127.0.0.1:8000/visual/compile', headers=headers, json={
            'nodes': [
                {'id': '1', 'type': 'start', 'config': {}},
                {'id': '2', 'type': 'variable', 'config': {'name': 'x', 'value': '10'}},
                {'id': '3', 'type': 'output', 'config': {'value': 'x'}},
                {'id': '4', 'type': 'end', 'config': {}}
            ],
            'edges': [
                {'source': '1', 'target': '2'},
                {'source': '2', 'target': '3'},
                {'source': '3', 'target': '4'}
            ]
        })
        print('Visual Compile:', r.status_code, r.json())

asyncio.run(test())