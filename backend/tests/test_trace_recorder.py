import json

import pytest

from app.services.trace_recorder import record_trace, trace_to_json

BINARY_SEARCH_BUGGY = """def binary_search(arr, target):
    left, right = 0, len(arr)
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid
        else:
            right = mid
    return -1
"""


class TestRecordTrace:
    def test_records_a_step_per_executed_line(self):
        result = record_trace(BINARY_SEARCH_BUGGY, "binary_search([1, 3, 5, 7, 9], 5)")
        assert result.is_valid
        assert result.error is None
        assert len(result.steps) > 0
        assert result.steps[-1].line == 6  # the `return mid` that finds target=5 at mid=2

    def test_captures_local_variable_values_at_each_step(self):
        result = record_trace(BINARY_SEARCH_BUGGY, "binary_search([1, 3, 5, 7, 9], 5)")
        # Somewhere in the trace, mid should have been computed as 2 (the
        # midpoint of a 5-element array) with arr/target still in scope.
        assert any(
            step.locals.get("mid") == 2 and step.locals.get("target") == 5
            for step in result.steps
        )

    def test_infinite_loop_fails_safely_instead_of_hanging(self):
        # target=2 never gets found and this buggy binary_search's left/right
        # updates don't shrink the search space for it -- a real infinite loop.
        result = record_trace(BINARY_SEARCH_BUGGY, "binary_search([1, 3, 5, 7, 9], 2)")
        assert not result.is_valid
        assert "did not terminate" in result.error

    def test_syntax_error_in_buggy_code_is_reported_not_raised(self):
        result = record_trace("def broken(:\n    pass", "broken()")
        assert not result.is_valid
        assert "SyntaxError" in result.error

    def test_runtime_error_in_entry_call_is_reported(self):
        result = record_trace("def f(x):\n    return 1 / x", "f(0)")
        assert not result.is_valid
        assert "ZeroDivisionError" in result.error

    def test_trace_to_json_is_plain_serializable_dicts(self):
        result = record_trace(BINARY_SEARCH_BUGGY, "binary_search([1, 3, 5, 7, 9], 5)")
        payload = trace_to_json(result)
        assert isinstance(payload, list)
        assert all(set(step.keys()) == {"line", "locals"} for step in payload)
        json.dumps(payload)  # must not raise


class TestBreakTheCodeAuthoringHelper:
    def test_builds_a_debugging_exercise_with_a_trace_attached(self):
        from app.seed.authoring import AR, EN, FR, BreakTheCode, T, asserts

        exercise = BreakTheCode(
            prompt=T("Fix it", "Corrigez", "أصلحه"),
            hint=T("Look closely", "Regardez de près", "انظر عن كثب"),
            explanation=T("It's off by one", "Décalage d'un", "خطأ بواحد"),
            buggy_code="def double(x):\n    return x + x + 1\n",
            fix_code="def double(x):\n    return x + x\n",
            entry_call="double(3)",
            test_code=asserts("assert double(3) == 6"),
        )

        assert exercise.exercise_type.value == "debugging"
        assert exercise.starter_code.startswith("def double")
        assert "trace" in exercise.validation
        assert len(exercise.validation["trace"]) > 0
        assert exercise.validation["trace"][0]["line"] == 1

    def test_rejects_a_buggy_code_and_entry_call_that_never_terminates(self):
        from app.seed.authoring import BreakTheCode, T, asserts

        with pytest.raises(AssertionError, match="trace recording failed"):
            BreakTheCode(
                prompt=T("a", "a", "a"),
                hint=T("a", "a", "a"),
                explanation=T("a", "a", "a"),
                buggy_code="def loop():\n    while True:\n        pass\n",
                fix_code="def loop():\n    return None\n",
                entry_call="loop()",
                test_code=asserts("assert loop() is None"),
            )
