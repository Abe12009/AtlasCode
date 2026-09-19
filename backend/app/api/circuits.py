"""Circuit Lab -- digital logic gate simulator.

Two endpoints only. Grading itself needs no dedicated route: the frontend
compiles the student's graph to Python via `/compile` and submits that
through the *existing* generic `POST /exercises/{id}/run` and `/submit`
(same as every other exercise type -- see ExercisePanel.tsx), which grades it
with the ordinary sandbox against the exercise's `test_code` (see
app.services.exercise_grading's STRATEGY_SANDBOX note on circuit_lab). A
`starter` endpoint isn't needed either: `Exercise.starter_code` already comes
back on the exercise object the lesson page loads.

`/evaluate` is the one Circuit-Lab-specific piece: it propagates actual
boolean values through the graph (rather than producing code) so the canvas
and the "real-world bridge" widget can animate live as the student toggles
inputs.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas import (
    CircuitCompileRequest,
    CircuitCompileResponse,
    CircuitEvaluateRequest,
    CircuitEvaluateResponse,
)
from app.services.circuit_evaluator import compile_circuit, evaluate_circuit

router = APIRouter(prefix="/circuits", tags=["circuit-lab"])


@router.post("/compile", response_model=CircuitCompileResponse)
async def compile_circuit_endpoint(
    request: CircuitCompileRequest,
    current_user=Depends(get_current_user),
):
    result = compile_circuit(request.nodes, request.edges)
    return result


@router.post("/evaluate", response_model=CircuitEvaluateResponse)
async def evaluate_circuit_endpoint(
    request: CircuitEvaluateRequest,
    current_user=Depends(get_current_user),
):
    result = evaluate_circuit(request.nodes, request.edges, request.input_values)
    return CircuitEvaluateResponse(values=result.values, outputs=result.outputs, errors=result.errors)
