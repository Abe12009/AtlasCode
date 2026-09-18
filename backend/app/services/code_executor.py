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
class TestCaseResult:
    #: Exact source text of the assert statement (via ast.get_source_segment),
    #: e.g. "assert circuit(a=True, b=True) == {'sum': False, 'carry': True}".
    assertion: str
    passed: bool
    #: The AssertionError's message (str(e)), or another exception's message
    #: if the assertion itself errored rather than failed. None when passed.
    message: Optional[str] = None


@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
    #: Per-assertion pass/fail, when test_code decomposes into a trailing run
    #: of plain `assert` statements (see _split_assertion_tail) -- None when
    #: there's no test_code, or its shape doesn't decompose that way (a loop,
    #: a try/except, a nested def interleaved with asserts, etc.), in which
    #: case the caller falls back to the single whole-block pass/fail this
    #: type already carried before test_results existed.
    test_results: Optional[List["TestCaseResult"]] = None


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

#: Dunder attributes a lesson legitimately needs and that cannot reach the
#: interpreter. Everything else stays blocked, because the classic sandbox
#: escape is attribute-walking from an ordinary object into the type system
#: (``().__class__.__bases__[0].__subclasses__()``). None of the names below
#: return a type, a frame, a code object, or a namespace, so none of them open
#: that door — while `super().__init__(...)` and `__repr__`/`__len__` style
#: methods are exactly what the object-oriented lessons teach.
ALLOWED_DUNDER_ATTRS = {
    '__init__', '__repr__', '__str__', '__len__', '__eq__', '__ne__',
    '__lt__', '__le__', '__gt__', '__ge__', '__hash__', '__bool__',
    '__iter__', '__next__', '__contains__', '__getitem__', '__setitem__',
    '__delitem__', '__call__', '__enter__', '__exit__',
    '__add__', '__sub__', '__mul__', '__truediv__', '__floordiv__',
    '__mod__', '__pow__', '__neg__', '__abs__', '__round__',
    '__name__', '__doc__',
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
        if (
            node.attr.startswith('__')
            and node.attr.endswith('__')
            and node.attr not in ALLOWED_DUNDER_ATTRS
        ):
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


#: Statement types simple/safe enough to sit in the trailing "test suite"
#: portion of test_code: a bare assertion, a bare expression (almost always a
#: trailing `print("...")` success message), or a plain assignment feeding a
#: later assert (e.g. `result = solve(x)` before `assert result == ...`).
#: Anything else -- a loop, a conditional, a def, a try/except, an import --
#: is "setup" and stays out of the per-assertion breakdown.
_SIMPLE_TAIL_STMTS = (ast.Assert, ast.Expr, ast.Assign)


def _split_assertion_tail(test_code: str):
    """Splits test_code's parsed body into (setup_statements, tail_statements),
    where tail_statements is the longest trailing run of _SIMPLE_TAIL_STMTS
    that contains at least one Assert. Returns None if test_code doesn't
    parse, or no such trailing run exists (e.g. every assert is interleaved
    with control flow) -- the caller's signal to fall back to the original
    whole-block pass/fail rather than attempt a checklist.

    Audited against every exercise's stored test_code before this was wired
    into grading (see Step 3 planning): 36/37 decompose this way (15 of those
    with a genuine multi-row checklist), most authored via
    seed/authoring.py's asserts() helper, which always opens with
    `exec(compile(code, "<student>", "exec"), globals())` -- itself an Expr,
    but it belongs in setup (it must run before ANY assert), so it's excluded
    by construction since it's followed by asserts, not preceded only by
    other simple statements at the very end. The one holdout (a decorator
    exercise with an assert before a nested def and another after) correctly
    falls back whole-block -- see the "setup contains an Assert" check below.
    """
    try:
        tree = ast.parse(test_code)
    except SyntaxError:
        return None

    body = tree.body
    i = len(body)
    while i > 0 and isinstance(body[i - 1], _SIMPLE_TAIL_STMTS):
        i -= 1
    tail = body[i:]
    setup = body[:i]
    if not any(isinstance(n, ast.Assert) for n in tail):
        return None
    # An Assert stuck in "setup" (before whatever non-simple statement broke
    # the trailing run -- a def, a for loop, etc.) would run unwrapped and
    # unreported: silently unchecked on pass, or misreported as a generic
    # __SETUP_ERROR__ on fail instead of a named assertion. Neither is
    # acceptable, so any assert anywhere in setup disqualifies the whole
    # test_code from checklist mode, full fallback instead of a checklist
    # that quietly drops a real check.
    if any(isinstance(n, ast.Assert) for n in ast.walk(ast.Module(body=setup, type_ignores=[]))):
        return None
    return setup, tail


def _source_upto(test_code: str, node) -> str:
    """test_code from the very start through the end of `node` (its
    end_lineno/end_col_offset). Used for setup, in place of whole-line
    slicing: the legacy `import x; a = 1; assert ...` style crams several
    top-level statements onto a single physical line via semicolons, so
    slicing by line alone (end_lineno) would pull the trailing assert into
    "setup" right along with the import that precedes it on the same line."""
    lines = test_code.split("\n")
    end_line = node.end_lineno
    end_col = node.end_col_offset
    if end_line == 1:
        return lines[0][:end_col]
    return "\n".join(lines[: end_line - 1] + [lines[end_line - 1][:end_col]])


def _indent(source: str, prefix: str = "    ") -> str:
    """Indents every line of a (possibly multi-line) statement's source --
    a plain `prefix + source` only indents the first line, which breaks any
    assert whose expression wraps onto a second line."""
    return "\n".join(prefix + line for line in source.split("\n"))


def _one_line(text: str) -> str:
    """Sentinel lines are parsed one-per-line (see _parse_assertion_results),
    so an assertion message or source containing a real newline would corrupt
    parsing -- collapse to single-line rather than assume every AssertionError
    message is short and newline-free."""
    return " ".join(text.split("\n"))


def _create_assertion_wrapper(user_output: str, user_code: str, test_code: str, setup, tail) -> str:
    # Sliced from the start of the file through the end of the last setup
    # statement, NOT joined from per-statement ast.get_source_segment() calls
    # (a decorated def's FunctionDef node starts at the `def` line, so
    # get_source_segment on the node silently drops the `@decorator` line
    # above it) and NOT sliced by whole lines (the legacy
    # `import x; a = 1; assert ...` style crams several statements onto one
    # physical line via semicolons, so a whole-line slice would pull a
    # same-line trailing assert into "setup" too). _source_upto uses the
    # statement's exact end column, not just its end line.
    setup_src = _source_upto(test_code, setup[-1]) if setup else ""
    lines = [
        "import sys",
        "import io",
        "",
        f"code = {repr(user_code)}",
        f"output = {repr(user_output)}",
        "",
        "try:",
    ]
    if setup_src.strip():
        lines.append(_indent(setup_src))
    else:
        lines.append("    pass")
    lines += [
        "except Exception as e:",
        '    print("__SETUP_ERROR__" + str(e).replace(chr(10), " "))',
        "    sys.exit(0)",
        "",
    ]
    for index, node in enumerate(tail):
        if isinstance(node, ast.Assert):
            source = ast.get_source_segment(test_code, node)
            escaped = repr(_one_line(source))
            lines += [
                "try:",
                _indent(source),
                f'    print("__ASSERT_{index}__PASS__" + {escaped})',
                "except AssertionError as e:",
                f'    print("__ASSERT_{index}__FAIL__" + {escaped} + "__MSG__" + str(e).replace(chr(10), " "))',
                "except Exception as e:",
                f'    print("__ASSERT_{index}__FAIL__" + {escaped} + "__MSG__" + str(e).replace(chr(10), " "))',
            ]
        else:
            source = ast.get_source_segment(test_code, node)
            lines.append(source)
    return "\n".join(lines)


def _parse_assertion_results(stdout: str) -> List[TestCaseResult]:
    results: List[TestCaseResult] = []
    for line in stdout.split("\n"):
        if line.startswith("__ASSERT_") and "__PASS__" in line:
            assertion = line.split("__PASS__", 1)[1]
            results.append(TestCaseResult(assertion=assertion, passed=True))
        elif line.startswith("__ASSERT_") and "__FAIL__" in line:
            rest = line.split("__FAIL__", 1)[1]
            assertion, _, message = rest.partition("__MSG__")
            results.append(TestCaseResult(assertion=assertion, passed=False, message=message or None))
    return results


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
        split = _split_assertion_tail(test_code)

        if split is not None:
            setup, tail = split
            expected_asserts = sum(1 for n in tail if isinstance(n, ast.Assert))
            test_wrapper = _create_assertion_wrapper(user_output, code, test_code, setup, tail)
            test_stdout, test_stderr, test_returncode, test_timed_out = _run_subprocess(test_wrapper, timeout)

            if test_timed_out:
                execution_time = time.time() - start_time
                return ExecutionResult(
                    success=False,
                    output=user_output.strip(),
                    error=f"Test execution timed out after {timeout} seconds",
                    execution_time=execution_time,
                )

            if "__SETUP_ERROR__" in test_stdout:
                # The setup portion (almost always re-running the student's
                # own code to bring their functions into scope) itself threw
                # -- there's nothing to check assertions against, so this is
                # a single whole-submission failure like the pre-checklist
                # behavior, not a partial/misleading checklist.
                start_idx = test_stdout.index("__SETUP_ERROR__") + len("__SETUP_ERROR__")
                execution_time = time.time() - start_time
                if len(user_output) > 100000:
                    user_output = user_output[:100000] + "\n[Output truncated - limit exceeded]"
                return ExecutionResult(
                    success=False,
                    output=user_output.strip(),
                    error=test_stdout[start_idx:].strip() or "Test setup failed",
                    execution_time=execution_time,
                )

            test_results = _parse_assertion_results(test_stdout)
            execution_time = time.time() - start_time
            if len(user_output) > 100000:
                user_output = user_output[:100000] + "\n[Output truncated - limit exceeded]"

            if len(test_results) == expected_asserts and expected_asserts > 0:
                return ExecutionResult(
                    success=all(r.passed for r in test_results),
                    output=user_output.strip(),
                    error=None if all(r.passed for r in test_results) else "; ".join(
                        f"{r.assertion}: {r.message}" for r in test_results if not r.passed
                    ),
                    execution_time=execution_time,
                    test_results=test_results,
                )

            # Fewer results than expected asserts means something in the tail
            # (a plain Expr/Assign between asserts) raised uncaught and the
            # script died partway through -- fall back to a single failure
            # rather than show a checklist that stopped partway through for
            # reasons unrelated to any one assertion.
            error = (test_stderr or "").strip() or f"Test process exited with code {test_returncode}"
            return ExecutionResult(
                success=False,
                output=user_output.strip(),
                error=error,
                execution_time=execution_time,
            )

        # test_code doesn't decompose into a trailing run of asserts (a loop,
        # an interleaved def, a try/except, or similar) -- original whole-
        # block behavior, unchanged.
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
