import { useEffect, useRef, useState } from 'react';
import { Bot, Send, User as UserIcon } from 'lucide-react';
import { Button, cn } from './ui';
import { useCodyChat } from '../hooks/useCodyChat';

interface CodyChatPanelProps {
  className?: string;
}

export function CodyChatPanel({ className }: CodyChatPanelProps) {
  const { messages, historyLoaded, sending, error, remaining, send } = useCodyChat();
  const [draft, setDraft] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, sending]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!draft.trim() || sending) return;
    send(draft);
    setDraft('');
  };

  return (
    <div className={cn('flex flex-col h-full min-h-0', className)}>
      <div ref={scrollRef} className="flex-1 min-h-0 overflow-y-auto px-4 py-4 space-y-4">
        {!historyLoaded && (
          <div className="flex items-center justify-center py-8 text-text-tertiary text-sm">
            Loading your conversation…
          </div>
        )}

        {historyLoaded && messages.length === 0 && (
          <div className="flex flex-col items-center text-center gap-2 py-8 px-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-accent-500">
              <Bot className="h-5 w-5 text-white" aria-hidden="true" />
            </div>
            <p className="text-sm font-medium text-text-primary">Hey, I'm Cody.</p>
            <p className="text-sm text-text-tertiary">
              Ask me anything about computer science — or what to learn next.
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={cn('flex items-start gap-2', m.role === 'user' && 'flex-row-reverse')}
          >
            <div
              className={cn(
                'flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full',
                m.role === 'user'
                  ? 'bg-bg-tertiary text-text-secondary'
                  : 'bg-gradient-to-br from-primary-500 to-accent-500 text-white'
              )}
              aria-hidden="true"
            >
              {m.role === 'user' ? <UserIcon className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>
            <div
              className={cn(
                'max-w-[80%] rounded-2xl px-3.5 py-2 text-sm whitespace-pre-wrap break-words',
                m.role === 'user'
                  ? 'bg-primary-500 text-white rounded-tr-sm'
                  : 'bg-bg-secondary text-text-primary rounded-tl-sm border border-border-primary'
              )}
            >
              {m.content}
            </div>
          </div>
        ))}

        {sending && (
          <div className="flex items-start gap-2">
            <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-accent-500">
              <Bot className="h-4 w-4 text-white" aria-hidden="true" />
            </div>
            <div className="rounded-2xl rounded-tl-sm border border-border-primary bg-bg-secondary px-3.5 py-2.5">
              <span className="flex gap-1" aria-label="Cody is typing">
                <span className="h-1.5 w-1.5 rounded-full bg-text-tertiary animate-pulse-glow" />
                <span className="h-1.5 w-1.5 rounded-full bg-text-tertiary animate-pulse-glow [animation-delay:0.15s]" />
                <span className="h-1.5 w-1.5 rounded-full bg-text-tertiary animate-pulse-glow [animation-delay:0.3s]" />
              </span>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mx-4 mb-2 rounded-lg border border-error-500/30 bg-error-50 dark:bg-error-900/20 px-3 py-2 text-xs text-error-600 dark:text-error-400">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="border-t border-border-primary p-3 flex items-end gap-2">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder="Ask Cody a CS question…"
          rows={1}
          disabled={sending}
          className="flex-1 resize-none rounded-xl border border-border-primary bg-bg-primary px-3 py-2 text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary-500/40 max-h-28"
        />
        <Button type="submit" size="sm" variant="primary" disabled={sending || !draft.trim()} aria-label="Send message">
          <Send className="h-4 w-4" />
        </Button>
      </form>
      {remaining !== null && remaining <= 5 && (
        <p className="px-4 pb-2 text-[11px] text-text-tertiary">
          {remaining === 0 ? "You've reached this hour's message limit." : `${remaining} message${remaining === 1 ? '' : 's'} left this hour.`}
        </p>
      )}
    </div>
  );
}
