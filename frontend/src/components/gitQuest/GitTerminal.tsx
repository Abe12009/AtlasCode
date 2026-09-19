import { useRef, useState, useEffect } from 'react';
import { useTranslation } from '../../hooks/useTranslation';
import { cn } from '../../lib/utils';

export interface TerminalEntry {
  command: string;
  output: string;
  error: string | null;
}

interface GitTerminalProps {
  history: TerminalEntry[];
  onCommand: (command: string) => void;
  disabled?: boolean;
}

/**
 * The typed half of Git Quest's terminal: a scrolling transcript of past
 * commands/output plus a real input line, styled to match the existing
 * output-only TerminalPanel (ui/CodeEditor.tsx) so the two read as the same
 * kind of surface even though this one accepts input and that one doesn't.
 */
export function GitTerminal({ history, onCommand, disabled }: GitTerminalProps) {
  const { t } = useTranslation();
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const submit = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onCommand(trimmed);
    setInput('');
  };

  return (
    <div dir="ltr" className="border border-border-primary rounded-xl overflow-hidden bg-bg-code flex flex-col">
      <div className="flex items-center gap-2 px-3 py-2 bg-bg-code-light border-b border-border-primary">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
        </div>
        <span className="text-xs text-gray-400 ms-1">terminal</span>
      </div>

      <div ref={scrollRef} className="p-3 h-64 overflow-y-auto font-mono text-sm text-gray-100 space-y-2" data-testid="git-terminal-history">
        {history.length === 0 && <p className="text-gray-500">{t('git_quest.terminal_empty')}</p>}
        {history.map((entry, i) => (
          <div key={i}>
            <div className="text-primary-400">$ {entry.command}</div>
            {/* A 'conflict' isn't a separate message -- it's the same
                `output` git already prints (the CONFLICT/"fix conflicts"
                lines), just re-colored as a warning. Rendering both the
                plain block below AND this one would show that text twice. */}
            {entry.output && entry.error !== 'conflict' && (
              <pre className="whitespace-pre-wrap text-gray-300">{entry.output}</pre>
            )}
            {entry.error && (
              <pre className={cn('whitespace-pre-wrap', entry.error === 'conflict' ? 'text-warning-400' : 'text-error-400')}>
                {entry.error === 'conflict' ? entry.output : entry.error}
              </pre>
            )}
          </div>
        ))}
      </div>

      <div className="flex items-center gap-2 px-3 py-2 border-t border-border-primary">
        <span className="text-primary-400 font-mono text-sm select-none">$</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') submit();
          }}
          disabled={disabled}
          placeholder={t('git_quest.terminal_placeholder')}
          className="flex-1 bg-transparent font-mono text-sm text-gray-100 placeholder:text-gray-600 focus:outline-none disabled:opacity-50"
          data-testid="git-terminal-input"
          autoComplete="off"
          spellCheck={false}
        />
      </div>
    </div>
  );
}
