"""Break-the-Code's trace recorder: runs a piece of *trusted, author-supplied*
buggy code once, at content-authoring/seed time, and records its real
line-by-line execution as a step-through trace the frontend can play back.

This is deliberately NOT part of the student-facing sandbox
(app.services.code_executor). It uses `sys.settrace`, which needs frame
access the sandbox explicitly forbids submitted code from touching (see
FORBIDDEN_BUILTINS/dangerous_modules there) -- and it never needs to be
sandboxed, because it only ever runs code an author wrote into a seed file,
the same trust boundary CircuitLab's `compile_circuit` output already sits
behind. The trace it produces is a static
artifact stored in the exercise's `validation_config`; nothing at request
time re-runs the author's code.
"""

import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

#: Safety cap against an author's buggy code that doesn't terminate (an
#: infinite loop is exactly the kind of bug this feature exists to surface,
#: so it must fail the seed build loudly instead of hanging it).
MAX_STEPS = 500

#: Local variables this deep or long are summarized rather than fully
#: serialized, so one giant/recursive structure can't blow up the trace.
_MAX_CONTAINER_ITEMS = 50
_MAX_REPR_LEN = 200

_TRACE_FILENAME = "<break_the_code>"


@dataclass
class TraceStep:
    line: int
    #: variable name -> JSON-serializable value (or a repr() string fallback).
    locals: Dict[str, Any]


@dataclass
class TraceResult:
    steps: List[TraceStep] = field(default_factory=list)
    #: Set when the traced code raised or exceeded MAX_STEPS. A non-None
    #: error means the trace is unusable -- callers must not store it.
    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.error is None and bool(self.steps)


def _to_serializable(value: Any) -> Any:
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_to_serializable(v) for v in list(value)[:_MAX_CONTAINER_ITEMS]]
    if isinstance(value, dict):
        return {str(k): _to_serializable(v) for k, v in list(value.items())[:_MAX_CONTAINER_ITEMS]}
    return repr(value)[:_MAX_REPR_LEN]


def record_trace(code: str, entry_call: str) -> TraceResult:
    """Execute `code` (function/class definitions, etc.) followed by
    `entry_call` (an expression that invokes it, e.g. "binary_search([1,3,5],
    5)"), tracing every line the interpreter actually executes within that
    source -- not into stdlib or any other module -- and snapshotting local
    variables at each one.
    """
    steps: List[TraceStep] = []
    limit_hit = False

    def tracer(frame, event, arg):
        nonlocal limit_hit
        if frame.f_code.co_filename != _TRACE_FILENAME:
            return None
        if event == "line":
            if len(steps) >= MAX_STEPS:
                limit_hit = True
                sys.settrace(None)
                raise RuntimeError("trace step limit exceeded")
            snapshot = {k: _to_serializable(v) for k, v in frame.f_locals.items() if not k.startswith("__")}
            steps.append(TraceStep(line=frame.f_lineno, locals=snapshot))
        return tracer

    full_source = f"{code}\n{entry_call}\n"
    try:
        compiled = compile(full_source, _TRACE_FILENAME, "exec")
    except SyntaxError as e:
        return TraceResult(error=f"SyntaxError: {e}")

    namespace: Dict[str, Any] = {}
    old_trace = sys.gettrace()
    sys.settrace(tracer)
    try:
        exec(compiled, namespace)
    except Exception as e:
        if limit_hit:
            return TraceResult(error=f"Code did not terminate within {MAX_STEPS} steps")
        return TraceResult(steps=steps, error=f"{type(e).__name__}: {e}")
    finally:
        sys.settrace(old_trace)

    return TraceResult(steps=steps)


def trace_to_json(result: TraceResult) -> List[Dict[str, Any]]:
    """The plain-dict shape stored in `Exercise.validation_config["trace"]`
    and served to the frontend as-is."""
    return [{"line": step.line, "locals": step.locals} for step in result.steps]
