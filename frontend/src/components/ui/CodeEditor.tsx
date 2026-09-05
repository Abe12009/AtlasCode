import { forwardRef, useState, useRef, useEffect, type TextareaHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';
import { Copy, Check, RotateCcw, Play } from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';

export interface CodeEditorProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'onChange'> {
  code: string;
  onChange: (code: string) => void;
  language?: string;
  readOnly?: boolean;
  theme?: 'dark' | 'light';
  showLineNumbers?: boolean;
  minHeight?: string;
  placeholder?: string;
  onRun?: () => void;
  onSubmit?: () => void;
  isRunning?: boolean;
  isSubmitting?: boolean;
  showToolbar?: boolean;
}

export const CodeEditor = forwardRef<HTMLTextAreaElement, CodeEditorProps>(
  (
    {
      className,
      code,
      onChange,
      language = 'python',
      readOnly = false,
      showLineNumbers = false,
      minHeight = '200px',
      placeholder,
      onRun,
      onSubmit,
      isRunning = false,
      isSubmitting = false,
      showToolbar = true,
      ...props
    },
    ref,
  ) => {
    const { t } = useTranslation();
    const [copied, setCopied] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const lineNumbersRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      if (textareaRef.current && lineNumbersRef.current) {
        lineNumbersRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
      }
    }, [code]);

    const handleCopy = async () => {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = e.currentTarget.selectionStart;
        const end = e.currentTarget.selectionEnd;
        const newCode = code.substring(0, start) + '    ' + code.substring(end);
        onChange(newCode);
        setTimeout(() => {
          if (textareaRef.current) {
            textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 4;
          }
        }, 0);
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        if (onSubmit && !isSubmitting) {
          e.preventDefault();
          onSubmit();
        }
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'r') {
        if (onRun && !isRunning) {
          e.preventDefault();
          onRun();
        }
      }
    };

    const lines = code.split('\n');
    const lineCount = lines.length;

    // Code is always left-to-right, independent of the surrounding page's
    // reading direction — see CodeBlock.tsx for the same rule applied to
    // static (non-editable) snippets.
    return (
      <div dir="ltr" className={cn('border border-border-primary rounded-xl overflow-hidden bg-bg-code', className)}>
        {showToolbar && (
          <div className="flex items-center justify-between px-3 py-2 bg-bg-code-light border-b border-border-primary">
            <span className="text-xs text-text-tertiary font-mono uppercase tracking-wider">{language}</span>
            <div className="flex items-center gap-1">
              <button
                onClick={handleCopy}
                className="p-1.5 rounded hover:bg-bg-tertiary transition-colors"
                title={t('common.copy')}
                aria-label={t('common.copy')}
              >
                {copied ? <Check className="h-4 w-4 text-success-500" /> : <Copy className="h-4 w-4 text-text-tertiary" />}
              </button>
              {onRun && (
                <button
                  onClick={onRun}
                  disabled={isRunning}
                  className="p-1.5 rounded hover:bg-bg-tertiary transition-colors disabled:opacity-50"
                  title={t('lessons.run_code')}
                  aria-label={t('lessons.run_code')}
                  data-testid="code-editor-run-btn"
                >
                  {isRunning ? <RotateCcw className="h-4 w-4 animate-spin text-primary-400" /> : <Play className="h-4 w-4 text-text-tertiary" />}
                </button>
              )}
            </div>
          </div>
        )}
        <div className="flex">
          {showLineNumbers && (
            <div
              ref={lineNumbersRef}
              className="bg-bg-code-light border-r border-border-primary px-3 py-4 font-mono text-xs text-text-tertiary select-none overflow-hidden"
              aria-hidden="true"
            >
              {Array.from({ length: lineCount }, (_, i) => i + 1).map((num) => (
                <div key={num} className="h-5 leading-5 text-right tabular-nums">{num}</div>
              ))}
            </div>
          )}
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            readOnly={readOnly}
            className={cn(
              'w-full bg-transparent focus:outline-none resize-y',
              'font-mono text-sm text-text-primary',
              'placeholder:text-text-quaternary',
              'tab-size-4',
              showLineNumbers ? 'pl-0' : 'pl-4',
              'pr-4 py-4'
            )}
            style={{ minHeight, lineHeight: 1.6 }}
            spellCheck={false}
            placeholder={placeholder}
            {...props}
          />
        </div>
      </div>
    );
  },
);

CodeEditor.displayName = 'CodeEditor';

export interface TerminalPanelProps {
  output?: string;
  error?: string;
  isRunning?: boolean;
  clearable?: boolean;
  onClear?: () => void;
  className?: string;
  'data-testid'?: string;
}

export function TerminalPanel({ output, error, isRunning, clearable = true, onClear, className, 'data-testid': testId }: TerminalPanelProps) {
  const { t } = useTranslation();
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output, error]);

  return (
    <div dir="ltr" className={cn('border border-border-primary rounded-xl overflow-hidden bg-bg-code flex flex-col', className)} data-testid={testId}>
      <div className="flex items-center justify-between px-3 py-2 bg-bg-code-light border-b border-border-primary">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div className="w-3 h-3 rounded-full bg-green-500" />
          </div>
          <span className="text-xs text-text-tertiary font-mono">terminal</span>
        </div>
        <div className="flex items-center gap-2">
          {isRunning && <span className="text-xs text-primary-400 animate-pulse flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary-400" /> Running...</span>}
          {clearable && (
            <button
              onClick={onClear}
              className="p-1 rounded hover:bg-bg-tertiary transition-colors"
              title={t('common.clear')}
              aria-label={t('common.clear')}
            >
              <RotateCcw className="h-4 w-4 text-text-tertiary" />
            </button>
          )}
        </div>
      </div>
      <div
        ref={terminalRef}
        className="flex-1 p-4 font-mono text-sm text-gray-100 overflow-y-auto min-h-[150px] max-h-[400px]"
      >
        {output && (
          <div className="whitespace-pre-wrap text-text-primary animate-fade-in">{output}</div>
        )}
        {error && (
          <div className="whitespace-pre-wrap text-error-400 animate-fade-in mt-2">{error}</div>
        )}
        {!output && !error && !isRunning && (
          <div className="text-text-tertiary italic">{t('lessons.no_output')}</div>
        )}
        {isRunning && !output && (
          <div className="text-primary-400 animate-pulse">▶ Running...</div>
        )}
      </div>
    </div>
  );
}

TerminalPanel.displayName = 'TerminalPanel';