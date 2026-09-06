import { Avatar } from './ui';
import { AvatarFace } from './AvatarFace';
import { parseAvatarConfig } from '../lib/avatar';
import { cn } from '../lib/utils';

export interface ProfileAvatarSource {
  username?: string | null;
  avatar_type?: string | null;
  avatar_config?: string | null;
  avatar_image_data?: string | null;
  avatar_url?: string | null;
}

const SIZE_CLASSES = {
  xs: 'h-5 w-5',
  sm: 'h-8 w-8',
  md: 'h-10 w-10',
  lg: 'h-12 w-12',
  xl: 'h-16 w-16',
  '2xl': 'h-20 w-20',
} as const;

/**
 * Renders whichever profile picture is active: the built cartoon avatar
 * (generated), an uploaded/provider photo (upload), or falls back to
 * initials — the single place every surface (nav, profile, public profile)
 * should read from so they never disagree on which picture is "active".
 */
export function ProfileAvatar({
  user,
  size = 'md',
  className,
}: {
  user: ProfileAvatarSource | undefined | null;
  size?: keyof typeof SIZE_CLASSES;
  className?: string;
}) {
  if (user?.avatar_type === 'generated' && user.avatar_config) {
    return (
      <div className={cn('overflow-hidden rounded-full bg-bg-secondary flex-shrink-0', SIZE_CLASSES[size], className)}>
        <AvatarFace config={parseAvatarConfig(user.avatar_config)} className="h-full w-full" />
      </div>
    );
  }

  const photo = user?.avatar_image_data || user?.avatar_url || undefined;
  return (
    <Avatar name={user?.username || ''} src={photo} size={size} className={className} />
  );
}
