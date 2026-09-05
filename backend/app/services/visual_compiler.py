from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class CompileResult:
    python_code: str
    is_valid: bool
    errors: List[str]


NODE_TEMPLATES = {
    "start": "",
    "end": "",
    "variable": "{name} = {value}",
    "output": "print({value})",
    "assign": "{target} = {value}",
    "if": "if {condition}:",
    "else": "else:",
    "loop": "for {var} in range({times}):",
    "while_loop": "while {condition}:",
    "function": "def {name}({params}):",
    "return": "return {value}",
    "operation": "{target} = {left} {op} {right}",
}


def compile_visual_program(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> CompileResult:
    errors: List[str] = []
    node_map = {node["id"]: node for node in nodes}
    adjacency: Dict[str, List[str]] = {}
    reverse_adjacency: Dict[str, List[str]] = {}

    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        if source not in adjacency:
            adjacency[source] = []
        adjacency[source].append(target)
        if target not in reverse_adjacency:
            reverse_adjacency[target] = []
        reverse_adjacency[target].append(source)

    start_nodes = [n for n in nodes if n["type"] == "start"]
    if not start_nodes:
        errors.append("No start node found")
        return CompileResult(python_code="", is_valid=False, errors=errors)

    if len(start_nodes) > 1:
        errors.append("Multiple start nodes found")
        return CompileResult(python_code="", is_valid=False, errors=errors)

    visited = set()
    code_lines = []
    indent_level = 0

    def generate_code(node_id: str, current_indent: int) -> int:
        if node_id in visited:
            return current_indent
        visited.add(node_id)

        node = node_map.get(node_id)
        if not node:
            errors.append(f"Node {node_id} not found")
            return current_indent

        node_type = node["type"]
        config = node.get("config", {})

        if node_type == "start":
            pass
        elif node_type == "end":
            pass
        elif node_type == "variable":
            name = config.get("name", "var")
            value = config.get("value", "0")
            code_lines.append(" " * current_indent * 4 + f"{name} = {value}")
        elif node_type == "output":
            value = config.get("value", "")
            code_lines.append(" " * current_indent * 4 + f"print({value})")
        elif node_type == "assign":
            target = config.get("target", "var")
            value = config.get("value", "0")
            code_lines.append(" " * current_indent * 4 + f"{target} = {value}")
        elif node_type == "if":
            condition = config.get("condition", "True")
            code_lines.append(" " * current_indent * 4 + f"if {condition}:")
            current_indent += 1
        elif node_type == "else":
            current_indent -= 1
            code_lines.append(" " * current_indent * 4 + "else:")
            current_indent += 1
        elif node_type == "loop":
            var = config.get("var", "i")
            times = config.get("times", "10")
            code_lines.append(" " * current_indent * 4 + f"for {var} in range({times}):")
            current_indent += 1
        elif node_type == "while_loop":
            condition = config.get("condition", "True")
            code_lines.append(" " * current_indent * 4 + f"while {condition}:")
            current_indent += 1
        elif node_type == "function":
            name = config.get("name", "my_function")
            params = config.get("params", "")
            code_lines.append(" " * current_indent * 4 + f"def {name}({params}):")
            current_indent += 1
        elif node_type == "return":
            value = config.get("value", "")
            code_lines.append(" " * current_indent * 4 + f"return {value}")
        elif node_type == "operation":
            target = config.get("target", "result")
            left = config.get("left", "0")
            op = config.get("op", "+")
            right = config.get("right", "0")
            code_lines.append(" " * current_indent * 4 + f"{target} = {left} {op} {right}")
        else:
            errors.append(f"Unknown node type: {node_type}")

        next_nodes = adjacency.get(node_id, [])
        for next_node in next_nodes:
            if next_node not in visited:
                current_indent = generate_code(next_node, current_indent)

        if node_type in ("if", "else", "loop", "while_loop", "function"):
            current_indent -= 1

        return current_indent

    generate_code(start_nodes[0]["id"], 0)

    unvisited = [n for n in nodes if n["id"] not in visited and n["type"] != "end"]
    if unvisited:
        errors.append(f"Unreachable nodes: {[n['id'] for n in unvisited]}")

    python_code = "\n".join(code_lines)

    return CompileResult(python_code=python_code, is_valid=len(errors) == 0, errors=errors)


def validate_visual_program(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> CompileResult:
    return compile_visual_program(nodes, edges)