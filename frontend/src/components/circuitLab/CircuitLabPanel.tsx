import { useEffect, useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Play, Check, Code2, RotateCcw } from 'lucide-react';
import { Button, CodeBlock } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import { circuitsApi } from '../../api/services';
import { CircuitCanvas } from './CircuitCanvas';
import type { CircuitGraph, Exercise } from '../../types';
import type { SubmitVars } from '../exerciseTypes';

interface CircuitLabPanelProps {
  exercise: Exercise;
  onSubmit: (vars: SubmitVars) => void;
  onRun: (vars: { exerciseId: number; code: string }) => void;
  isSubmitting: boolean;
  isRunning: boolean;
}

function parseStarter(raw: string | null): CircuitGraph {
  if (!raw) return { nodes: [], edges: [] };
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed.nodes) && Array.isArray(parsed.edges)) return parsed;
  } catch {
    // fall through to empty graph
  }
  return { nodes: [], edges: [] };
}

export function CircuitLabPanel({ exercise, onSubmit, onRun, isSubmitting, isRunning }: CircuitLabPanelProps) {
  const { t } = useTranslation();
  const starter = useMemo(() => parseStarter(exercise.starter_code), [exercise.starter_code]);
  const [graph, setGraph] = useState<CircuitGraph>(starter);
  const [inputToggles, setInputToggles] = useState<Record<string, boolean>>({});
  const [showCode, setShowCode] = useState(false);

  const evaluateMutation = useMutation({
    mutationFn: (vars: { graph: CircuitGraph; inputValues: Record<string, boolean> }) =>
      circuitsApi.evaluate(vars.graph, vars.inputValues),
  });

  const compileMutation = useMutation({
    mutationFn: (g: CircuitGraph) => circuitsApi.compile(g),
  });

  const inputValues = useMemo(() => {
    const values: Record<string, boolean> = {};
    for (const node of graph.nodes) {
      if (node.type === 'input' && node.config.name) {
        values[node.config.name] = !!inputToggles[node.id];
      }
    }
    return values;
  }, [graph.nodes, inputToggles]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (graph.nodes.length === 0) return;
      evaluateMutation.mutate({ graph, inputValues });
    }, 200);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graph, inputValues]);

  const handleToggleInput = (nodeId: string) => {
    setInputToggles((prev) => ({ ...prev, [nodeId]: !prev[nodeId] }));
  };

  const handleReset = () => {
    setGraph(starter);
    setInputToggles({});
  };

  const compileAndRun = async (action: 'run' | 'submit') => {
    const result = await compileMutation.mutateAsync(graph);
    if (!result.is_valid) return;
    if (action === 'run') {
      onRun({ exerciseId: exercise.id, code: result.python_code });
    } else {
      onSubmit({ exerciseId: exercise.id, code: result.python_code });
    }
  };

  const values = evaluateMutation.data?.values ?? {};
  const evalErrors = evaluateMutation.data?.errors ?? [];
  const compileErrors = compileMutation.data && !compileMutation.data.is_valid ? compileMutation.data.errors : [];

  return (
    <div className="space-y-4">
      <CircuitCanvas
        graph={graph}
        onChange={setGraph}
        values={values}
        inputToggles={inputToggles}
        onToggleInput={handleToggleInput}
        errors={evalErrors}
      />

      {compileErrors.length > 0 && (
        <div className="rounded-lg border border-error-500/30 bg-error-500/10 p-3 text-sm text-error-600 dark:text-error-400">
          {compileErrors.join(' · ')}
        </div>
      )}

      <div className="flex items-center gap-3 flex-wrap">
        <Button variant="outline" onClick={handleReset} leftIcon={<RotateCcw className="h-4 w-4" />}>
          {t('circuit_lab.reset')}
        </Button>
        <Button variant="outline" onClick={() => setShowCode((v) => !v)} leftIcon={<Code2 className="h-4 w-4" />}>
          {showCode ? t('circuit_lab.hide_code') : t('circuit_lab.show_code')}
        </Button>
        <div className="flex-1" />
        <Button
          variant="outline"
          onClick={() => compileAndRun('run')}
          disabled={isRunning || compileMutation.isPending}
          loading={isRunning || compileMutation.isPending}
          leftIcon={<Play className="h-4 w-4" />}
        >
          {t('lessons.run_code')}
        </Button>
        <Button
          onClick={() => compileAndRun('submit')}
          disabled={isSubmitting || compileMutation.isPending}
          loading={isSubmitting}
          leftIcon={<Check className="h-4 w-4" />}
          className="bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent"
        >
          {t('lessons.submit_solution')}
        </Button>
      </div>

      {showCode && compileMutation.data?.python_code && (
        <CodeBlock>{compileMutation.data.python_code}</CodeBlock>
      )}
    </div>
  );
}
