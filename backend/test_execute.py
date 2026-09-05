import asyncio
import sys
sys.path.insert(0, 'C:/Users/abdes/AtlasCode/backend')
from app.services.code_executor import execute_code

async def test():
    code = 'print("Hello, World!")'
    test_code = 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Hello, World!" in output'
    result = execute_code(code, test_code)
    print(f'success: {result.success}')
    print(f'output: {result.output}')
    print(f'error: {result.error}')
    print(f'is_correct: {result.success}')

asyncio.run(test())