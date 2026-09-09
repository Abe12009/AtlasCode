import { useCallback, useEffect, useRef, useState } from 'react';
import type { AxiosError } from 'axios';
import { codyApi } from '../api/services';
import type { CodyMessage } from '../types';

/** Shared chat state/logic for Cody, used by both the nav page and the
 * floating bubble popup so the two surfaces behave identically. */
export function useCodyChat() {
  const [messages, setMessages] = useState<CodyMessage[]>([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const loadedRef = useRef(false);

  const loadHistory = useCallback(async () => {
    if (loadedRef.current) return;
    loadedRef.current = true;
    try {
      const history = await codyApi.getMessages();
      setMessages(history);
    } catch {
      // History is a nice-to-have; a failed fetch just starts an empty chat.
    } finally {
      setHistoryLoaded(true);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const send = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || sending) return;

    setError(null);
    const optimisticUser: CodyMessage = {
      role: 'user',
      content: trimmed,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUser]);
    setSending(true);

    try {
      const response = await codyApi.sendMessage(trimmed);
      setMessages((prev) => [...prev, response.reply]);
      setRemaining(response.messages_remaining_this_hour);
    } catch (err: unknown) {
      const axiosError = err as AxiosError<{ detail?: string }>;
      setError(axiosError.response?.data?.detail || "Cody couldn't respond just now. Please try again.");
      // Roll back the optimistic message so a failed send doesn't look sent.
      setMessages((prev) => prev.filter((m) => m !== optimisticUser));
    } finally {
      setSending(false);
    }
  }, [sending]);

  return { messages, historyLoaded, sending, error, remaining, send };
}
