import { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { visualApi, exercisesApi } from '../api/services';
import { ArrowLeft, Play, CheckCircle, RotateCcw, Trash2, Plus, Minus, Download, ChevronRight, Sparkles, Terminal, Code, Check, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from '../hooks/useTranslation';
import { VisualNode } from '../components/VisualNode';
import type { VisualProgramResponse, Exercise, ExerciseTranslation } from '../types';
import { Card, Button, Badge, Alert, cn, Skeleton, CodeEditor, TerminalPanel, StatusBadge, XPBadge } from '../components/ui';

type NodeType = 'start' | 'end' | 'variable' | 'output' | 'assign' | 'if' | 'else' | 'loop' | 'while_loop' | 'function' | 'return' | 'operation';

interface Node {
  id: string;
  type: string;
  position: { x: number; y: number };
  config: Record<string, string>;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

interface VisualEditorState {
  nodes: Node[];
  edges: Edge[];
  selectedNodeId: string | null;
  history: { nodes: Node[]; edges: Edge[] }[];
  historyIndex: number;
}

interface ExerciseWithRelations extends Exercise {
  course_id?: number;
  course_title?: string;
  lesson_id?: number;
  lesson_title?: string;
}

interface ExerciseTranslationWithTitle extends ExerciseTranslation {
  title?: string;
}

const NODE_PALETTE: { type: string; label: string; icon: string; defaultConfig: Record<string, string>; category: string }[] = [
  { type: 'start', label: 'Start', icon: '▶', defaultConfig: {}, category: 'control' },
  { type: 'end', label: 'End', icon: '■', defaultConfig: {}, category: 'control' },
  { type: 'variable', label: 'Variable', icon: '𝑥', defaultConfig: { name: 'var', value: '0' }, category: 'data' },
  { type: 'output', label: 'Output', icon: '📤', defaultConfig: { value: '' }, category: 'io' },
  { type: 'assign', label: 'Assign', icon: '←', defaultConfig: { target: 'var', value: '0' }, category: 'data' },
  { type: 'if', label: 'If', icon: '?', defaultConfig: { condition: 'True' }, category: 'control' },
  { type: 'else', label: 'Else', icon: ':', defaultConfig: {}, category: 'control' },
  { type: 'loop', label: 'For Loop', icon: '↻', defaultConfig: { var: 'i', times: '10' }, category: 'control' },
  { type: 'while_loop', label: 'While', icon: '∞', defaultConfig: { condition: 'True' }, category: 'control' },
  { type: 'function', label: 'Function', icon: 'ƒ', defaultConfig: { name: 'my_func', params: '' }, category: 'control' },
  { type: 'return', label: 'Return', icon: '↩', defaultConfig: { value: '' }, category: 'control' },
  { type: 'operation', label: 'Operation', icon: '±', defaultConfig: { target: 'result', left: '0', op: '+', right: '0' }, category: 'data' },
];

const CATEGORY_COLORS = {
  control: 'bg-primary-500/10 text-primary-400 border-primary-500/30',
  data: 'bg-accent-500/10 text-accent-400 border-accent-500/30',
  io: 'bg-success-500/10 text-success-400 border-success-500/30',
};

export function VisualProgrammingPage() {
  const { t, isRTL } = useTranslation();
  const { exerciseId } = useParams<{ exerciseId: string }>();
  const queryClient = useQueryClient();

  const [state, setState] = useState<VisualEditorState>({
    nodes: [],
    edges: [],
    selectedNodeId: null,
    history: [],
    historyIndex: -1,
  });
  const [isCompiling, setIsCompiling] = useState(false);
  const [compileResult, setCompileResult] = useState<VisualProgramResponse | null>(null);
  const [showCodePreview, setShowCodePreview] = useState(false);
  const canvasRef = useRef<HTMLDivElement>(null);
  const [terminalOutput, setTerminalOutput] = useState<string>('');
  const [terminalError, setTerminalError] = useState<string>('');

  const { data: exercise } = useQuery({
    queryKey: ['exercise', exerciseId],
    queryFn: () => exercisesApi.getById(Number(exerciseId), 'en'),
    enabled: !!exerciseId,
  });

  const { data: starterData } = useQuery({
    queryKey: ['visualStarter', exerciseId],
    queryFn: () => visualApi.getStarter(Number(exerciseId)),
    enabled: !!exerciseId,
  });

  const compileMutation = useMutation({
    mutationFn: (data: { nodes: Node[]; edges: Edge[] }) => visualApi.compile(data as any),
    onSuccess: (data) => {
      setCompileResult(data);
      setIsCompiling(false);
    },
    onError: (error) => {
      setIsCompiling(false);
      console.error('Compile error:', error);
    },
  });

  const runMutation = useMutation({
    mutationFn: ({ exerciseId, code }: { exerciseId: number; code: string }) =>
      exercisesApi.run(exerciseId, { code, exercise_id: exerciseId }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      if (data.output) setTerminalOutput(data.output);
      if (data.error) setTerminalError(data.error);
    },
    onError: (error: any) => {
      setTerminalError(error.response?.data?.detail || 'Execution failed');
    },
  });

  const submitMutation = useMutation({
    mutationFn: ({ exerciseId, code }: { exerciseId: number; code: string }) =>
      exercisesApi.submit(exerciseId, { code, exercise_id: exerciseId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['exercise', exerciseId] });
    },
  });

  useEffect(() => {
    if (starterData) {
      try {
        const starter = typeof starterData === 'string' ? JSON.parse(starterData) : starterData;
        if (starter.nodes && starter.edges) {
          const newState: VisualEditorState = {
            nodes: starter.nodes,
            edges: starter.edges,
            selectedNodeId: null,
            history: [{ nodes: starter.nodes, edges: starter.edges }],
            historyIndex: 0,
          };
          setState(newState);
        }
      } catch (e) {
        console.error('Failed to parse starter data:', e);
      }
    }
  }, [starterData]);

  const saveToHistory = (newNodes: Node[], newEdges: Edge[]) => {
    setState((prev) => {
      const newHistory = prev.history.slice(0, prev.historyIndex + 1);
      newHistory.push({ nodes: newNodes, edges: newEdges });
      if (newHistory.length > 50) newHistory.shift();
      return {
        ...prev,
        nodes: newNodes,
        edges: newEdges,
        history: newHistory,
        historyIndex: newHistory.length - 1,
      };
    });
  };

  const handleUndo = () => {
    setState((prev) => {
      if (prev.historyIndex > 0) {
        const newIndex = prev.historyIndex - 1;
        const historyItem = prev.history[newIndex];
        return {
          ...prev,
          nodes: historyItem.nodes,
          edges: historyItem.edges,
          historyIndex: newIndex,
        };
      }
      return prev;
    });
  };

  const handleRedo = () => {
    setState((prev) => {
      if (prev.historyIndex < prev.history.length - 1) {
        const newIndex = prev.historyIndex + 1;
        const historyItem = prev.history[newIndex];
        return {
          ...prev,
          nodes: historyItem.nodes,
          edges: historyItem.edges,
          historyIndex: newIndex,
        };
      }
      return prev;
    });
  };

  const addNode = (type: string, position: { x: number; y: number }) => {
    const nodeConfig = NODE_PALETTE.find((n) => n.type === type)?.defaultConfig || {};
    const newNode: Node = {
      id: `node-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      position,
      config: { ...nodeConfig },
    };
    const newNodes = [...state.nodes, newNode];
    saveToHistory(newNodes, state.edges);
    setState((prev) => ({ ...prev, nodes: newNodes, selectedNodeId: newNode.id }));
  };

  const updateNodeConfig = (nodeId: string, config: Record<string, string>) => {
    const newNodes = state.nodes.map((node) =>
      node.id === nodeId ? { ...node, config: { ...node.config, ...config } } : node
    );
    saveToHistory(newNodes, state.edges);
    setState((prev) => ({ ...prev, nodes: newNodes }));
  };

  const deleteNode = (nodeId: string) => {
    const newNodes = state.nodes.filter((n) => n.id !== nodeId);
    const newEdges = state.edges.filter((e) => e.source !== nodeId && e.target !== nodeId);
    saveToHistory(newNodes, newEdges);
    setState((prev) => ({
      ...prev,
      nodes: newNodes,
      edges: newEdges,
      selectedNodeId: prev.selectedNodeId === nodeId ? null : prev.selectedNodeId,
    }));
  };

  const deleteEdge = (edgeId: string) => {
    const newEdges = state.edges.filter((e) => e.id !== edgeId);
    saveToHistory(state.nodes, newEdges);
    setState((prev) => ({ ...prev, edges: newEdges }));
  };

  const selectNode = (nodeId: string | null) => {
    setState((prev) => ({ ...prev, selectedNodeId: nodeId }));
  };

  const handleNodeDrag = (nodeId: string, deltaX: number, deltaY: number) => {
    const newNodes = state.nodes.map((node) =>
      node.id === nodeId
        ? { ...node, position: { x: node.position.x + deltaX, y: node.position.y + deltaY } }
        : node
    );
    setState((prev) => ({ ...prev, nodes: newNodes }));
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      selectNode(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const type = e.dataTransfer.getData('node-type') as string;
    if (!type) return;

    const canvasRect = canvasRef.current?.getBoundingClientRect();
    if (!canvasRect) return;

    const position = {
      x: e.clientX - canvasRect.left,
      y: e.clientY - canvasRect.top,
    };
    addNode(type, position);
  };

  const handleConnect = (sourceId: string, targetId: string, _sourceHandle?: string, _targetHandle?: string) => {
    if (sourceId === targetId) return;

    const existingEdge = state.edges.find((e) => e.source === sourceId && e.target === targetId);
    if (existingEdge) return;

    const newEdge: Edge = {
      id: `edge-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      source: sourceId,
      target: targetId,
    };
    const newEdges = [...state.edges, newEdge];
    saveToHistory(state.nodes, newEdges);
    setState((prev) => ({ ...prev, edges: newEdges }));
  };

  const handleCompile = async () => {
    setIsCompiling(true);
    setTerminalOutput('');
    setTerminalError('');
    try {
      await compileMutation.mutateAsync({ nodes: state.nodes, edges: state.edges } as any);
    } catch (error) {
      console.error('Compile error:', error);
    }
  };

  const handleRun = async () => {
    if (!exerciseId) return;
    if (!compileResult?.is_valid) {
      await handleCompile();
      if (!compileResult?.is_valid) return;
    }
    setTerminalOutput('');
    setTerminalError('');
    runMutation.mutate({ exerciseId: Number(exerciseId), code: compileResult!.python_code });
  };

  const handleSubmit = async () => {
    if (!exerciseId) return;
    if (!compileResult?.is_valid) {
      await handleCompile();
      if (!compileResult?.is_valid) return;
    }
    setTerminalOutput('');
    setTerminalError('');
    submitMutation.mutate({ exerciseId: Number(exerciseId), code: compileResult!.python_code });
  };

  const downloadCode = () => {
    if (!compileResult) return;
    const blob = new Blob([compileResult.python_code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `visual_program_${exerciseId}.py`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getHandlePosition = (node: Node, isSource: boolean) => {
    const nodeWidth = 180;
    const nodeHeight = 60;
    if (isSource) {
      return { x: node.position.x + nodeWidth, y: node.position.y + nodeHeight / 2 };
    }
    return { x: node.position.x, y: node.position.y + nodeHeight / 2 };
  };

  const isLoading = !exercise;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-bg-primary" dir={isRTL ? 'rtl' : 'ltr'}>
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <Skeleton variant="text" width="30%" height={24} data-testid="loading-spinner" />
            <Skeleton variant="rectangular" width={200} height={36} />
          </div>
          <div className="grid lg:grid-cols-[300px_1fr_320px] gap-6">
            <aside className="space-y-6">
              <Skeleton variant="rectangular" width="100%" height={300} />
              <Skeleton variant="rectangular" width="100%" height={200} />
              <Skeleton variant="rectangular" width="100%" height={200} />
            </aside>
            <div className="flex-1">
              <Skeleton variant="rectangular" width="100%" height={600} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="text-center py-12" dir={isRTL ? 'rtl' : 'ltr'}>
        <p className="text-error-600 dark:text-error-400">Exercise not found</p>
        <Link to="/app/courses" className="mt-4 inline-block text-primary-400 hover:text-primary-300">
          {t('common.back_to_courses')}
        </Link>
      </div>
    );
  }

  const exerciseTitle = exercise.translations[0]?.prompt || `Exercise ${exercise.id}`;
  const exercisePrompt = exercise.translations[0]?.prompt || '';

  const groupedPalette = NODE_PALETTE.reduce((acc, node) => {
    if (!acc[node.category]) acc[node.category] = [];
    acc[node.category].push(node);
    return acc;
  }, {} as Record<string, typeof NODE_PALETTE>);

  return (
    <div className="min-h-screen bg-bg-primary" dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <Link to="/app/courses" className="inline-flex items-center gap-2 text-text-tertiary hover:text-primary-400 dark:hover:text-primary-300 text-sm font-medium transition-colors">
            <ArrowLeft className="h-4 w-4" />
            <span>{t('common.back')}</span>
          </Link>
          <div className="flex items-center gap-2">
            <Link to={`/app/courses/${exercise.course_id}`} className="text-sm text-primary-400 hover:text-primary-300">
              {t('courses.course')} {exercise.course_id}
            </Link>
            <span className="text-text-tertiary">/</span>
            <Link to={`/app/lessons/${exercise.lesson_id}`} className="text-sm text-primary-400 hover:text-primary-300">
              {t('lessons.lesson')} {exercise.lesson_id}
            </Link>
          </div>
        </div>

        <div className="mb-6">
          <div className="flex items-center gap-2 mb-2">
            <StatusBadge status="current" size="sm" />
            <Badge variant="primary" size="sm" dot dotColor="primary">
              {t('visual_programming.visual_programming')}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold text-text-primary">{exerciseTitle}</h1>
          <p className="text-text-secondary mt-1">{exercisePrompt}</p>
        </div>

        <div className="grid lg:grid-cols-[300px_1fr_320px] gap-6">
          <aside className="space-y-6">
            <Card variant="default" padding="lg" className="relative overflow-hidden">
              <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
              <div className="relative z-10">
                <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-accent-400" />
                  <span>{t('visual_programming.palette')}</span>
                </h2>
                <div className="space-y-4">
                  {Object.entries(groupedPalette).map(([category, nodes]) => (
                    <div key={category} className="space-y-2">
                      <div className="flex items-center gap-2 px-2 py-1 text-xs font-semibold text-text-tertiary uppercase tracking-wider">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: category === 'control' ? '#3B82F6' : category === 'data' ? '#F97316' : '#10B981' }} />
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </div>
                      <div className="space-y-1.5">
                        {nodes.map((nodeType) => (
                          <button
                            key={nodeType.type}
                            draggable
                            onDragStart={(e) => {
                              e.dataTransfer.setData('node-type', nodeType.type);
                              e.dataTransfer.effectAllowed = 'copy';
                            }}
                            onDragEnd={(e) => e.preventDefault()}
                            className={cn(
                              'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-fast group',
                              CATEGORY_COLORS[category as keyof typeof CATEGORY_COLORS],
                              'hover:shadow-lg hover:shadow-glow-primary hover:-translate-x-0.5'
                            )}
                          >
                            <span className="text-2xl">{nodeType.icon}</span>
                            <span className="font-medium">{nodeType.label}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>

            <Card variant="default" padding="lg" className="relative overflow-hidden">
              <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
              <div className="relative z-10">
                <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  <span>{t('visual_programming.code_preview')}</span>
                </h2>
                <Button
                  variant="outline"
                  onClick={() => setShowCodePreview(!showCodePreview)}
                  className="w-full mb-3"
                >
                  {showCodePreview ? t('visual_programming.hide_code') : t('visual_programming.show_code')}
                </Button>
                {showCodePreview && compileResult && (
                  <CodeEditor
                    code={compileResult.python_code}
                    onChange={() => {}}
                    language="python"
                    readOnly={true}
                    showLineNumbers
                    minHeight="300px"
                    showToolbar
                  />
                )}
              </div>
            </Card>

            <Card variant="default" padding="lg" className="relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5" aria-hidden="true" />
              <div className="relative z-10">
                <h2 className="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
                  <Terminal className="h-5 w-5" />
                  <span>{t('visual_programming.actions')}</span>
                </h2>
                <div className="space-y-2">
                  <Button
                    onClick={() => {
                      setIsCompiling(true);
                      compileMutation.mutate({ nodes: state.nodes, edges: state.edges } as any);
                    }}
                    disabled={isCompiling || state.nodes.length === 0}
                    className="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
                    leftIcon={isCompiling ? <RotateCcw className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
                  >
                    {isCompiling ? t('visual_programming.compiling') : t('visual_programming.compile')}
                  </Button>
                  <Button
                    onClick={handleRun}
                    disabled={isCompiling || !compileResult?.is_valid}
                    className="w-full bg-gradient-to-r from-success-500 to-success-600 hover:from-success-600 hover:to-success-700 shadow-lg hover:shadow-glow-success"
                    leftIcon={<Play className="h-4 w-4" />}
                  >
                    {t('visual_programming.run_program')}
                  </Button>
                  <Button
                    onClick={handleSubmit}
                    disabled={!compileResult?.is_valid}
                    className="w-full bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent"
                    leftIcon={<CheckCircle className="h-4 w-4" />}
                  >
                    {t('visual_programming.submit_solution')}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleUndo}
                    disabled={state.historyIndex <= 0}
                    className="w-full"
                    leftIcon={<RotateCcw className="h-4 w-4" />}
                  >
                    {t('visual_programming.undo')}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleRedo}
                    disabled={state.historyIndex >= state.history.length - 1}
                    className="w-full"
                    leftIcon={<RotateCcw className="h-4 w-4" style={{ transform: 'scaleX(-1)' }} />}
                  >
                    {t('visual_programming.redo')}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setState({
                      nodes: [],
                      edges: [],
                      selectedNodeId: null,
                      history: [],
                      historyIndex: -1,
                    })}
                    className="w-full text-error-400 hover:bg-error-500/10 hover:border-error-500/30"
                    leftIcon={<Trash2 className="h-4 w-4" />}
                  >
                    {t('visual_programming.clear_canvas')}
                  </Button>
                </div>
              </div>
            </Card>

            {compileResult && !compileResult.is_valid && (
              <Alert variant="error" className="animate-slide-up border-error-500/30 bg-error-500/5">
                <h3 className="font-semibold text-error-400 mb-2">
                  {t('visual_programming.validation_errors')}
                </h3>
                <ul className="text-sm text-error-300 space-y-1">
                  {compileResult.errors.map((error, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <X className="h-4 w-4 text-error-400 flex-shrink-0 mt-0.5" />
                      <span>{error}</span>
                    </li>
                  ))}
                </ul>
              </Alert>
            )}
          </aside>

          <section aria-label="Visual Programming Canvas">
            <Card variant="default" padding="none" className="overflow-hidden relative">
              <div className="flex items-center justify-between p-4 border-b border-border-primary/50">
                <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                  <Terminal className="h-5 w-5 text-accent-400" />
                  <span>{t('visual_programming.visual_editor')}</span>
                </h2>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="sm" className="p-2" onClick={() => {
                    const wrapper = document.getElementById('visual-canvas-wrapper');
                    if (wrapper) wrapper.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
                  }} title={t('visual_programming.fit_view')}>
                    <RotateCcw className="h-5 w-5" style={{ transform: 'rotate(45deg)' }} />
                  </Button>
                  <Button variant="ghost" size="sm" className="p-2" onClick={() => { const w = document.getElementById('visual-canvas-wrapper'); if (w) w.scrollBy({ left: -200, top: 0, behavior: 'smooth' }); }} title={t('visual_programming.zoom_out')}>
                    <Minus className="h-5 w-5" />
                  </Button>
                  <Button variant="ghost" size="sm" className="p-2" onClick={() => { const w = document.getElementById('visual-canvas-wrapper'); if (w) w.scrollBy({ left: 200, top: 0, behavior: 'smooth' }); }} title={t('visual_programming.zoom_in')}>
                    <Plus className="h-5 w-5" />
                  </Button>
                </div>
              </div>

              <div
                id="visual-canvas-wrapper"
                className="relative h-[600px] bg-bg-code/50"
                onClick={handleCanvasClick}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <div ref={canvasRef} className="absolute inset-0 bg-grid-pattern" style={{ backgroundSize: '40px 40px' }}>
                  {/* Edges */}
                  {state.edges.map((edge) => {
                    const sourceNode = state.nodes.find((n) => n.id === edge.source);
                    const targetNode = state.nodes.find((n) => n.id === edge.target);
                    if (!sourceNode || !targetNode) return null;

                    const sourcePos = getHandlePosition(sourceNode, true);
                    const targetPos = getHandlePosition(targetNode, false);

                    const path = `M ${sourcePos.x} ${sourcePos.y} C ${sourcePos.x + 100} ${sourcePos.y} ${targetPos.x - 100} ${targetPos.y} ${targetPos.x} ${targetPos.y}`;

                    return (
                      <svg key={edge.id} className="absolute inset-0 pointer-events-none" style={{ width: '100%', height: '100%' }}>
                        <defs>
                          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#64748B" />
                          </marker>
                        </defs>
                        <path
                          d={path}
                          stroke="#64748B"
                          strokeWidth={2}
                          fill="none"
                          markerEnd="url(#arrowhead)"
                        />
                      </svg>
                    );
                  })}
                  {/* Nodes */}
                  {state.nodes.map((node) => (
                    <VisualNode
                      key={node.id}
                      node={node}
                      isSelected={state.selectedNodeId === node.id}
                      onSelect={selectNode}
                      onDrag={handleNodeDrag}
                      onDelete={deleteNode}
                      onConfigChange={updateNodeConfig}
                      onConnect={handleConnect}
                      t={t}
                    />
                  ))}
                </div>
              </div>
            </Card>
          </section>
        </div>

        <TerminalPanel
          output={terminalOutput}
          error={terminalError}
          isRunning={isCompiling || runMutation.isPending}
          clearable={true}
          onClear={() => { setTerminalOutput(''); setTerminalError(''); }}
          className="lg:col-span-3 h-80"
        />
      </div>
    </div>
  );
}

export default VisualProgrammingPage;