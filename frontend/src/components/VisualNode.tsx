import { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';

interface VisualNodeProps {
  node: {
    id: string;
    type: string;
    position: { x: number; y: number };
    config: Record<string, string>;
  };
  isSelected: boolean;
  onSelect: (id: string | null) => void;
  onDrag: (id: string, deltaX: number, deltaY: number) => void;
  onDelete: (id: string) => void;
  onConfigChange: (id: string, config: Record<string, string>) => void;
  onConnect: (sourceId: string, targetId: string, sourceHandle?: string, targetHandle?: string) => void;
  t: (key: string, options?: Record<string, unknown>) => string;
}

export function VisualNode({ 
  node, 
  isSelected, 
  onSelect, 
  onDrag, 
  onDelete, 
  onConfigChange, 
  onConnect 
}: VisualNodeProps) {
  const { t } = useTranslation();
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget || (e.target as HTMLElement).classList.contains('node-header')) {
      e.preventDefault();
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
      e.stopPropagation();
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || !dragStart) return;
    const deltaX = e.clientX - dragStart.x;
    const deltaY = e.clientY - dragStart.y;
    onDrag(node.id, deltaX, deltaY);
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setDragStart(null);
  };

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove as EventListener);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove as EventListener);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div
      className={`absolute transition-all duration-150 ${isSelected ? 'ring-2 ring-primary-500' : ''} w-48`}
      style={{
        left: node.position.x,
        top: node.position.y,
        zIndex: isSelected ? 10 : 1,
      }}
      onMouseDown={handleMouseDown}
      onClick={(e) => { e.stopPropagation(); onSelect(node.id); }}
    >
      <div className="node-header bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-t cursor-move flex items-center justify-between" style={{ borderRadius: '0.5rem 0.5rem 0 0' }}>
        <span className="flex items-center space-x-1 text-xs font-medium text-gray-700 dark:text-gray-300">
          <span className="text-lg">{'🔧'}</span>
          <span>{'Node'}</span>
        </span>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(node.id); }}
          className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500 transition-colors"
          aria-label="Delete node"
        >
          <span className="h-3 w-3">🗑️</span>
        </button>
      </div>
      <div className="bg-white dark:bg-gray-800 px-2 py-2 rounded-b border-t border-gray-200 dark:border-gray-700" style={{ borderRadius: '0 0 0.5rem 0.5rem' }}>
        <div className="mt-2 flex space-x-1">
          <div
            className="w-3 h-3 rounded-full bg-gray-400 cursor-pointer"
            style={{ cursor: 'crosshair' }}
            title="Connect from here"
          />
          <div
            className="w-3 h-3 rounded-full bg-gray-400 cursor-pointer ml-auto"
            style={{ cursor: 'crosshair' }}
            title="Connect to here"
          />
        </div>
      </div>
    </div>
  );
}