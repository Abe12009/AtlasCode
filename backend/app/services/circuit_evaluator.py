"""Circuit Lab's simulation engine: propagates boolean values through a gate
graph, and compiles the same graph to a Python function so grading can reuse
the existing code sandbox unchanged (see app.services.visual_compiler for the
identical idea applied to flowcharts -- this mirrors it for gates).

Two entry points, both built on the same topological walk:

* ``evaluate_circuit`` -- for the interactive canvas and the "real-world
  bridge" widget. Given input values, returns the boolean at every node so
  the frontend can light up wires/gates live.
* ``compile_circuit`` -- for grading. Produces ``def circuit(**inputs): ...``
  Python source. Authoring a circuit_lab exercise's ``test_code`` uses the
  existing ``app.seed.authoring.asserts()`` helper (`exec`s the submitted
  source into the grader's globals, then calls it by name) -- the same
  mechanism already used for exercises that grade a *returned* value rather
  than printed output. No bespoke grading strategy needed.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

GATE_TYPES = ("and", "or", "not", "nand", "nor", "xor", "xnor")
#: Number of inputs each gate type consumes. Everything else (input/output
#: pins) is handled separately -- they are not gates.
GATE_ARITY: Dict[str, int] = {
    "and": 2, "or": 2, "nand": 2, "nor": 2, "xor": 2, "xnor": 2,
    "not": 1,
}

GATE_FUNCS = {
    "and": lambda a, b: a and b,
    "or": lambda a, b: a or b,
    "nand": lambda a, b: not (a and b),
    "nor": lambda a, b: not (a or b),
    "xor": lambda a, b: a != b,
    "xnor": lambda a, b: a == b,
    "not": lambda a: not a,
}

GATE_PYTHON_EXPR = {
    "and": "({a} and {b})",
    "or": "({a} or {b})",
    "nand": "(not ({a} and {b}))",
    "nor": "(not ({a} or {b}))",
    "xor": "({a} != {b})",
    "xnor": "({a} == {b})",
    "not": "(not {a})",
}

#: Circuits stay small and purely combinational for v1 (see the Feature 2
#: proposal) -- this is a generous ceiling against a malformed/huge graph,
#: not a design target.
MAX_NODES = 200

#: Sanity cap on input pins -- keeps v1 circuits (and any test author
#: enumerating combinations by hand) small and teachable, not a technical
#: limit of the evaluator or compiler.
MAX_INPUT_PINS = 8


@dataclass
class GraphError:
    message: str


@dataclass
class EvaluateResult:
    #: node id -> propagated boolean value, for every node in the graph.
    values: Dict[str, bool] = field(default_factory=dict)
    #: output pin name -> boolean value (the subset a student/scenario cares about).
    outputs: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


@dataclass
class CompileResult:
    python_code: str
    is_valid: bool
    errors: List[str]


def _ordered_inputs(node_id: str, edges: Sequence[dict]) -> List[str]:
    """Source node ids feeding `node_id`, in port order.

    Ports are disambiguated by `targetHandle` ("in0", "in1", ...) when
    present; edges without one keep arrival order, which is enough for a
    single-input gate (NOT) or when the author only ever wires one edge at a
    time in the UI.
    """
    incoming = [e for e in edges if e["target"] == node_id]
    #: Snapshot of arrival order, read by the key function below -- must be a
    #: list distinct from `incoming` itself: CPython detaches a list's
    #: backing storage while it sorts (to detect concurrent mutation), so a
    #: key function that reads the list it's sorting sees it as empty.
    arrival_order = list(incoming)

    def sort_key(edge: dict):
        handle = edge.get("targetHandle")
        if handle and handle.startswith("in") and handle[2:].isdigit():
            return int(handle[2:])
        return arrival_order.index(edge)

    incoming.sort(key=sort_key)
    return [e["source"] for e in incoming]


def _topo_order(nodes: Sequence[dict], edges: Sequence[dict]) -> tuple[List[dict], List[str]]:
    """Kahn's algorithm. Returns (ordered_nodes, errors) -- errors is
    non-empty (and ordering incomplete/unusable) when the graph has a cycle,
    which a purely combinational circuit can never legitimately have."""
    node_map = {n["id"]: n for n in nodes}
    in_degree = {n["id"]: 0 for n in nodes}
    out_edges: Dict[str, List[str]] = {n["id"]: [] for n in nodes}

    for edge in edges:
        if edge["source"] not in node_map or edge["target"] not in node_map:
            continue
        out_edges[edge["source"]].append(edge["target"])
        in_degree[edge["target"]] += 1

    queue = [nid for nid, deg in in_degree.items() if deg == 0]
    ordered: List[dict] = []
    while queue:
        nid = queue.pop(0)
        ordered.append(node_map[nid])
        for target in out_edges[nid]:
            in_degree[target] -= 1
            if in_degree[target] == 0:
                queue.append(target)

    if len(ordered) != len(nodes):
        return [], ["Circuit contains a cycle -- combinational circuits cannot loop back on themselves"]
    return ordered, []


def _validate_graph(nodes: Sequence[dict]) -> List[str]:
    errors = []
    if len(nodes) > MAX_NODES:
        errors.append(f"Circuit has too many components (max {MAX_NODES})")
    for node in nodes:
        ntype = node.get("type")
        if ntype not in GATE_TYPES and ntype not in ("input", "output"):
            errors.append(f"Unknown component type '{ntype}'")
    return errors


def evaluate_circuit(nodes: Sequence[dict], edges: Sequence[dict], input_values: Dict[str, bool]) -> EvaluateResult:
    errors = _validate_graph(nodes)
    if errors:
        return EvaluateResult(errors=errors)

    ordered, topo_errors = _topo_order(nodes, edges)
    if topo_errors:
        return EvaluateResult(errors=topo_errors)

    values: Dict[str, bool] = {}
    outputs: Dict[str, bool] = {}

    for node in ordered:
        ntype = node["type"]
        config = node.get("config") or {}
        node_id = node["id"]

        if ntype == "input":
            values[node_id] = bool(input_values.get(config.get("name", ""), False))
            continue

        if ntype == "output":
            sources = _ordered_inputs(node_id, edges)
            values[node_id] = values.get(sources[0], False) if sources else False
            name = config.get("name", node_id)
            outputs[name] = values[node_id]
            continue

        # Gate.
        sources = _ordered_inputs(node_id, edges)
        arity = GATE_ARITY[ntype]
        if len(sources) != arity:
            errors.append(f"'{ntype}' gate ({node_id}) expects {arity} input(s), has {len(sources)}")
            values[node_id] = False
            continue
        args = [values.get(sid, False) for sid in sources]
        values[node_id] = GATE_FUNCS[ntype](*args)

    return EvaluateResult(values=values, outputs=outputs, errors=errors)


def compile_circuit(nodes: Sequence[dict], edges: Sequence[dict]) -> CompileResult:
    errors = _validate_graph(nodes)
    if errors:
        return CompileResult(python_code="", is_valid=False, errors=errors)

    ordered, topo_errors = _topo_order(nodes, edges)
    if topo_errors:
        return CompileResult(python_code="", is_valid=False, errors=topo_errors)

    input_names = [n["config"]["name"] for n in ordered if n["type"] == "input" and (n.get("config") or {}).get("name")]
    if not input_names:
        errors.append("Circuit has no input pins")
    if len(input_names) > MAX_INPUT_PINS:
        errors.append(f"Circuit has too many input pins (max {MAX_INPUT_PINS})")
    output_nodes = [n for n in ordered if n["type"] == "output"]
    if not output_nodes:
        errors.append("Circuit has no output pins")
    if errors:
        return CompileResult(python_code="", is_valid=False, errors=errors)

    var_name = {n["id"]: f"v_{i}" for i, n in enumerate(ordered)}
    lines = ["def circuit(**inputs):"]

    for node in ordered:
        ntype = node["type"]
        config = node.get("config") or {}
        node_id = node["id"]
        var = var_name[node_id]

        if ntype == "input":
            name = config.get("name", "")
            lines.append(f"    {var} = bool(inputs.get({name!r}, False))")
            continue

        if ntype == "output":
            sources = _ordered_inputs(node_id, edges)
            if not sources:
                errors.append(f"Output pin '{config.get('name', node_id)}' is not connected")
                lines.append(f"    {var} = False")
            else:
                lines.append(f"    {var} = {var_name[sources[0]]}")
            continue

        sources = _ordered_inputs(node_id, edges)
        arity = GATE_ARITY[ntype]
        if len(sources) != arity:
            errors.append(f"'{ntype}' gate ({node_id}) expects {arity} input(s), has {len(sources)}")
            lines.append(f"    {var} = False")
            continue
        expr = GATE_PYTHON_EXPR[ntype]
        if arity == 1:
            lines.append(f"    {var} = {expr.format(a=var_name[sources[0]])}")
        else:
            lines.append(f"    {var} = {expr.format(a=var_name[sources[0]], b=var_name[sources[1]])}")

    if errors:
        return CompileResult(python_code="", is_valid=False, errors=errors)

    return_pairs = [
        (f"{(n.get('config') or {}).get('name', n['id'])!r}", var_name[n["id"]])
        for n in output_nodes
    ]
    return_items = ", ".join(f"{key}: {var}" for key, var in return_pairs)
    lines.append(f"    return {{{return_items}}}")

    return CompileResult(python_code="\n".join(lines), is_valid=True, errors=[])
