import { useEffect, useRef, useState } from 'react';
import { getWsBaseUrl } from '../api/client';
import type { DuelSocketMessage } from '../types';

export type DuelSocketStatus = 'connecting' | 'open' | 'closed';

/**
 * Opens the live duel WebSocket for one ticket. A ticket is single-use and
 * expires in ~20s (see backend/app/services/duel_tickets.py), so this never
 * retries with the same ticket string -- the caller mints a fresh one and
 * changes `ticket` to trigger a reconnect (DuelArena does this on an
 * unexpected close).
 *
 * The only messages this can ever receive are opponent_connected /
 * opponent_disconnected / opponent_progress / duel_ended -- the backend
 * never serializes a submitter's code into a broadcast, so there is no
 * "code" field in DuelSocketMessage for this hook (or its caller) to even
 * reach for.
 */
export function useDuelSocket(
  duelId: number | null,
  ticket: string | null,
  onMessage: (message: DuelSocketMessage) => void
): { status: DuelSocketStatus } {
  const [status, setStatus] = useState<DuelSocketStatus>('connecting');
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!duelId || !ticket) {
      return;
    }

    const url = `${getWsBaseUrl()}/duels/ws/${duelId}?ticket=${encodeURIComponent(ticket)}`;
    const socket = new WebSocket(url);
    setStatus('connecting');

    socket.onopen = () => setStatus('open');
    socket.onclose = () => setStatus('closed');
    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as DuelSocketMessage;
        onMessageRef.current(message);
      } catch {
        // Not a frame this client understands -- ignore rather than crash
        // the whole duel over a malformed message.
      }
    };

    return () => {
      socket.close();
    };
  }, [duelId, ticket]);

  return { status };
}
