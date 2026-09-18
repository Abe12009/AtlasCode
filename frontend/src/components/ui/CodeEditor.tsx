import { useState, useRef, useEffect, useCallback } from 'react';
import CodeMirror, { type ReactCodeMirrorRef } from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import { keymap } from '@codemirror/view';
import { indentUnit } from '@codemirror/language';
import { cn } from '../../lib/utils';
import { Copy, Check, RotateCcw, Play } from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';

export interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  language?: string;
  readOnly?: boolean;
  theme?: 'dark' | 'light';
  showLineNumbers?: boolean;
  minHeight?: string;
  /** When set, the editor fills its parent's height (parent must be a flex
   * item with a real height, e.g. `flex-1 min-h-0`) instead of sizing to
   * `minHeight` -- used where the editor should grow to fill the available
   * space rather than the page scrolling past it. */
  fillHeight?: boolean;
  placeholder?: string;
  onRun?: () => void;
  onSubmit?: () => void;
  isRunning?: boolean;
  isSubmitting?: boolean;
  showToolbar?: boolean;
  /** Shown in the toolbar next to the window-control dots, e.g. "solution.py".
   * Defaults to a name derived from `language`. */
  filename?: string;
  className?: string;
}

const LANGUAGE_EXTENSIONS: Record<string, string> = {
  python: 'py',
};

export function CodeEditor({
  className,
  code,
  onChange,
  language = 'python',
  readOnly = false,
  showLineNumbers = false,
  minHeight = '200px',
  fillHeight = false,
  placeholder,
  onRun,
  onSubmit,
  isRunning = false,
  isSubmitting = false,
  showToolbar = true,
  filename,
}: CodeEditorProps) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const editorRef = useRef<ReactCodeMirrorRef>(null);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Ctrl/Cmd+Enter to submit and Ctrl/Cmd+R to run are the editor's own
  // established shortcuts (see the previous textarea-based implementation) --
  // wired as a CodeMirror keymap extension rather than a DOM keydown handler
  // so they keep working when the editor itself has focus.
  const submitRef = useRef(onSubmit);
  const runRef = useRef(onRun);
  const isSubmittingRef = useRef(isSubmitting);
  const isRunningRef = useRef(isRunning);
  submitRef.current = onSubmit;
  runRef.current = onRun;
  isSubmittingRef.current = isSubmitting;
  isRunningRef.current = isRunning;

  const shortcutKeymap = useCallback(
    () =>
      keymap.of([
        {
          key: 'Mod-Enter',
          run: () => {
            if (submitRef.current && !isSubmittingRef.current) {
              submitRef.current();
              return true;
            }
            return false;
          },
        },
        {
          key: 'Mod-r',
          run: () => {
            if (runRef.current && !isRunningRef.current) {
              runRef.current();
              return true;
            }
            return false;
          },
        },
      ]),
    []
  );

  const extensions = [python(), indentUnit.of('    '), shortcutKeymap()];

  const displayFilename = filename ?? `solution.${LANGUAGE_EXTENSIONS[language] ?? 'txt'}`;

  // Code is always left-to-right, independent of the surrounding page's
  // reading direction — see CodeBlock.tsx for the same rule applied to
  // static (non-editable) snippets.
  return (
    <div
      dir="ltr"
      className={cn(
        'border border-border-primary rounded-xl overflow-hidden bg-bg-code',
        fillHeight && 'h-full flex flex-col',
        className
      )}
    >
      {showToolbar && (
        <div className="flex items-center justify-between px-3 py-2 bg-bg-code-light border-b border-border-primary gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex gap-1.5 flex-shrink-0" aria-hidden="true">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
            <span className="text-xs text-text-secondary font-mono truncate">{displayFilename}</span>
            <span className="flex items-center gap-1.5 text-xs text-text-tertiary font-mono uppercase tracking-wider flex-shrink-0">
              <span className="w-1.5 h-1.5 rounded-full bg-success-500" data-testid="code-editor-status-dot" aria-hidden="true" />
              {language}
            </span>
          </div>
          <div className="flex items-center gap-1 flex-shrink-0">
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
      {readOnly ? (
        // A read-only CodeEditor is always static display, never live editing
        // (the compiled-code preview, a lesson's example, a locked project
        // task) -- rendered as plain text rather than through CodeMirror.
        // CodeMirror wraps syntax-highlighted tokens in their own <span>s, so
        // testing-library's getByText (which only reads an element's direct
        // text nodes, not descendant text) can never find code rendered that
        // way; a plain <pre> keeps the whole snippet as one real text node.
        <pre
          data-testid="code-editor"
          className={cn(
            'whitespace-pre-wrap overflow-x-auto font-mono text-sm text-text-primary px-4 py-4',
            fillHeight && 'flex-1 min-h-0 overflow-auto'
          )}
          style={{ fontSize: '0.875rem', ...(fillHeight ? {} : { minHeight }) }}
        >
          {code}
        </pre>
      ) : (
        <CodeMirror
          ref={editorRef}
          value={code}
          onChange={onChange}
          theme={oneDark}
          extensions={extensions}
          placeholder={placeholder}
          {...(fillHeight ? { height: '100%' } : { minHeight })}
          basicSetup={{
            lineNumbers: showLineNumbers,
            foldGutter: false,
            highlightActiveLine: true,
            highlightActiveLineGutter: true,
            autocompletion: false,
          }}
          style={{ fontSize: '0.875rem', ...(fillHeight ? { flex: 1, minHeight: 0, overflow: 'auto' } : {}) }}
          data-testid="code-editor"
        />
      )}
    </div>
  );
}

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
        role="status"
        aria-live="polite"
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
