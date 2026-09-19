import { useRef, useState } from 'react';
import { cn } from '../../lib/utils';
import { useTranslation } from '../../hooks/useTranslation';
import type { CircuitEdge, CircuitGraph, CircuitNode, CircuitNodeType } from '../../types';
import { CircuitNodeView } from './CircuitNodeView';
import {
  GATE_TYPES,
  NODE_HEIGHT,
  NODE_WIDTH,
  edgePath,
  inputPortCount,
  inputPortPosition,
  outputPortPosition,
  targetPortIndex,
} from './circuitLayout';

interface CircuitCanvasProps {
  graph: CircuitGraph;
  onChange: (graph: CircuitGraph) => void;
  values: Record<string, boolean>;
  inputToggles: Record<string, boolean>;
  onToggleInput: (nodeId: string) => void;
  errors: string[];
}

let nodeCounter = 0;
function newId(prefix: string) {
  nodeCounter += 1;
  return `${prefix}-${Date.now()}-${nodeCounter}`;
}

export function CircuitCanvas({ graph, onChange, values, inputToggles, onToggleInput, errors }: CircuitCanvasProps) {
  const { t } = useTranslation();
  const canvasRef = useRef<HTMLDivElement>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);

  const addNode = (type: CircuitNodeType, position: { x: number; y: number }) => {
    const node: CircuitNode = {
      id: newId(type),
      type,
      position,
      config: type === 'input' || type === 'output' ? { name: type === 'input' ? 'x' : 'y' } : {},
    };
    onChange({ ...graph, nodes: [...graph.nodes, node] });
  };

  const moveNode = (id: string, position: { x: number; y: number }) => {
    onChange({ ...graph, nodes: graph.nodes.map((n) => (n.id === id ? { ...n, position } : n)) });
  };

  const renameNode = (id: string, name: string) => {
    onChange({ ...graph, nodes: graph.nodes.map((n) => (n.id === id ? { ...n, config: { ...n.config, name } } : n)) });
  };

  const deleteNode = (id: string) => {
    onChange({
      nodes: graph.nodes.filter((n) => n.id !== id),
      edges: graph.edges.filter((e) => e.source !== id && e.target !== id),
    });
    if (selectedId === id) setSelectedId(null);
  };

  const deleteEdge = (id: string) => {
    onChange({ ...graph, edges: graph.edges.filter((e) => e.id !== id) });
  };

  const handleOutputPortClick = (nodeId: string) => {
    setConnectingFrom((prev) => (prev === nodeId ? null : nodeId));
  };

  const handleInputPortClick = (nodeId: string, portIndex: number) => {
    if (!connectingFrom || connectingFrom === nodeId) {
      setConnectingFrom(null);
      return;
    }
    const targetHandle = `in${portIndex}`;
    const withoutExisting = graph.edges.filter((e) => !(e.target === nodeId && e.targetHandle === targetHandle));
    const edge: CircuitEdge = { id: newId('edge'), source: connectingFrom, target: nodeId, targetHandle };
    onChange({ ...graph, edges: [...withoutExisting, edge] });
    setConnectingFrom(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const type = e.dataTransfer.getData('circuit-node-type') as CircuitNodeType;
    if (!type) return;
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    addNode(type, { x: e.clientX - rect.left - NODE_WIDTH / 2, y: e.clientY - rect.top - NODE_HEIGHT / 2 });
  };

  const nodeById = new Map(graph.nodes.map((n) => [n.id, n]));

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {(['input', 'output', ...GATE_TYPES] as CircuitNodeType[]).map((type) => (
          <div
            key={type}
            draggable
            onDragStart={(e) => e.dataTransfer.setData('circuit-node-type', type)}
            className="px-3 py-1.5 rounded-lg border border-border-primary bg-bg-secondary text-xs font-mono font-semibold text-text-secondary cursor-grab active:cursor-grabbing hover:border-primary-400 hover:text-text-primary transition-colors"
            title={t('circuit_lab.drag_to_add')}
          >
            {type === 'input' ? t('circuit_lab.input_pin') : type === 'output' ? t('circuit_lab.output_pin') : type.toUpperCase()}
          </div>
        ))}
      </div>

      {errors.length > 0 && (
        <div className="rounded-lg border border-error-500/30 bg-error-500/10 p-2 text-xs text-error-600 dark:text-error-400">
          {errors.join(' · ')}
        </div>
      )}

      <div
        ref={canvasRef}
        data-testid="circuit-canvas-background"
        className="relative h-[420px] rounded-xl border border-border-primary bg-bg-code/50 bg-grid-pattern overflow-auto"
        style={{ backgroundSize: '24px 24px' }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={(e) => {
          // Only the empty canvas background clears selection/connecting --
          // a click on a node or port bubbles up here too, and without this
          // guard it would immediately undo handleOutputPortClick's
          // setConnectingFrom, making the output-then-input wiring gesture
          // impossible (the click-to-connect equivalent of VisualProgramming's
          // handleCanvasClick).
          if (e.target === e.currentTarget) {
            setSelectedId(null);
            setConnectingFrom(null);
          }
        }}
      >
        <svg className="absolute inset-0 pointer-events-none" width="100%" height="100%">
          {graph.edges.map((edge) => {
            const source = nodeById.get(edge.source);
            const target = nodeById.get(edge.target);
            if (!source || !target) return null;
            const from = outputPortPosition(source);
            const to = inputPortPosition(target, targetPortIndex(edge));
            const lit = !!values[source.id];
            return (
              <path
                key={edge.id}
                d={edgePath(from, to)}
                fill="none"
                stroke={lit ? '#22c55e' : '#64748b'}
                strokeWidth={2.5}
                className="pointer-events-auto cursor-pointer"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteEdge(edge.id);
                }}
              />
            );
          })}
        </svg>

        {graph.nodes.map((node) => (
          <CircuitNodeView
            key={node.id}
            node={node}
            isSelected={selectedId === node.id}
            value={values[node.id]}
            isConnectingSource={connectingFrom === node.id}
            onSelect={setSelectedId}
            onMove={moveNode}
            onDelete={deleteNode}
            onRename={renameNode}
            onOutputPortClick={handleOutputPortClick}
            onInputPortClick={handleInputPortClick}
            onToggleInputValue={onToggleInput}
            inputToggleValue={node.type === 'input' ? !!inputToggles[node.id] : undefined}
          />
        ))}

        {graph.nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-sm text-text-quaternary pointer-events-none">
            {t('circuit_lab.empty_canvas')}
          </div>
        )}
      </div>

      <p className={cn('text-xs text-text-quaternary')}>{t('circuit_lab.canvas_help')}</p>
    </div>
  );
}
