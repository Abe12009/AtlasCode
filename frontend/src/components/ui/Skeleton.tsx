import { cn } from '../../lib/utils';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
  animation = 'wave',
  ...props
}: SkeletonProps) {
  const baseStyles = 'bg-bg-tertiary rounded overflow-hidden';
  
  const variantStyles = {
    text: 'h-4 rounded-md',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  const animationStyles = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };

  return (
    <div
      className={cn(
        baseStyles,
        variantStyles[variant],
        animationStyles[animation],
        className,
      )}
      style={{
        width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
        height: height ? (typeof height === 'number' ? `${height}px` : height) : undefined,
      }}
      {...props}
    />
  );
}

export function SkeletonText({ lines = 3, className, ...props }: { lines?: number; className?: string } & Omit<SkeletonProps, 'variant'>) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          width={i === lines - 1 ? '60%' : '100%'}
          {...props}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className, ...props }: { className?: string } & Omit<SkeletonProps, 'variant'>) {
  return (
    <div className={cn('space-y-4 p-6 bg-bg-elevated border border-border-primary rounded-2xl', className)}>
      <div className="flex items-center gap-4">
        <Skeleton variant="circular" width={40} height={40} />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" width="40%" height={24} />
          <Skeleton variant="text" width="30%" height={16} />
        </div>
      </div>
      <Divider />
      <SkeletonText lines={3} />
    </div>
  );
}

import { Divider } from './Feedback';