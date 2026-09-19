import type { CircuitEdge, CircuitNode, CircuitNodeType } from '../../types';

export const NODE_WIDTH = 140;
export const NODE_HEIGHT = 64;

export const GATE_TYPES: CircuitNodeType[] = ['and', 'or', 'not', 'nand', 'nor', 'xor', 'xnor'];

/** Number of input ports a node type has (0 for `input` pins, which have
 * none -- they are the graph's sources). */
export function inputPortCount(type: CircuitNodeType): number {
  if (type === 'input') return 0;
  if (type === 'not' || type === 'output') return 1;
  return 2;
}

export function hasOutputPort(type: CircuitNodeType): boolean {
  return type !== 'output';
}

/** Pixel position (canvas-relative) of a node's Nth input port, or its
 * single output port. Matches the port dots CircuitNodeView renders. */
export function inputPortPosition(node: CircuitNode, index: number): { x: number; y: number } {
  const count = inputPortCount(node.type);
  const spacing = NODE_HEIGHT / (count + 1);
  return {
    x: node.position.x,
    y: node.position.y + spacing * (index + 1),
  };
}

export function outputPortPosition(node: CircuitNode): { x: number; y: number } {
  return {
    x: node.position.x + NODE_WIDTH,
    y: node.position.y + NODE_HEIGHT / 2,
  };
}

/** Which input port index an edge targets -- parses `targetHandle` ("in0",
 * "in1") when present, else 0 (correct for single-input nodes and the common
 * case of one edge per target). */
export function targetPortIndex(edge: CircuitEdge): number {
  if (edge.targetHandle && /^in\d+$/.test(edge.targetHandle)) {
    return Number(edge.targetHandle.slice(2));
  }
  return 0;
}

export function edgePath(from: { x: number; y: number }, to: { x: number; y: number }): string {
  const dx = Math.max(40, Math.abs(to.x - from.x) / 2);
  return `M ${from.x} ${from.y} C ${from.x + dx} ${from.y} ${to.x - dx} ${to.y} ${to.x} ${to.y}`;
}
