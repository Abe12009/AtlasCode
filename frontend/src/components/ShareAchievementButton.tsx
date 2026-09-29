import { useState } from 'react';
import { Loader2, Share2 } from 'lucide-react';
import { Dropdown, DropdownItem } from './ui/Dropdown';
import { cn } from '../lib/utils';
import { shareOrDownloadCard, type ShareCardData, type ShareFormat } from '../lib/shareCard';

export interface ShareAchievementButtonProps {
  achievement: ShareCardData;
  className?: string;
}

/**
 * Share control for an unlocked achievement.
 *
 * Only ever rendered for the achievement's own owner: Profile and the Dashboard
 * pass it, PublicProfile does not, so the button cannot appear on someone
 * else's achievement. The card it produces carries nothing the owner is not
 * already looking at -- the badge, its title, and their own username.
 *
 * Offers both formats rather than guessing: a square reads as a feed post and
 * a 9:16 as a story, and one image cannot be both without letterboxing.
 */
export function ShareAchievementButton({ achievement, className }: ShareAchievementButtonProps) {
  const [busy, setBusy] = useState<ShareFormat | null>(null);

  const run = async (format: ShareFormat) => {
    setBusy(format);
    try {
      await shareOrDownloadCard(achievement, format);
    } catch (error) {
      // Nothing is half-done if this throws -- the card is built in memory and
      // only ever leaves the page through the share sheet or a download.
      console.error('Share achievement failed', error);
    } finally {
      setBusy(null);
    }
  };

  return (
    <Dropdown position="bottom" align="end">
      <button
        type="button"
        aria-label={`Share ${achievement.title}`}
        disabled={busy !== null}
        className={cn(
          'inline-flex h-8 w-8 items-center justify-center rounded-lg',
          'text-text-tertiary transition-colors duration-fast',
          'hover:bg-bg-tertiary hover:text-text-primary',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus',
          'disabled:cursor-not-allowed disabled:opacity-60',
          className,
        )}
      >
        {busy ? (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        ) : (
          <Share2 className="h-4 w-4" aria-hidden="true" />
        )}
      </button>
      <div className="w-52 py-1">
        <DropdownItem onClick={() => void run('post')}>
          <span className="flex w-full items-center justify-between gap-3">
            <span>Share as post</span>
            <span className="text-xs text-text-tertiary">1:1</span>
          </span>
        </DropdownItem>
        <DropdownItem onClick={() => void run('story')}>
          <span className="flex w-full items-center justify-between gap-3">
            <span>Share as story</span>
            <span className="text-xs text-text-tertiary">9:16</span>
          </span>
        </DropdownItem>
      </div>
    </Dropdown>
  );
}
