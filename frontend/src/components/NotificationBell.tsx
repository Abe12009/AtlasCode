import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { fr as frLocale, arSA as arLocale } from 'date-fns/locale';
import { Bell, CheckCheck, Inbox, AlertTriangle, CheckCircle, Trophy, Sparkles, Zap } from 'lucide-react';
import { notificationsApi } from '../api/services';
import { Button, Dropdown, DropdownItem, Skeleton, cn } from './ui';
import { useTranslation } from '../hooks/useTranslation';
import type { Notification, NotificationType } from '../types';

const DATE_LOCALES = { en: undefined, fr: frLocale, ar: arLocale };

const TYPE_ICON: Record<NotificationType, typeof CheckCircle> = {
  welcome: Sparkles,
  xp_earned: Zap,
  lesson_completed: CheckCircle,
  project_completed: Trophy,
};

function notificationMessage(t: (key: string, opts?: Record<string, unknown>) => string, notification: Notification): string {
  switch (notification.type) {
    case 'xp_earned':
      return t('notifications.events.xp_earned', { xp: notification.data.xp ?? 0 });
    case 'lesson_completed':
      return t('notifications.events.lesson_completed');
    case 'project_completed':
      return t('notifications.events.project_completed', { xp: notification.data.xp ?? 0 });
    case 'welcome':
    default:
      return t('notifications.events.welcome');
  }
}

export function NotificationBell() {
  const { t, currentLanguage } = useTranslation();
  const queryClient = useQueryClient();

  const unreadCountQuery = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: notificationsApi.getUnreadCount,
    refetchInterval: 30000,
  });

  const notificationsQuery = useQuery({
    queryKey: ['notifications', 'list'],
    queryFn: () => notificationsApi.list(20),
    refetchInterval: 30000,
  });

  const markReadMutation = useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const unreadCount = unreadCountQuery.data?.count ?? 0;
  const notifications = notificationsQuery.data ?? [];

  return (
    <div className="relative">
      <Dropdown position="bottom" align="end">
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<Bell className="h-4 w-4" />}
          aria-label={t('common.notifications')}
          className="relative"
        >
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 h-4 min-w-4 px-0.5 rounded-full bg-error-500 text-xs text-white flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </Button>
        <div className="w-80 max-w-[calc(100vw-2rem)] py-2">
          <div className="px-3 py-2 flex items-center justify-between border-b border-border-primary">
            <span className="text-sm font-semibold text-text-primary">{t('common.notifications')}</span>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={() => markAllReadMutation.mutate()}
                disabled={markAllReadMutation.isPending}
                className="flex items-center gap-1 text-xs font-medium text-primary-400 hover:text-primary-300 disabled:opacity-50"
              >
                <CheckCheck className="h-3.5 w-3.5" aria-hidden="true" />
                {t('notifications.mark_all_read')}
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto">
            {notificationsQuery.isLoading && (
              <div className="p-3 space-y-3">
                <Skeleton variant="text" width="90%" height={14} />
                <Skeleton variant="text" width="70%" height={14} />
                <Skeleton variant="text" width="80%" height={14} />
              </div>
            )}

            {notificationsQuery.isError && (
              <div className="p-6 flex flex-col items-center text-center gap-2">
                <AlertTriangle className="h-6 w-6 text-error-500" aria-hidden="true" />
                <p className="text-sm text-text-secondary">{t('notifications.load_error')}</p>
              </div>
            )}

            {!notificationsQuery.isLoading && !notificationsQuery.isError && notifications.length === 0 && (
              <div className="p-6 flex flex-col items-center text-center gap-2">
                <Inbox className="h-6 w-6 text-text-tertiary" aria-hidden="true" />
                <p className="text-sm text-text-secondary">{t('notifications.empty')}</p>
              </div>
            )}

            {notifications.map((notification) => {
              const Icon = TYPE_ICON[notification.type] ?? Bell;
              return (
                <DropdownItem
                  key={notification.id}
                  icon={<Icon className={cn('h-4 w-4', notification.is_read ? 'text-text-tertiary' : 'text-primary-400')} />}
                  className={cn(!notification.is_read && 'bg-primary-500/5')}
                  onClick={() => {
                    if (!notification.is_read) markReadMutation.mutate(notification.id);
                  }}
                >
                  <div className="flex items-start gap-2">
                    {!notification.is_read && (
                      <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary-500 flex-shrink-0" aria-hidden="true" />
                    )}
                    <div className="flex flex-col gap-1 min-w-0">
                      <span className={cn('font-medium', notification.is_read ? 'text-text-secondary' : 'text-text-primary')}>
                        {notificationMessage(t, notification)}
                      </span>
                      <span className="text-xs text-text-tertiary">
                        {formatDistanceToNow(new Date(notification.created_at), {
                          addSuffix: true,
                          locale: DATE_LOCALES[currentLanguage as keyof typeof DATE_LOCALES],
                        })}
                      </span>
                    </div>
                  </div>
                </DropdownItem>
              );
            })}
          </div>
        </div>
      </Dropdown>
    </div>
  );
}
