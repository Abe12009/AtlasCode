"""Grading strategies for every exercise type.

Before this module the only grader was "run the submitted Python and see if it
raised" -- which meant any exercise without ``test_code`` (multiple choice,
prediction, fill-in-the-blank, ordering) awarded full XP for any code that
merely executed. Each type now has an explicit strategy that checks the
student's answer against the stored expected answer.

The strategy is chosen from the exercise's type plus the data it actually
carries, so a malformed exercise surfaces as ``UNGRADABLE`` instead of silently
passing everyone.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from app.models import ExerciseTypeEnum
from app.services.code_executor import execute_code, validate_python_code

# Strategy identifiers, also used by the audit script.
STRATEGY_SANDBOX = "sandbox"
STRATEGY_OPTION = "option"
STRATEGY_ORDERING = "ordering"
STRATEGY_EXPECTED_OUTPUT = "expected_output"
STRATEGY_EXPECTED_KEYWORDS = "expected_keywords"
STRATEGY_BLANKS = "blanks"
UNGRADABLE = "ungradable"

#: Types whose answer is free text (a prediction) rather than runnable code.
TEXT_ANSWER_TYPES = {ExerciseTypeEnum.prediction}


@dataclass
class GradingResult:
    is_correct: bool
    strategy: str
    output: str = ""
    error: Optional[str] = None
    feedback: str = ""
    details: dict[str, Any] = field(default_factory=dict)


def parse_validation_config(raw: Optional[str]) -> dict[str, Any]:
    """Return the exercise's validation_config, or {} when absent/malformed."""
    if not raw or not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def resolve_strategy(exercise, options: Sequence[Any] = ()) -> str:
    """Decide how an exercise must be graded, without grading it.

    Shared by the grader and the curriculum audit so both agree on exactly
    which exercises are gradable.
    """
    config = parse_validation_config(getattr(exercise, "validation_config", None))
    etype = exercise.exercise_type
    has_test = bool((exercise.test_code or "").strip())

    if etype == ExerciseTypeEnum.multiple_choice:
        correct = [o for o in options if o.is_correct]
        return STRATEGY_OPTION if len(correct) == 1 and len(options) >= 2 else UNGRADABLE

    if etype == ExerciseTypeEnum.ordering:
        return STRATEGY_ORDERING if len(options) >= 2 else UNGRADABLE

    if etype == ExerciseTypeEnum.fill_blank:
        blanks = config.get("blanks")
        return STRATEGY_BLANKS if isinstance(blanks, list) and blanks else UNGRADABLE

    if etype in TEXT_ANSWER_TYPES:
        if isinstance(config.get("expected_output"), str):
            return STRATEGY_EXPECTED_OUTPUT
        if config.get("expected_keywords"):
            return STRATEGY_EXPECTED_KEYWORDS
        return UNGRADABLE

    # code_writing, debugging, visual_programming: the existing sandbox stays
    # the source of truth wherever real tests exist.
    if has_test:
        return STRATEGY_SANDBOX
    if config.get("expected_keywords"):
        return STRATEGY_EXPECTED_KEYWORDS
    return UNGRADABLE


def _normalize_text(value: str) -> str:
    """Collapse the differences that should not decide correctness."""
    text = (value or "").replace("\r\n", "\n").strip()
    return "\n".join(line.rstrip() for line in text.split("\n")).strip()


def _normalize_blank(value: str) -> str:
    """Blank answers are stored inconsistently: some carry the surrounding
    quotes from the snippet, some do not. Compare without them so both a
    quoted and an unquoted answer is accepted."""
    text = (value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        text = text[1:-1]
    return text.strip()


def _grade_option(options, request) -> GradingResult:
    correct = next((o for o in options if o.is_correct), None)
    selected = request.selected_option_id
    if selected is None:
        return GradingResult(
            is_correct=False, strategy=STRATEGY_OPTION,
            error="No option selected",
            feedback="Select an answer before submitting.",
        )
    if selected not in {o.id for o in options}:
        return GradingResult(
            is_correct=False, strategy=STRATEGY_OPTION,
            error="Invalid option",
            feedback="That option does not belong to this exercise.",
        )
    is_correct = correct is not None and selected == correct.id
    return GradingResult(
        is_correct=is_correct, strategy=STRATEGY_OPTION,
        feedback="Correct answer!" if is_correct else "That is not the right answer.",
        error=None if is_correct else "Incorrect answer",
    )


def _grade_ordering(options, request) -> GradingResult:
    expected = [o.id for o in sorted(options, key=lambda o: o.order)]
    submitted = list(request.ordered_option_ids or [])
    if not submitted:
        return GradingResult(
            is_correct=False, strategy=STRATEGY_ORDERING,
            error="No ordering submitted",
            feedback="Arrange the steps before submitting.",
        )
    if sorted(submitted) != sorted(expected):
        return GradingResult(
            is_correct=False, strategy=STRATEGY_ORDERING,
            error="Invalid ordering",
            feedback="The submitted steps do not match this exercise.",
        )
    is_correct = submitted == expected
    return GradingResult(
        is_correct=is_correct, strategy=STRATEGY_ORDERING,
        feedback="Correct order!" if is_correct else "The steps are not in the right order.",
        error=None if is_correct else "Incorrect order",
    )


def _grade_expected_output(config, request) -> GradingResult:
    expected = config["expected_output"]
    answer = request.answer if request.answer is not None else (request.code or "")
    is_correct = _normalize_text(answer) == _normalize_text(expected)
    return GradingResult(
        is_correct=is_correct, strategy=STRATEGY_EXPECTED_OUTPUT,
        output=answer,
        feedback="Correct prediction!" if is_correct else "That is not what this code prints.",
        error=None if is_correct else "Incorrect prediction",
    )


def _normalize_for_keywords(text: str) -> str:
    """Fold the differences that should never decide a keyword match.

    Whitespace runs collapse (so ``age >= 20`` matches ``age  >=  20`` and a
    line break), and matching is case-insensitive. Nothing else is folded: the
    tokens themselves must genuinely appear.
    """
    return " ".join((text or "").lower().split())


def _grade_expected_keywords(config, request) -> GradingResult:
    """Every entry must appear. An entry may itself be a list of alternatives,
    of which any one satisfies it.

    Alternatives matter for answers that have several equally correct spellings
    -- ``O(n^2)``, ``n²`` and "quadratic" are the same answer -- and requiring
    all of them at once made those exercises impossible to pass.
    """
    raw = config.get("expected_keywords") or []
    answer = request.answer if request.answer is not None else (request.code or "")
    haystack = _normalize_for_keywords(answer)

    requirements: list[list[str]] = []
    for entry in raw:
        alternatives = entry if isinstance(entry, (list, tuple)) else [entry]
        requirements.append([_normalize_for_keywords(str(a)) for a in alternatives if str(a).strip()])
    requirements = [r for r in requirements if r]

    missing = [r for r in requirements if not any(a in haystack for a in r)]
    is_correct = bool(requirements) and not missing
    return GradingResult(
        is_correct=is_correct, strategy=STRATEGY_EXPECTED_KEYWORDS,
        output=answer,
        feedback="Correct!" if is_correct else "Your answer is missing something important.",
        error=None if is_correct else "Incorrect answer",
        details={"missing_count": len(missing)},
    )


def _grade_blanks(config, request) -> GradingResult:
    expected = [_normalize_blank(str(b.get("answer", ""))) for b in config["blanks"]]
    submitted = request.blanks
    if submitted is None:
        # Fall back to reading a filled-in snippet: look for each expected
        # answer in order through what the student typed.
        remaining = (request.answer if request.answer is not None else (request.code or "")) or ""
        filled = []
        for want in expected:
            idx = remaining.lower().find(want.lower()) if want else -1
            if idx == -1:
                filled.append("")
            else:
                filled.append(want)
                remaining = remaining[idx + len(want):]
        submitted = filled
    normalized = [_normalize_blank(str(s)) for s in submitted]
    if len(normalized) != len(expected):
        return GradingResult(
            is_correct=False, strategy=STRATEGY_BLANKS,
            error="Wrong number of blanks",
            feedback=f"This exercise has {len(expected)} blanks to fill.",
        )
    wrong = [i for i, (got, want) in enumerate(zip(normalized, expected)) if got.lower() != want.lower()]
    is_correct = not wrong
    return GradingResult(
        is_correct=is_correct, strategy=STRATEGY_BLANKS,
        feedback=(
            "All blanks correct!" if is_correct
            else f"{len(wrong)} of {len(expected)} blanks are not right yet."
        ),
        error=None if is_correct else "Incorrect answer",
        details={"wrong_indices": wrong},
    )


def _grade_sandbox(exercise, request) -> GradingResult:
    """Unchanged behaviour: run the student's Python in the existing sandbox."""
    code = request.code or ""
    validation = validate_python_code(code)
    if not validation.is_valid:
        return GradingResult(
            is_correct=False, strategy=STRATEGY_SANDBOX,
            error="Validation error",
            feedback="Code validation failed: " + "; ".join(validation.errors),
        )
    exec_result = execute_code(code, exercise.test_code)
    return GradingResult(
        is_correct=exec_result.success, strategy=STRATEGY_SANDBOX,
        output=exec_result.output,
        error=None if exec_result.success else (exec_result.error or "Incorrect solution"),
        feedback=exec_result.output if exec_result.success else (exec_result.error or "Incorrect solution"),
    )


def grade_exercise(exercise, options: Sequence[Any], request) -> GradingResult:
    """Grade one submission. Never returns correct for an ungradable exercise."""
    strategy = resolve_strategy(exercise, options)
    config = parse_validation_config(getattr(exercise, "validation_config", None))

    if strategy == STRATEGY_SANDBOX:
        return _grade_sandbox(exercise, request)
    if strategy == STRATEGY_OPTION:
        return _grade_option(options, request)
    if strategy == STRATEGY_ORDERING:
        return _grade_ordering(options, request)
    if strategy == STRATEGY_EXPECTED_OUTPUT:
        return _grade_expected_output(config, request)
    if strategy == STRATEGY_EXPECTED_KEYWORDS:
        return _grade_expected_keywords(config, request)
    if strategy == STRATEGY_BLANKS:
        return _grade_blanks(config, request)

    return GradingResult(
        is_correct=False, strategy=UNGRADABLE,
        error="Exercise cannot be graded",
        feedback="This exercise is missing its grading configuration.",
    )
