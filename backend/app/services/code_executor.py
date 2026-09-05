import ast
import subprocess
import tempfile
import os
import time
import signal
import sys
from dataclasses import dataclass
from typing import List, Optional

try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    resource = None
    HAS_RESOURCE = False


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]


@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str]
    execution_time: float


FORBIDDEN_IMPORTS = {
    'os', 'sys', 'subprocess', 'shutil', 'pathlib', 'glob', 'pickle',
    'marshal', 'importlib', 'pkgutil', 'runpy', 'zipimport', 'ctypes',
    'multiprocessing', 'threading', 'asyncio', 'socket', 'urllib',
    'http', 'ftplib', 'telnetlib', 'smtplib', 'poplib', 'imaplib',
    'sqlite3', 'psycopg2', 'mysql', 'pymongo', 'redis', 'requests',
    'httpx', 'aiohttp', 'paramiko', 'fabric', 'ansible', 'docker',
    'kubernetes', 'boto3', 'google', 'azure', 'tensorflow', 'torch',
    'sklearn', 'cv2', 'PIL', 'numpy', 'pandas', 'matplotlib', 'scipy',
    'builtins', 'types', 'inspect', 'gc', 'weakref', 'copyreg',
    'shelve', 'dbm', 'anydbm', 'whichdb', 'dumbdbm',
    'email', 'json', 'csv', 'html', 'xml', 'html', 'xmlrpc',
    'distutils', 'ensurepip', 'venv', 'zipapp',
}

# property/staticmethod/classmethod/super are exactly what lessons 121, 124 and
# 127 teach. They cannot import, read files, or reach interpreter internals, so
# blocking them only made those lessons' exercises unsolvable.
FORBIDDEN_BUILTINS = {
    'eval', 'exec', 'compile', '__import__', 'open', 'input',
    'getattr', 'setattr', 'delattr', 'vars', 'dir', 'globals',
    'locals', 'breakpoint', 'exit', 'quit', 'help', 'license',
    'copyright', 'credits', '__build_class__',
}

ALLOWED_BUILTINS = {
    'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list',
    'dict', 'set', 'tuple', 'enumerate', 'zip', 'map', 'filter',
    'sum', 'min', 'max', 'abs', 'round', 'pow', 'divmod', 'ord',
    'chr', 'hex', 'bin', 'oct', 'isinstance', 'issubclass', 'hasattr',
    'type', 'object', 'Exception', 'ValueError', 'TypeError', 'IndexError',
    'KeyError', 'AttributeError', 'NameError', 'SyntaxError', 'ZeroDivisionError',
    'True', 'False', 'None', 'NotImplemented', 'Ellipsis', '__name__',
    '__doc__', '__package__', '__loader__', '__spec__', '__annotations__',
    'iter', 'next', 'reversed', 'sorted', 'any', 'all', 'callable',
    'format', 'id', 'hash', 'memoryview', 'slice', 'complex', 'bytes',
    'bytearray', 'frozenset',
}


class CodeValidator(ast.NodeVisitor):
    def __init__(self):
        self.errors: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            if alias.name.split('.')[0] in FORBIDDEN_IMPORTS:
                self.errors.append(f"Import '{alias.name}' is not allowed")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module and node.module.split('.')[0] in FORBIDDEN_IMPORTS:
            self.errors.append(f"Import from '{node.module}' is not allowed")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_BUILTINS:
                self.errors.append(f"Use of '{node.func.id}' is not allowed")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_BUILTINS:
                self.errors.append(f"Use of '{node.func.attr}' is not allowed")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr.startswith('__') and node.attr.endswith('__'):
            self.errors.append(f"Access to dunder attribute '{node.attr}' is not allowed")
        forbidden_attrs = {
            'system', 'popen', 'spawn', 'fork', 'exec', 'kill',
            'environ', 'getenv', 'putenv', 'unsetenv',
            'listdir', 'mkdir', 'rmdir', 'remove', 'unlink', 'rename',
            'read', 'write', 'open', 'close', 'seek', 'tell',
            'connect', 'bind', 'listen', 'accept', 'send', 'recv',
            'gethostbyname', 'gethostname', 'socket',
        }
        if node.attr in forbidden_attrs:
            self.errors.append(f"Access to '{node.attr}' is not allowed")
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        if isinstance(node.value, ast.Name) and node.value.id in {'globals', 'locals', 'vars'}:
            self.errors.append(f"Access to '{node.value.id}' via subscript is not allowed")
        self.generic_visit(node)

    def visit_Starred(self, node: ast.Starred):
        if isinstance(node.value, ast.Name) and node.value.id in {'globals', 'locals'}:
            self.errors.append(f"Unpacking '{node.value.id}' is not allowed")
        self.generic_visit(node)


def validate_python_code(code: str) -> ValidationResult:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ValidationResult(is_valid=False, errors=[f"Syntax error: {e.msg}"])

    validator = CodeValidator()
    validator.visit(tree)

    return ValidationResult(is_valid=len(validator.errors) == 0, errors=validator.errors)


def _create_sandboxed_user_code(user_code: str) -> str:
    return f"""import sys
import io

# Limit output size
MAX_OUTPUT_SIZE = 100000

class LimitedStringIO(io.StringIO):
    def __init__(self, max_size=MAX_OUTPUT_SIZE):
        super().__init__()
        self.max_size = max_size
        self._size = 0

    def write(self, s):
        self._size += len(s)
        if self._size > self.max_size:
            raise ValueError(f"Output limit exceeded (max {{self.max_size}} characters)")
        return super().write(s)

stdout_capture = LimitedStringIO()
stderr_capture = LimitedStringIO()

stdout_original = sys.stdout
stderr_original = sys.stderr

sys.stdout = stdout_capture
sys.stderr = stderr_capture

# Remove dangerous builtins from __builtins__
if isinstance(__builtins__, dict):
    safe_builtins = {{k: v for k, v in __builtins__.items() if k not in {{
        'eval', 'exec', 'compile', '__import__', 'open', 'input',
        'getattr', 'setattr', 'delattr', 'vars', 'dir', 'globals',
        'locals', 'breakpoint', 'exit', 'quit', 'help', 'license',
        'copyright', 'credits', '__build_class__',
    }}}}
    __builtins__ = safe_builtins
else:
    safe_builtins = {{}}
    for name in dir(__builtins__):
        if name not in {{
            'eval', 'exec', 'compile', '__import__', 'open', 'input',
            'getattr', 'setattr', 'delattr', 'vars', 'dir', 'globals',
            'locals', 'breakpoint', 'exit', 'quit', 'help', 'license',
            'copyright', 'credits', '__build_class__',
        }}:
            safe_builtins[name] = getattr(__builtins__, name)
    __builtins__ = safe_builtins

# Remove dangerous modules from sys.modules
dangerous_modules = {{
    'os', 'sys', 'subprocess', 'shutil', 'pathlib', 'glob', 'pickle',
    'marshal', 'importlib', 'pkgutil', 'runpy', 'zipimport', 'ctypes',
    'multiprocessing', 'threading', 'asyncio', 'socket', 'urllib',
    'http', 'ftplib', 'telnetlib', 'smtplib', 'poplib', 'imaplib',
    'sqlite3', 'psycopg2', 'mysql', 'pymongo', 'redis', 'requests',
    'httpx', 'aiohttp', 'paramiko', 'fabric', 'ansible', 'docker',
    'kubernetes', 'boto3', 'google', 'azure', 'tensorflow', 'torch',
    'sklearn', 'cv2', 'PIL', 'numpy', 'pandas', 'matplotlib', 'scipy',
    'builtins', 'types', 'inspect', 'gc', 'weakref', 'copyreg',
    'shelve', 'dbm', 'anydbm', 'whichdb', 'dumbdbm',
    'email', 'json', 'csv', 'html', 'xml', 'html', 'xmlrpc',
    'distutils', 'ensurepip', 'venv', 'zipapp',
}}
# Deleting these from the module cache adds no protection -- user code cannot
# import them anyway (the AST validator rejects it and restricted_import blocks
# it at runtime) -- but dropping 'sys' broke every stdlib module that touches
# sys.modules while initialising, which is why `import collections`, `random`,
# `functools`, `decimal` and `statistics` all raised.
cache_keep = {{'sys', 'builtins', 'types'}}
for mod in dangerous_modules - cache_keep:
    if mod in sys.modules:
        del sys.modules[mod]

# Prevent re-importing dangerous modules
original_import = __builtins__['__import__'] if '__import__' in __builtins__ else None

def restricted_import(name, *args, **kwargs):
    if name.split('.')[0] in dangerous_modules:
        raise ImportError(f"Import of '{{name}}' is not allowed")
    if original_import:
        return original_import(name, *args, **kwargs)
    raise ImportError(f"Import of '{{name}}' is not allowed")

__builtins__['__import__'] = restricted_import

try:
{chr(10).join('    ' + line for line in user_code.split(chr(10)))}
finally:
    sys.stdout = stdout_original
    sys.stderr = stderr_original
    output = stdout_capture.getvalue()
    error_output = stderr_capture.getvalue()
    print("__OUTPUT__" + output + "__END_OUTPUT__")
    if error_output:
        print("__ERROR__" + error_output + "__END_ERROR__")
"""


def _create_test_code_wrapper(user_output: str, user_code: str, test_code: str) -> str:
    return f"""import sys
import io

code = {repr(user_code)}
output = {repr(user_output)}

try:
{chr(10).join('    ' + line for line in test_code.split(chr(10)))}
    print("__TEST_PASSED__")
except AssertionError as e:
    print("__TEST_FAILED__" + str(e))
except Exception as e:
    print("__TEST_ERROR__" + str(e))
"""


def _run_subprocess(python_code: str, timeout: float) -> tuple[str, str, int, bool]:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(python_code)
        temp_path = f.name

    def preexec_fn():
        if HAS_RESOURCE and resource:
            try:
                resource.setrlimit(resource.RLIMIT_CPU, (int(timeout) + 1, int(timeout) + 1))
                resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
                resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
            except Exception:
                pass
        try:
            os.setpgrp()
        except Exception:
            pass

    try:
        result = subprocess.run(
            [sys.executable, '-I', '-S', '-s', temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),
            preexec_fn=preexec_fn if hasattr(os, 'setpgrp') else None,
        )
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode
        timed_out = False
    except subprocess.TimeoutExpired:
        stdout = ""
        stderr = f"Execution timed out after {timeout} seconds"
        returncode = -1
        timed_out = True
    except Exception as e:
        stdout = ""
        stderr = f"Execution error: {str(e)}"
        returncode = -1
        timed_out = False
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    return stdout, stderr, returncode, timed_out


def execute_code(code: str, test_code: Optional[str] = None, timeout: float = 5.0) -> ExecutionResult:
    start_time = time.time()

    user_code_wrapper = _create_sandboxed_user_code(code)
    stdout, stderr, returncode, timed_out = _run_subprocess(user_code_wrapper, timeout)

    user_output = ""
    user_error = None

    if "__OUTPUT__" in stdout and "__END_OUTPUT__" in stdout:
        start_idx = stdout.index("__OUTPUT__") + len("__OUTPUT__")
        end_idx = stdout.index("__END_OUTPUT__")
        user_output = stdout[start_idx:end_idx]

    if "__ERROR__" in stdout and "__END_ERROR__" in stdout:
        start_idx = stdout.index("__ERROR__") + len("__ERROR__")
        end_idx = stdout.index("__END_ERROR__")
        user_error = stdout[start_idx:end_idx]

    if timed_out:
        execution_time = time.time() - start_time
        return ExecutionResult(
            success=False,
            output="",
            error=f"Execution timed out after {timeout} seconds",
            execution_time=execution_time
        )

    # If process exited with error, capture stderr as error
    if returncode != 0:
        if not user_error and stderr:
            user_error = stderr.strip()
        execution_time = time.time() - start_time
        return ExecutionResult(
            success=False,
            output=user_output.strip(),
            error=user_error.strip() if user_error else f"Process exited with code {returncode}",
            execution_time=execution_time
        )

    if test_code:
        test_wrapper = _create_test_code_wrapper(user_output, code, test_code)
        test_stdout, test_stderr, test_returncode, test_timed_out = _run_subprocess(test_wrapper, timeout)

        if test_timed_out:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output=user_output.strip(),
                error=f"Test execution timed out after {timeout} seconds",
                execution_time=execution_time
            )

        if "__TEST_PASSED__" in test_stdout:
            success = True
            error = None
        elif "__TEST_FAILED__" in test_stdout:
            success = False
            start_idx = test_stdout.index("__TEST_FAILED__") + len("__TEST_FAILED__")
            error = test_stdout[start_idx:].strip()
        elif "__TEST_ERROR__" in test_stdout:
            success = False
            start_idx = test_stdout.index("__TEST_ERROR__") + len("__TEST_ERROR__")
            error = test_stdout[start_idx:].strip()
        elif test_returncode == 0:
            success = True
            error = None
        else:
            success = False
            error = test_stderr.strip() or f"Test process exited with code {test_returncode}"

        execution_time = time.time() - start_time

        if len(user_output) > 100000:
            user_output = user_output[:100000] + "\n[Output truncated - limit exceeded]"

        return ExecutionResult(
            success=success,
            output=user_output.strip(),
            error=error,
            execution_time=execution_time
        )

    execution_time = time.time() - start_time

    if len(user_output) > 100000:
        user_output = user_output[:100000] + "\n[Output truncated - limit exceeded]"

    return ExecutionResult(
        success=(user_error is None and returncode == 0),
        output=user_output.strip(),
        error=user_error.strip() if user_error else None,
        execution_time=execution_time
    )


def execute_code_subprocess(code: str, test_code: Optional[str] = None, timeout: float = 5.0) -> ExecutionResult:
    return execute_code(code, test_code, timeout)
