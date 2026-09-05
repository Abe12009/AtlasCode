from app.services.code_executor import execute_code

# Test project 1 task 1 - proper validation
code = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return "Error: Division by zero"

print(add(5, 3))
"""

validation_code = """
assert add(2, 3) == 5
assert subtract(5, 3) == 2
assert multiply(3, 4) == 12
assert divide(10, 2) == 5
assert divide(5, 0) == "Error: Division by zero"
print("All tests passed!")
"""

result = execute_code(code + "\n\n" + validation_code, None)
print("Success:", result.success)
print("Output:", result.output)
print("Error:", result.error)