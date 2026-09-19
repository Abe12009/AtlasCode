import { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, Bug } from 'lucide-react';
import { Button, cn } from '../ui';
import { useTranslation } from '../../hooks/useTranslation';
import type { TraceStep } from '../../types';

interface DebugTracePanelProps {
  code: string;
  trace: TraceStep[];
}

function formatValue(value: unknown): string {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

/**
 * Read-only step-through inspector for a Break-the-Code exercise: highlights
 * the line the buggy code's real, once-recorded execution was on at each
 * step, and shows every local variable's value at that point. Never grades
 * anything -- the student still writes and submits their fix through the
 * ordinary CodeEditor this renders above (see ExercisePanel).
 */
export function DebugTracePanel({ code, trace }: DebugTracePanelProps) {
  const { t, isRTL } = useTranslation();
  const [stepIndex, setStepIndex] = useState(0);

  const lines = useMemo(() => code.split('\n'), [code]);
  const step = trace[stepIndex];
  const previousLocals = stepIndex > 0 ? trace[stepIndex - 1].locals : {};

  const goPrev = () => setStepIndex((i) => Math.max(0, i - 1));
  const goNext = () => setStepIndex((i) => Math.min(trace.length - 1, i + 1));

  if (!step) return null;

  const localEntries = Object.entries(step.locals);

  return (
    <div className="space-y-3 rounded-xl border border-border-primary bg-bg-secondary/40 p-4" dir={isRTL ? 'rtl' : 'ltr'}>
      <div className="flex items-center gap-2 text-sm font-semibold text-text-primary">
        <Bug className="h-4 w-4 text-warning-500" />
        {t('break_the_code.title')}
      </div>

      {/* Always stacked, never side-by-side: this panel can end up nested
          two grids deep (ExercisePanel's own code/terminal split, itself
          inside the Micro-Quest layout), so a viewport-width breakpoint like
          `lg:` has no idea how little horizontal room its actual parent
          column has -- a side-by-side split reliably crushed the code down
          to a handful of visible characters. Stacking is the one layout that
          holds up regardless of nesting depth. */}
      <div className="space-y-4">
        <pre dir="ltr" className="rounded-lg bg-bg-code text-left p-3 text-sm font-mono overflow-x-auto">
          {lines.map((line, i) => {
            const lineNumber = i + 1;
            const isCurrent = lineNumber === step.line;
            return (
              <div
                key={i}
                data-testid={isCurrent ? 'trace-current-line' : undefined}
                className={cn('px-2 -mx-2 rounded', isCurrent && 'bg-warning-500/20 border-l-2 border-warning-500')}
              >
                <span className="inline-block w-8 text-text-quaternary select-none">{lineNumber}</span>
                <span className="text-gray-100">{line || ' '}</span>
              </div>
            );
          })}
        </pre>

        <div className="space-y-1" dir="ltr">
          <div className="text-xs font-semibold uppercase tracking-wide text-text-quaternary">
            {t('break_the_code.variables')}
          </div>
          {localEntries.length === 0 ? (
            <p className="text-sm text-text-quaternary">{t('break_the_code.no_variables_yet')}</p>
          ) : (
            <dl className="space-y-1 text-sm font-mono">
              {localEntries.map(([name, value]) => {
                const changed = formatValue(value) !== formatValue(previousLocals[name]);
                return (
                  <div
                    key={name}
                    data-testid={`trace-var-${name}`}
                    className={cn('flex justify-between gap-2 rounded px-2 py-1', changed && 'bg-primary-500/10')}
                  >
                    <dt className="text-text-secondary">{name}</dt>
                    <dd className={cn('truncate text-text-primary', changed && 'font-semibold text-primary-400')}>
                      {formatValue(value)}
                    </dd>
                  </div>
                );
              })}
            </dl>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <Button variant="outline" size="sm" onClick={goPrev} disabled={stepIndex === 0} leftIcon={<ChevronLeft className="h-4 w-4" />}>
          {t('break_the_code.prev_step')}
        </Button>
        <span className="text-sm text-text-tertiary" data-testid="trace-step-counter">
          {t('break_the_code.step_counter', { current: stepIndex + 1, total: trace.length })}
        </span>
        <Button variant="outline" size="sm" onClick={goNext} disabled={stepIndex === trace.length - 1} rightIcon={<ChevronRight className="h-4 w-4" />}>
          {t('break_the_code.next_step')}
        </Button>
      </div>
    </div>
  );
}
