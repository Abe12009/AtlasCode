import pytest
from httpx import AsyncClient

AND_GRAPH = {
    "nodes": [
        {"id": "a", "type": "input", "config": {"name": "a"}},
        {"id": "b", "type": "input", "config": {"name": "b"}},
        {"id": "g1", "type": "and", "config": {}},
        {"id": "o1", "type": "output", "config": {"name": "out"}},
    ],
    "edges": [
        {"id": "e1", "source": "a", "target": "g1", "targetHandle": "in0"},
        {"id": "e2", "source": "b", "target": "g1", "targetHandle": "in1"},
        {"id": "e3", "source": "g1", "target": "o1"},
    ],
}


class TestCircuitCompile:
    async def test_compile_valid_graph(self, client: AsyncClient, test_user):
        response = await client.post("/circuits/compile", headers=test_user["headers"], json=AND_GRAPH)
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is True
        assert "def circuit(**inputs):" in result["python_code"]

    async def test_compile_missing_inputs(self, client: AsyncClient, test_user):
        response = await client.post("/circuits/compile", headers=test_user["headers"], json={
            "nodes": [{"id": "o1", "type": "output", "config": {"name": "out"}}],
            "edges": [],
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is False
        assert any("input pins" in e for e in result["errors"])

    async def test_compile_cycle_detected(self, client: AsyncClient, test_user):
        response = await client.post("/circuits/compile", headers=test_user["headers"], json={
            "nodes": AND_GRAPH["nodes"],
            "edges": AND_GRAPH["edges"] + [{"id": "e4", "source": "o1", "target": "a"}],
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is False
        assert any("cycle" in e for e in result["errors"])

    async def test_unauthenticated_compile(self, client: AsyncClient):
        response = await client.post("/circuits/compile", json=AND_GRAPH)
        assert response.status_code == 401


class TestCircuitEvaluate:
    async def test_evaluate_and_gate_truth_table(self, client: AsyncClient, test_user):
        expected = {
            (False, False): False,
            (False, True): False,
            (True, False): False,
            (True, True): True,
        }
        for (a, b), expected_out in expected.items():
            response = await client.post("/circuits/evaluate", headers=test_user["headers"], json={
                **AND_GRAPH,
                "input_values": {"a": a, "b": b},
            })
            assert response.status_code == 200
            result = response.json()
            assert result["errors"] == []
            assert result["outputs"]["out"] == expected_out

    async def test_evaluate_reports_cycle_error(self, client: AsyncClient, test_user):
        response = await client.post("/circuits/evaluate", headers=test_user["headers"], json={
            "nodes": AND_GRAPH["nodes"],
            "edges": AND_GRAPH["edges"] + [{"id": "e4", "source": "o1", "target": "a"}],
            "input_values": {"a": True, "b": True},
        })
        assert response.status_code == 200
        result = response.json()
        assert any("cycle" in e for e in result["errors"])


class TestCircuitGradingIntegration:
    """The actual grading path: compile a circuit, then submit the resulting
    Python through the *existing* generic exercise run/submit endpoints --
    Circuit Lab adds no grading code of its own (see circuit_evaluator.py)."""

    async def test_compiled_circuit_graded_by_existing_sandbox(self, client: AsyncClient, test_user):
        compile_response = await client.post("/circuits/compile", headers=test_user["headers"], json=AND_GRAPH)
        python_code = compile_response.json()["python_code"]

        from app.services.code_executor import execute_code

        test_code = (
            'exec(compile(code, "<student>", "exec"), globals())\n'
            "assert circuit(a=True, b=True) == {'out': True}\n"
            "assert circuit(a=True, b=False) == {'out': False}\n"
        )
        result = execute_code(python_code, test_code)
        assert result.success is True

        # A wrong circuit (OR instead of AND) must fail the same test.
        or_graph = {**AND_GRAPH, "nodes": [
            n if n["id"] != "g1" else {**n, "type": "or"} for n in AND_GRAPH["nodes"]
        ]}
        wrong_compile = await client.post("/circuits/compile", headers=test_user["headers"], json=or_graph)
        wrong_result = execute_code(wrong_compile.json()["python_code"], test_code)
        assert wrong_result.success is False
