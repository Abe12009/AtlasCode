import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Award } from 'lucide-react';

const ACHIEVEMENT_TOAST_EVENT = 'achievement-toast';
const DISPLAY_MS = 3400;

interface AchievementToastDetail {
  icon: string;
  title: string;
  xpReward: number;
}

/** Fires an "Achievement Unlocked" toast in the corner, one per newly-earned
 * achievement. Same event-based pattern as showXpToast -- triggered from
 * arbitrary submit-response handlers that shouldn't need to thread a
 * callback down to reach it. */
export function showAchievementToast(icon: string, title: string, xpReward: number) {
  window.dispatchEvent(
    new CustomEvent<AchievementToastDetail>(ACHIEVEMENT_TOAST_EVENT, { detail: { icon, title, xpReward } })
  );
}

interface ToastEntry extends AchievementToastDetail {
  id: number;
}

let nextId = 0;

/** Renders the queue of active achievement toasts. Mount once, near the app root. */
export function AchievementToastHost() {
  const [toasts, setToasts] = useState<ToastEntry[]>([]);

  useEffect(() => {
    function handleToast(e: Event) {
      const detail = (e as CustomEvent<AchievementToastDetail>).detail;
      const id = nextId++;
      setToasts((prev) => [...prev, { id, ...detail }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, DISPLAY_MS);
    }
    window.addEventListener(ACHIEVEMENT_TOAST_EVENT, handleToast);
    return () => window.removeEventListener(ACHIEVEMENT_TOAST_EVENT, handleToast);
  }, []);

  return (
    <div
      className="fixed top-20 left-1/2 -translate-x-1/2 z-[70] flex flex-col items-center gap-2 pointer-events-none"
      role="alert"
    >
      <AnimatePresence>
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: -16, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="flex items-center gap-3 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 px-5 py-3 text-white shadow-elevated"
          >
            <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-white/20 text-lg" aria-hidden="true">
              {toast.icon || <Award className="h-5 w-5" />}
            </span>
            <div className="text-left">
              <p className="text-xs font-semibold uppercase tracking-wide text-white/80">Achievement Unlocked</p>
              <p className="text-sm font-bold leading-tight">{toast.title}</p>
              {toast.xpReward > 0 && <p className="text-xs text-white/80">+{toast.xpReward} XP</p>}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
