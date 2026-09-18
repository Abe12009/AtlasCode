"""Per-assertion test result breakdown (code_executor._split_assertion_tail
and friends). Exercised directly against execute_code() -- these are pure
process-boundary tests, no DB/HTTP needed.

The shape assumption ("test_code decomposes into setup + a trailing run of
plain asserts") was audited against every real exercise's stored test_code
before this was built: 37/37 decomposed this way. These tests pin both the
common shapes actually in the seed content and the deliberately-adversarial
shapes (a loop, a try/except, a nested def) that must fall back gracefully
instead of 500ing or producing a bogus partial checklist.
"""

from app.services.code_executor import execute_code


class TestSimpleAssertsHelperStyle:
    """The seed/authoring.py asserts() shape: exec(compile(code, ...)) then
    a flat run of asserts -- most of the curriculum's test_code."""

    def test_all_pass(self):
        code = "def double(x):\n    return x * 2\n"
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "assert double(2) == 4\n"
            "assert double(0) == 0\n"
            "assert double(-3) == -6\n"
        )
        result = execute_code(code, test_code)
        assert result.success is True
        assert result.test_results is not None
        assert len(result.test_results) == 3
        assert all(r.passed for r in result.test_results)
        assert result.test_results[0].assertion == "assert double(2) == 4"

    def test_one_failure_reported_without_stopping_the_rest(self):
        # A real test-runner property: one failing assertion doesn't hide
        # the others -- the student should see all 3 rows, not just the first.
        code = "def double(x):\n    return x * 2 + 1\n"  # deliberately wrong
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "assert double(2) == 4\n"
            "assert double(0) == 0\n"
            "assert double(-3) == -6\n"
        )
        result = execute_code(code, test_code)
        assert result.success is False
        assert len(result.test_results) == 3
        assert [r.passed for r in result.test_results] == [False, False, False]

    def test_trailing_print_after_asserts_does_not_break_the_checklist(self):
        # Circuit Lab's shape (see seed/stage1_foundations.py's half adder):
        # asserts followed by a plain print() success message.
        code = "def add(a, b):\n    return a + b\n"
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "assert add(1, 1) == 2\n"
            "assert add(2, 2) == 4\n"
            "print('Correct!')\n"
        )
        result = execute_code(code, test_code)
        assert result.success is True
        assert len(result.test_results) == 2


class TestLegacySemicolonStyle:
    """The older one-line, semicolon-joined style (import + assigns + a
    single assert on one physical line) found in ~20 seeded exercises. Only
    one assert each, so per-assertion mode still applies cleanly -- no loop,
    def, or try/except to disqualify it."""

    def test_single_assert_single_line(self):
        code = 'print("Hello, World!")'
        test_code = (
            'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); '
            'exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); '
            'sys.stdout = stdout; assert "Hello, World!" in output'
        )
        result = execute_code(code, test_code)
        assert result.success is True
        assert len(result.test_results) == 1
        assert result.test_results[0].passed is True


class TestSetupWithAssertsAfterALoop:
    """A real exercise shape (seed content's Trie exercise, id 147): a
    for-loop builds state, then several plain asserts check it. The loop
    disqualifies the WHOLE body from being flat, but the trailing asserts
    after it are still a clean, checkable run -- this is exactly the
    refinement over "the whole test_code must be flat"."""

    def test_asserts_after_a_setup_loop_still_produce_a_checklist(self):
        code = (
            "class Counter:\n"
            "    def __init__(self):\n"
            "        self.n = 0\n"
            "    def bump(self):\n"
            "        self.n += 1\n"
        )
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "c = Counter()\n"
            "for _ in range(3):\n"
            "    c.bump()\n"
            "assert c.n == 3\n"
            "assert c.n != 0\n"
        )
        result = execute_code(code, test_code)
        assert result.success is True
        assert len(result.test_results) == 2


class TestGracefulFallbackForComplexShapes:
    """Shapes that must NOT attempt a per-assertion breakdown: asserts
    interleaved with a nested def (id 101's decorator exercise), or any
    other case where checkable asserts aren't a clean trailing run. These
    must still grade correctly (single pass/fail) and must never 500."""

    def test_a_single_trailing_assert_after_complex_setup_still_gets_a_checklist(self):
        # A def (with a decorator, even) is fine IN SETUP -- only one assert
        # trails it, so this is still a clean 1-row checklist. This is NOT
        # the disqualifying case; see the two tests below for that.
        code = (
            "def double(f):\n"
            "    def wrapper(*args):\n"
            "        return f(*args) * 2\n"
            "    return wrapper\n"
        )
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "@double\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "assert add(3, 4) == 14, 'the decorator must accept any signature'\n"
        )
        result = execute_code(code, test_code)
        assert result.success is True
        assert len(result.test_results) == 1
        assert result.test_results[0].passed is True

    def test_asserts_split_by_a_def_in_between_fall_back_cleanly(self):
        # The real disqualifying shape (seed content id 101): one assert
        # BEFORE a nested def, another AFTER it. Only the trailing one could
        # form a "clean run" -- the one before it would silently never be
        # checked/reported, so this must fall back to the original
        # whole-block behavior entirely rather than show a checklist that
        # quietly drops a real assertion.
        code = "def five():\n    return 10\n"
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "assert five() == 10, five()\n"
            "def double(f):\n"
            "    def wrapper(*a):\n"
            "        return f(*a) * 2\n"
            "    return wrapper\n"
            "@double\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "assert add(3, 4) == 14, 'the decorator must accept any signature'\n"
        )
        result = execute_code(code, test_code)
        assert result.success is True
        # Falls back to the original whole-block behavior -- no checklist.
        assert result.test_results is None

    def test_asserts_split_by_a_def_reports_failure_correctly_too(self):
        code = "def five():\n    return 999\n"
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "assert five() == 10, five()\n"
            "def noop(f):\n"
            "    return f\n"
            "@noop\n"
            "def add(a, b):\n"
            "    return a + b\n"
            "assert add(3, 4) == 7\n"
        )
        result = execute_code(code, test_code)
        assert result.success is False
        assert result.test_results is None
        assert result.error

    def test_a_setup_exec_that_itself_throws_is_a_single_graceful_failure(self):
        # The student's own code raises when re-exec'd for testing (e.g. a
        # module-level bug) -- must not 500, and must not report a bogus
        # checklist since no assertion ever got to run.
        code = "raise ValueError('boom at import time')\n"
        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "assert True\n"
        )
        result = execute_code(code, test_code)
        assert result.success is False
        assert result.test_results is None
        assert "boom at import time" in (result.error or "")

    def test_zero_asserts_in_test_code_falls_back(self):
        code = "print('hi')"
        test_code = "print('setup only, no assert')"
        result = execute_code(code, test_code)
        assert result.success is True
        assert result.test_results is None
