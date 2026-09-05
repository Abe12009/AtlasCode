import { cn } from '../../lib/utils';
import { CheckCircle, Lock, Clock, AlertCircle } from 'lucide-react';

export type Status = 'completed' | 'current' | 'available' | 'locked' | 'in_progress' | 'pending';

export interface StatusBadgeProps {
  status: Status;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

const statusStyles = {
  completed: 'bg-success-900/30 text-success-400 border-success-500/30',
  current: 'bg-primary-900/30 text-primary-400 border-primary-500/30 animate-pulse-glow',
  available: 'bg-blue-900/30 text-blue-400 border-blue-500/30',
  locked: 'bg-bg-tertiary text-text-tertiary border-border-primary',
  in_progress: 'bg-accent-900/30 text-accent-400 border-accent-500/30',
  pending: 'bg-warning-900/30 text-warning-400 border-warning-500/30',
};

const statusIcons = {
  completed: CheckCircle,
  current: AlertCircle,
  available: Clock,
  locked: Lock,
  in_progress: AlertCircle,
  pending: Clock,
};

const sizeStyles = {
  sm: 'px-2 py-0.5 text-xs gap-1',
  md: 'px-3 py-1 text-sm gap-1.5',
  lg: 'px-4 py-1.5 text-base gap-2',
};

const statusLabels: Record<Status, string> = {
  completed: 'Completed',
  current: 'Current',
  available: 'Available',
  locked: 'Locked',
  in_progress: 'In Progress',
  pending: 'Pending',
};

export function StatusBadge({
  status,
  size = 'md',
  showIcon = true,
  className,
  ...props
}: StatusBadgeProps) {
  const Icon = statusIcons[status];

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium border',
        'rounded-full transition-all duration-fast',
        statusStyles[status],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {showIcon && <Icon className={cn('flex-shrink-0', size === 'sm' && 'h-3 w-3', size === 'md' && 'h-4 w-4', size === 'lg' && 'h-5 w-5')} aria-hidden="true" />}
      <span>{statusLabels[status]}</span>
    </span>
  );
}

export interface XPBadgeProps {
  xp: number;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

export function XPBadge({ xp, size = 'md', showIcon = true, className }: XPBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center font-semibold text-accent-400',
        'bg-accent-900/30 border border-accent-500/30',
        'rounded-full transition-all duration-fast',
        size === 'sm' && 'px-2 py-0.5 text-xs gap-1',
        size === 'md' && 'px-3 py-1 text-sm gap-1.5',
        size === 'lg' && 'px-4 py-1.5 text-base gap-2',
        className
      )}
    >
      {showIcon && <span className="flex-shrink-0" aria-hidden="true">⚡</span>}
      <span>{xp.toLocaleString()} XP</span>
    </span>
  );
}

export interface StreakBadgeProps {
  streak: number;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  className?: string;
}

export function StreakBadge({ streak, size = 'md', showIcon = true, className }: StreakBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center font-semibold text-orange-400',
        'bg-orange-900/30 border border-orange-500/30',
        'rounded-full transition-all duration-fast',
        size === 'sm' && 'px-2 py-0.5 text-xs gap-1',
        size === 'md' && 'px-3 py-1 text-sm gap-1.5',
        size === 'lg' && 'px-4 py-1.5 text-base gap-2',
        className
      )}
    >
      {showIcon && <span className="flex-shrink-0" aria-hidden="true">🔥</span>}
      <span>{streak} Day{streak !== 1 ? 's' : ''}</span>
    </span>
  );
}

export interface AchievementBadgeProps {
  icon: string;
  title: string;
  description?: string;
  xpReward?: number;
  earned?: boolean;
  earnedAt?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function AchievementBadge({
  icon,
  title,
  description,
  xpReward,
  earned = false,
  earnedAt,
  size = 'md',
  className,
}: AchievementBadgeProps) {
  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-2xl border transition-all duration-normal',
        earned
          ? 'bg-yellow-500/10 border-yellow-500/30'
          : 'bg-bg-secondary border-border-primary opacity-60',
        size === 'sm' && 'p-3 gap-2',
        size === 'lg' && 'p-5 gap-4',
        className
      )}
    >
      <div
        className={cn(
          'flex-shrink-0 rounded-xl flex items-center justify-center',
          'bg-yellow-500/20 text-yellow-400',
          size === 'sm' && 'w-10 h-10 text-xl',
          size === 'md' && 'w-12 h-12 text-2xl',
          size === 'lg' && 'w-16 h-16 text-3xl'
        )}
        aria-hidden="true"
      >
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <h4 className={cn(
          'font-semibold truncate',
          earned ? 'text-text-primary' : 'text-text-tertiary'
        )}>
          {title}
        </h4>
        {description && (
          <p className={cn(
            'text-sm mt-1 truncate',
            earned ? 'text-text-secondary' : 'text-text-quaternary'
          )}>
            {description}
          </p>
        )}
        {(xpReward || earnedAt) && (
          <div className="flex items-center gap-3 mt-2">
            {xpReward && (
              <span className={cn(
                'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                earned ? 'bg-accent-900/30 text-accent-400 border border-accent-500/30' : 'bg-bg-tertiary text-text-quaternary'
              )}>
                ⚡ +{xpReward} XP
              </span>
            )}
            {earnedAt && earned && (
              <span className="text-xs text-text-tertiary">
                Earned {earnedAt}
              </span>
            )}
          </div>
        )}
      </div>
      {earned && (
        <CheckCircle className="flex-shrink-0 h-5 w-5 text-success-500 mt-0.5" aria-hidden="true" />
      )}
    </div>
  );
}