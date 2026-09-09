import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Zap } from 'lucide-react';

const XP_TOAST_EVENT = 'xp-toast';
const DISPLAY_MS = 2600;

interface XpToastDetail {
  amount: number;
}

/** Fires a brief "+N XP" toast in the corner. Event-based (like
 * pulseCodyBubble) rather than context/props, since this is triggered from
 * arbitrary mutation call sites (exercise submit, lesson completion, ...)
 * that shouldn't need to thread a callback down to reach it. */
export function showXpToast(amount: number) {
  if (amount <= 0) return;
  window.dispatchEvent(new CustomEvent<XpToastDetail>(XP_TOAST_EVENT, { detail: { amount } }));
}

interface ToastEntry {
  id: number;
  amount: number;
}

let nextId = 0;

/** Renders the queue of active XP toasts. Mount once, near the app root. */
export function XpToastHost() {
  const [toasts, setToasts] = useState<ToastEntry[]>([]);

  useEffect(() => {
    function handleToast(e: Event) {
      const { amount } = (e as CustomEvent<XpToastDetail>).detail;
      const id = nextId++;
      setToasts((prev) => [...prev, { id, amount }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, DISPLAY_MS);
    }
    window.addEventListener(XP_TOAST_EVENT, handleToast);
    return () => window.removeEventListener(XP_TOAST_EVENT, handleToast);
  }, []);

  return (
    <div className="fixed top-20 right-4 z-[70] flex flex-col items-end gap-2 pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, x: 24, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="flex items-center gap-2 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 px-4 py-2 text-sm font-semibold text-white shadow-elevated"
          >
            <Zap className="h-4 w-4" aria-hidden="true" />
            +{toast.amount} XP
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
