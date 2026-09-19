import { useEffect, useState } from 'react';
import { Trash2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import type { CircuitNode } from '../../types';
import { NODE_HEIGHT, NODE_WIDTH, inputPortCount, inputPortPosition, hasOutputPort } from './circuitLayout';

const GATE_SYMBOLS: Record<string, string> = {
  and: 'AND', or: 'OR', not: 'NOT', nand: 'NAND', nor: 'NOR', xor: 'XOR', xnor: 'XNOR',
};

interface CircuitNodeViewProps {
  node: CircuitNode;
  isSelected: boolean;
  value: boolean | undefined;
  isConnectingSource: boolean;
  onSelect: (id: string | null) => void;
  onMove: (id: string, position: { x: number; y: number }) => void;
  onDelete: (id: string) => void;
  onRename: (id: string, name: string) => void;
  onOutputPortClick: (id: string) => void;
  onInputPortClick: (id: string, portIndex: number) => void;
  onToggleInputValue: (id: string) => void;
  inputToggleValue?: boolean;
}

export function CircuitNodeView({
  node,
  isSelected,
  value,
  isConnectingSource,
  onSelect,
  onMove,
  onDelete,
  onRename,
  onOutputPortClick,
  onInputPortClick,
  onToggleInputValue,
  inputToggleValue,
}: CircuitNodeViewProps) {
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);

  const handlePointerDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('[data-no-drag]')) return;
    e.stopPropagation();
    onSelect(node.id);
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  useEffect(() => {
    if (!dragStart) return;
    const handleMove = (e: MouseEvent) => {
      const deltaX = e.clientX - dragStart.x;
      const deltaY = e.clientY - dragStart.y;
      onMove(node.id, { x: node.position.x + deltaX, y: node.position.y + deltaY });
      setDragStart({ x: e.clientX, y: e.clientY });
    };
    const handleUp = () => setDragStart(null);
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dragStart]);

  const inputCount = inputPortCount(node.type);
  const isPin = node.type === 'input' || node.type === 'output';
  const lit = node.type === 'input' ? inputToggleValue : value;

  return (
    <div
      className={cn(
        'absolute rounded-xl border-2 bg-bg-elevated shadow-card select-none cursor-move transition-colors',
        isSelected ? 'border-primary-500' : 'border-border-primary',
      )}
      style={{ left: node.position.x, top: node.position.y, width: NODE_WIDTH, height: NODE_HEIGHT }}
      onMouseDown={handlePointerDown}
    >
      <div className="flex items-center justify-between px-2 py-1 h-full">
        <div className="flex-1 min-w-0">
          {isPin ? (
            <input
              data-no-drag
              type="text"
              value={node.config.name || ''}
              onChange={(e) => onRename(node.id, e.target.value)}
              className="w-full bg-transparent text-sm font-mono font-semibold text-text-primary border-b border-dashed border-border-secondary focus:outline-none focus:border-primary-500"
              placeholder="name"
            />
          ) : (
            <span className="text-sm font-bold text-text-primary">{GATE_SYMBOLS[node.type] || node.type}</span>
          )}
          {node.type === 'input' && (
            <button
              type="button"
              data-no-drag
              onClick={() => onToggleInputValue(node.id)}
              className={cn(
                'mt-1 block w-10 h-5 rounded-full transition-colors relative',
                inputToggleValue ? 'bg-success-500' : 'bg-bg-tertiary border border-border-primary',
              )}
              aria-pressed={!!inputToggleValue}
              aria-label={`Toggle ${node.config.name || 'input'}`}
            >
              <span
                className={cn(
                  'absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform',
                  inputToggleValue ? 'translate-x-5' : 'translate-x-0.5',
                )}
              />
            </button>
          )}
          {node.type === 'output' && (
            <span className={cn('mt-1 block text-xs font-mono font-semibold', lit ? 'text-success-500' : 'text-text-quaternary')}>
              {lit ? 'TRUE' : 'FALSE'}
            </span>
          )}
        </div>
        <button
          type="button"
          data-no-drag
          onClick={() => onDelete(node.id)}
          className="p-1 rounded hover:bg-error-500/10 text-text-quaternary hover:text-error-500 transition-colors flex-shrink-0"
          aria-label="Delete component"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>

      {Array.from({ length: inputCount }).map((_, i) => {
        const pos = inputPortPosition(node, i);
        return (
          <button
            key={i}
            type="button"
            data-no-drag
            onClick={() => onInputPortClick(node.id, i)}
            className={cn(
              'absolute w-3.5 h-3.5 rounded-full border-2 -translate-x-1/2 -translate-y-1/2 transition-colors',
              isConnectingSource ? 'bg-primary-400 border-primary-600 animate-pulse' : 'bg-bg-tertiary border-text-quaternary hover:border-primary-500',
            )}
            style={{ left: pos.x - node.position.x, top: pos.y - node.position.y }}
            aria-label="Input port"
          />
        );
      })}
      {hasOutputPort(node.type) && (
        <button
          type="button"
          data-no-drag
          onClick={() => onOutputPortClick(node.id)}
          className={cn(
            'absolute w-3.5 h-3.5 rounded-full border-2 -translate-x-1/2 -translate-y-1/2 transition-colors',
            isConnectingSource
              ? 'bg-primary-500 border-primary-600'
              : lit
                ? 'bg-success-500 border-success-600'
                : 'bg-bg-tertiary border-text-quaternary hover:border-primary-500',
          )}
          style={{ left: NODE_WIDTH, top: NODE_HEIGHT / 2 }}
          aria-label="Output port"
        />
      )}
    </div>
  );
}
