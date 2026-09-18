import { cn } from '../lib/utils';
import { CheckCircle, BookOpen, FolderKanban, Code, Trophy, Target, Clock, ChevronRight, Lock } from 'lucide-react';
import { StatusBadge, XPBadge } from './ui/StatusBadge';
import { useTranslation } from '../hooks/useTranslation';

export interface QuestNodeData {
  id: string | number;
  title: string;
  description?: string;
  type: 'lesson' | 'project' | 'visual' | 'checkpoint';
  status: 'completed' | 'current' | 'available' | 'locked';
  estimatedMinutes?: number;
  xpReward?: number;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  path?: string;
  icon?: React.ReactNode;
}

interface QuestNodeProps {
  node: QuestNodeData;
  index: number;
  total: number;
  isFirst?: boolean;
  isLast?: boolean;
  onClick?: () => void;
  showConnectors?: boolean;
  variant?: 'horizontal' | 'vertical';
  className?: string;
}

const typeIcons = {
  lesson: BookOpen,
  project: FolderKanban,
  visual: Code,
  checkpoint: Trophy,
};

const difficultyColors = {
  beginner: 'text-green-400 bg-green-900/30 border-green-500/30',
  intermediate: 'text-yellow-400 bg-yellow-900/30 border-yellow-500/30',
  advanced: 'text-red-400 bg-red-900/30 border-red-500/30',
};

export function QuestNode({
  node,
  index,
  total,
  isFirst = false,
  isLast = false,
  onClick,
  showConnectors = true,
  variant = 'horizontal',
  className,
}: QuestNodeProps) {
  const { t, isRTL } = useTranslation();
  const TypeIcon = typeIcons[node.type] || BookOpen;

  const isCurrent = node.status === 'current';
  const isCompleted = node.status === 'completed';
  const isLocked = node.status === 'locked';
  // 'available' (not yet started, not blocked by a prerequisite) is real
  // information distinct from 'locked' -- keep its own quiet styling rather
  // than folding it into either state. See app.services dashboard proposal.
  const isAvailable = node.status === 'available';

  const baseNodeSize = variant === 'horizontal' ? 56 : 48;
  // The current node reads as "you are here": larger than its neighbors,
  // per the target wireframe.
  const nodeSize = isCurrent ? baseNodeSize + 12 : baseNodeSize;
  const connectorWidth = variant === 'horizontal' ? 'calc(100% - 56px)' : '4px';
  const connectorHeight = variant === 'horizontal' ? '4px' : 'calc(100% - 48px)';

  return (
    <div className={cn('relative flex flex-col items-center', variant === 'horizontal' ? 'flex-1' : 'w-full', className)}>
      <div
        className={cn(
          'relative flex flex-col items-center transition-all duration-300',
          'group',
          onClick && 'cursor-pointer',
          isCurrent && 'animate-pulse-glow',
          isCompleted && 'opacity-100',
          isLocked && 'opacity-50'
        )}
        onClick={onClick}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
        onKeyDown={(e) => { if (onClick && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); onClick(); } }}
        aria-label={`${node.title}, ${t(`lessons.${node.status}`)}`}
      >
        <div
          className={cn(
            'relative flex items-center justify-center rounded-full border-2 transition-all duration-300',
            'z-10',
            isCompleted
              ? 'bg-primary-500 border-primary-500 text-white shadow-glow-primary'
              : isCurrent
              ? 'bg-accent-500 border-accent-500 text-white shadow-glow-accent animate-pulse-glow ring-4 ring-accent-500/30'
              : isLocked
              ? 'border-dashed bg-bg-tertiary border-border-secondary text-text-tertiary'
              : 'bg-bg-secondary border-border-secondary text-text-secondary hover:border-primary-500/50 hover:bg-bg-tertiary'
          )}
          style={{ width: nodeSize, height: nodeSize }}
        >
          {isCompleted ? (
            <CheckCircle className="h-6 w-6" aria-hidden="true" />
          ) : isCurrent ? (
            <span className="font-bold text-lg" aria-hidden="true">{index + 1}</span>
          ) : isLocked ? (
            <Lock className="h-5 w-5" aria-hidden="true" />
          ) : (
            <TypeIcon className={cn('h-7 w-7', isAvailable ? 'text-text-secondary' : 'text-text-tertiary')} aria-hidden="true" />
          )}
        </div>

        <div className="mt-3 w-full px-2 text-center">
          <h4 className={cn(
            'font-medium truncate transition-colors',
            isCurrent ? 'text-text-primary' : isCompleted ? 'text-text-secondary' : isLocked ? 'text-text-tertiary' : 'text-text-secondary'
          )}>
            {node.title}
          </h4>
          <div className="flex items-center justify-center gap-2 mt-1.5 flex-wrap">
            {node.estimatedMinutes && (
              <span className={cn(
                'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs',
                'bg-bg-tertiary text-text-tertiary border border-border-primary'
              )}>
                <Clock className="h-3 w-3" aria-hidden="true" />
                <span>{node.estimatedMinutes} {t('common.min')}</span>
              </span>
            )}
            {node.xpReward && (
              <XPBadge xp={node.xpReward} size="sm" showIcon={false} />
            )}
            {node.difficulty && (
              <span className={cn(
                'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border',
                difficultyColors[node.difficulty]
              )}>
                <Target className="h-3 w-3" aria-hidden="true" />
                <span>{t(`courses.difficulty_level.${node.difficulty}`)}</span>
              </span>
            )}
          </div>
          {node.description && (
            <p className="mt-2 text-xs text-text-tertiary line-clamp-2">{node.description}</p>
          )}
        </div>
      </div>

      {showConnectors && !isLast && (
        <div
          className={cn(
            'absolute transition-colors duration-300',
            variant === 'horizontal'
              ? 'left-1/2 w-[calc(100%-56px)] h-0.5 -translate-x-1/2'
              : 'left-[calc(50%-2px)] w-0.5 h-[calc(100%-48px-16px)] -translate-x-1/2'
          )}
          style={{
            // Offset from this node's own (possibly enlarged, for 'current')
            // circle rather than a size hardcoded for the common case --
            // the current node is bigger, so its outgoing connector needs
            // to start further down/right or it clips into the circle.
            top: variant === 'horizontal' ? nodeSize + 8 : baseNodeSize + 8,
            background: isCompleted
              ? 'linear-gradient(90deg, var(--color-primary-500), var(--color-primary-500))'
              : 'linear-gradient(90deg, var(--color-border-primary), var(--color-border-primary))',
          }}
          aria-hidden="true"
        />
      )}
    </div>
  );
}

export interface QuestRoadmapProps {
  nodes: QuestNodeData[];
  variant?: 'horizontal' | 'vertical';
  className?: string;
}

export function QuestRoadmap({ nodes, variant = 'horizontal', className }: QuestRoadmapProps) {
  return (
    <div
      className={cn(
        'relative',
        variant === 'horizontal' ? 'flex items-start gap-0 overflow-x-auto pb-4 scrollbar-thin' : 'flex flex-col items-center gap-0',
        className
      )}
      role="list"
      aria-label="Learning roadmap"
    >
      {nodes.map((node, index) => (
        <QuestNode
          key={node.id}
          node={node}
          index={index}
          total={nodes.length}
          isFirst={index === 0}
          isLast={index === nodes.length - 1}
          variant={variant}
        />
      ))}
    </div>
  );
}