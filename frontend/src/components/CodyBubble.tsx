import { useCallback, useEffect, useRef, useState } from 'react';
import { Bot, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { cn } from './ui';
import { CodyChatPanel } from './CodyChatPanel';

const BUBBLE_SIZE = 56;
const EDGE_MARGIN = 16;
const DRAG_THRESHOLD_PX = 4;
const PANEL_WIDTH = 360;
const PANEL_HEIGHT = 480;
// Keeps the popup from sliding under the fixed app header when the bubble
// sits high up the screen and the panel opens upward.
const HEADER_SAFE_TOP = 76;
const PULSE_DURATION_MS = 3000;
const PULSE_EVENT = 'cody-bubble-pulse';

/** Briefly highlights the bubble -- used by the onboarding walkthrough's
 * final step to point at where Cody lives after the modal closes. A window
 * event (rather than React state/context) because CodyBubble is already
 * mounted inside Layout by the time any page wants to trigger this, and a
 * global signal is simpler than threading a callback through the tree. */
export function pulseCodyBubble() {
  window.dispatchEvent(new Event(PULSE_EVENT));
}

interface Position {
  left: number;
  top: number;
}

function storageKey(userId: number) {
  return `cody_bubble_position_${userId}`;
}

function defaultPosition(): Position {
  return {
    left: window.innerWidth - BUBBLE_SIZE - EDGE_MARGIN,
    top: window.innerHeight - BUBBLE_SIZE - EDGE_MARGIN - 24,
  };
}

function clamp(pos: Position): Position {
  const maxLeft = window.innerWidth - BUBBLE_SIZE - EDGE_MARGIN;
  const maxTop = window.innerHeight - BUBBLE_SIZE - EDGE_MARGIN;
  return {
    left: Math.min(Math.max(pos.left, EDGE_MARGIN), Math.max(EDGE_MARGIN, maxLeft)),
    top: Math.min(Math.max(pos.top, EDGE_MARGIN), Math.max(EDGE_MARGIN, maxTop)),
  };
}

/** Floating, draggable chat entry point for Cody, visible on every
 * authenticated app page. Position is per-user and persisted to
 * localStorage -- it doesn't need to sync across devices, so this is
 * intentionally simpler than a DB-backed preference. */
export function CodyBubble() {
  const { user } = useAuth();
  const [position, setPosition] = useState<Position | null>(null);
  const [open, setOpen] = useState(false);
  const [pulsing, setPulsing] = useState(false);
  const draggingRef = useRef(false);
  const movedRef = useRef(false);
  const dragStartRef = useRef<{ pointerX: number; pointerY: number; left: number; top: number } | null>(null);
  const bubbleRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!user) return;
    try {
      const stored = localStorage.getItem(storageKey(user.id));
      if (stored) {
        setPosition(clamp(JSON.parse(stored)));
        return;
      }
    } catch {
      // Corrupt/unavailable storage falls back to the default corner.
    }
    setPosition(defaultPosition());
  }, [user]);

  useEffect(() => {
    function handleResize() {
      setPosition((prev) => (prev ? clamp(prev) : prev));
    }
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;
    function handlePulse() {
      setPulsing(true);
      clearTimeout(timeout);
      timeout = setTimeout(() => setPulsing(false), PULSE_DURATION_MS);
    }
    window.addEventListener(PULSE_EVENT, handlePulse);
    return () => {
      window.removeEventListener(PULSE_EVENT, handlePulse);
      clearTimeout(timeout);
    };
  }, []);

  const persistPosition = useCallback((pos: Position) => {
    if (!user) return;
    try {
      localStorage.setItem(storageKey(user.id), JSON.stringify(pos));
    } catch {
      // Best-effort only; nothing to recover from a full/blocked storage.
    }
  }, [user]);

  const handlePointerDown = (e: React.PointerEvent<HTMLButtonElement>) => {
    if (!position) return;
    draggingRef.current = true;
    movedRef.current = false;
    dragStartRef.current = { pointerX: e.clientX, pointerY: e.clientY, left: position.left, top: position.top };
    bubbleRef.current?.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLButtonElement>) => {
    if (!draggingRef.current || !dragStartRef.current) return;
    const dx = e.clientX - dragStartRef.current.pointerX;
    const dy = e.clientY - dragStartRef.current.pointerY;
    if (!movedRef.current && Math.hypot(dx, dy) > DRAG_THRESHOLD_PX) {
      movedRef.current = true;
    }
    if (movedRef.current) {
      setPosition(clamp({ left: dragStartRef.current.left + dx, top: dragStartRef.current.top + dy }));
    }
  };

  const handlePointerUp = () => {
    if (!draggingRef.current) return;
    draggingRef.current = false;
    if (movedRef.current) {
      setPosition((prev) => {
        if (prev) persistPosition(prev);
        return prev;
      });
    } else {
      setOpen((prev) => !prev);
    }
  };

  if (!user || !position) return null;

  const openUpward = position.top > window.innerHeight / 2;
  const openLeftward = position.left > window.innerWidth / 2;

  return (
    <>
      {open && (
        <div
          className="fixed z-[60] glass-strong rounded-2xl shadow-modal border border-border-primary flex flex-col overflow-hidden animate-scale-in"
          style={{
            width: PANEL_WIDTH,
            height: PANEL_HEIGHT,
            maxWidth: 'calc(100vw - 2rem)',
            maxHeight: 'calc(100vh - 2rem)',
            left: openLeftward
              ? Math.max(EDGE_MARGIN, position.left + BUBBLE_SIZE - PANEL_WIDTH)
              : Math.min(window.innerWidth - PANEL_WIDTH - EDGE_MARGIN, position.left),
            top: openUpward
              ? Math.max(HEADER_SAFE_TOP, position.top - PANEL_HEIGHT - 8)
              : Math.min(window.innerHeight - PANEL_HEIGHT - EDGE_MARGIN, position.top + BUBBLE_SIZE + 8),
          }}
          role="dialog"
          aria-label="Cody chat"
        >
          <div className="flex items-center justify-between px-4 py-3 border-b border-border-primary">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-accent-500">
                <Bot className="h-4 w-4 text-white" aria-hidden="true" />
              </div>
              <span className="text-sm font-semibold text-text-primary">Cody</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="p-1 rounded-lg text-text-tertiary hover:text-text-primary hover:bg-bg-tertiary transition-colors"
              aria-label="Close Cody chat"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <CodyChatPanel className="flex-1 min-h-0" />
        </div>
      )}

      {pulsing && (
        <span
          className="fixed z-[59] rounded-full bg-primary-400 animate-ping pointer-events-none"
          style={{ left: position.left, top: position.top, width: BUBBLE_SIZE, height: BUBBLE_SIZE }}
          aria-hidden="true"
        />
      )}

      <button
        ref={bubbleRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        className={cn(
          'fixed z-[60] flex items-center justify-center rounded-full',
          'bg-gradient-to-br from-primary-500 to-accent-500 shadow-elevated',
          'touch-none select-none cursor-grab active:cursor-grabbing',
          'hover:scale-105 transition-transform duration-fast'
        )}
        style={{ left: position.left, top: position.top, width: BUBBLE_SIZE, height: BUBBLE_SIZE }}
        aria-label={open ? 'Close Cody chat' : 'Open Cody chat'}
      >
        <Bot className="h-6 w-6 text-white" aria-hidden="true" />
      </button>
    </>
  );
}
