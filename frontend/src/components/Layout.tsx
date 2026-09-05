import { useState, useEffect, useRef } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { LayoutDashboard, BookOpen, FolderKanban, User, LogOut, Menu, X, ChevronDown, Trophy, Code, Globe, Zap, Star } from 'lucide-react';
import { Button, Avatar, Dropdown, DropdownItem, DropdownSeparator, Badge, cn } from './ui';
import { StatusBadge, XPBadge, StreakBadge } from './ui/StatusBadge';
import { NotificationBell } from './NotificationBell';

export function Layout() {
  const { user, profile, logout, loading: authLoading } = useAuth();
  const { t, currentLanguage, changeLanguage, languages, isRTL } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const headerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 8);
    }
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const currentXP = profile?.xp || 0;
  const currentLevel = profile?.level || 1;
  const xpForNextLevel = 100;
  const xpProgress = (currentXP % xpForNextLevel) / xpForNextLevel * 100;

  const navItems = [
    { path: '/app/dashboard', label: t('navigation.dashboard'), icon: LayoutDashboard },
    { path: '/app/courses', label: t('navigation.courses'), icon: BookOpen },
    { path: '/app/projects', label: t('navigation.projects'), icon: FolderKanban },
    { path: '/app/profile', label: t('navigation.profile'), icon: User },
  ];

  const userDropdownItems = [
    { label: t('navigation.profile'), icon: User, path: '/app/profile' },
    { label: t('navigation.achievements'), icon: Trophy, path: '/app/profile?tab=achievements' },
    { label: t('navigation.settings'), icon: Code, path: '/app/profile?tab=settings' },
  ];

  if (authLoading) {
    return (
      <div className="min-h-screen bg-bg-primary flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className={cn('min-h-screen bg-bg-primary flex flex-col', isRTL ? 'rtl' : 'ltr')}>
      <a href="#main-content" className="skip-link">
        {t('accessibility.skip_to_main')}
      </a>
      <header
        ref={headerRef}
        className={cn(
          'fixed top-0 left-0 right-0 z-50 bg-bg-primary/90 backdrop-blur-xl border-b border-border-primary/50',
          'transition-all duration-normal',
          scrolled && 'shadow-elevated bg-bg-primary/95'
        )}
        role="banner"
      >
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-6">
              <NavLink
                to="/app/dashboard"
                className="flex items-center gap-2"
                aria-label={t('common.home')}
              >
                <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
                  <Code className="h-5 w-5 text-white" aria-hidden="true" />
                  <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-accent-500" aria-hidden="true" />
                </div>
                <span className="text-xl font-bold text-text-primary bg-gradient-to-r from-text-primary via-primary-400 to-accent-400 bg-clip-text text-transparent">
                  AtlasCode
                </span>
              </NavLink>

              <nav className="hidden lg:flex items-center gap-1" aria-label={t('navigation.main')}>
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path || (item.path !== '/app/dashboard' && location.pathname.startsWith(item.path));
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={({ isActive: active }) =>
                        cn(
                          'flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-fast',
                          active
                            ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                            : 'text-text-secondary hover:text-text-primary hover:bg-bg-secondary'
                        )
                      }
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </nav>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-bg-secondary rounded-xl border border-border-primary">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-mono text-text-tertiary">Lvl.</span>
                  <span className="font-bold text-text-primary tabular-nums">{currentLevel}</span>
                </div>
                <div className="w-24 h-1.5 bg-bg-tertiary rounded-full overflow-hidden ml-2">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all duration-500"
                    style={{ width: `${xpProgress}%` }}
                  />
                </div>
                <XPBadge xp={currentXP} size="sm" />
              </div>

              <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-bg-secondary rounded-xl border border-border-primary">
                <StreakBadge streak={profile?.streak || 0} size="sm" showIcon />
              </div>

              <div className="relative hidden sm:block">
                <Dropdown position="bottom" align="end">
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<Globe className="h-4 w-4" />}
                    onClick={() => setLangMenuOpen(!langMenuOpen)}
                    aria-label={t('common.language')}
                    className="gap-1.5"
                  >
                    <span className="hidden sm:inline text-sm font-medium text-text-secondary">
                      {languages.find(l => l.code === currentLanguage)?.nativeName || currentLanguage}
                    </span>
                    <ChevronDown className={cn('h-4 w-4 text-text-tertiary transition-transform', langMenuOpen && 'rotate-180')} />
                  </Button>
                  {languages.map((lang) => (
                    <DropdownItem
                      key={lang.code}
                      onClick={() => {
                        changeLanguage(lang.code);
                        setLangMenuOpen(false);
                      }}
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{lang.code === 'ar' ? '🇸🇦' : lang.code === 'fr' ? '🇫🇷' : '🇺🇸'}</span>
                        <span>{lang.nativeName}</span>
                        {currentLanguage === lang.code && (
                          <span className="h-4 w-4 text-accent-500 flex-shrink-0" aria-hidden="true">✓</span>
                        )}
                      </div>
                    </DropdownItem>
                  ))}
                </Dropdown>
              </div>

              <NotificationBell />

              <div className="relative">
                <Dropdown position="bottom" align="end">
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<Avatar name={user?.username || ''} size="xs" />}
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    aria-label={t('common.profile')}
                    className="gap-2"
                  >
                    <span className="hidden sm:inline text-sm font-medium text-text-secondary">
                      {user?.username}
                    </span>
                    <ChevronDown className={cn('h-4 w-4 text-text-tertiary transition-transform', userMenuOpen && 'rotate-180')} />
                  </Button>
                  <div className="w-56 py-1">
                    <div className="px-3 py-2 border-b border-border-primary">
                      <p className="text-sm font-medium text-text-primary">{user?.username}</p>
                      <p className="text-xs text-text-tertiary truncate">{user?.email}</p>
                    </div>
                    {userDropdownItems.map((item) => (
                      <DropdownItem
                        key={item.path}
                        icon={<item.icon className="h-4 w-4" />}
                        onClick={() => {
                          navigate(item.path);
                          setUserMenuOpen(false);
                        }}
                      >
                        {item.label}
                      </DropdownItem>
                    ))}
                    <DropdownSeparator />
                    <DropdownItem
                      icon={<LogOut className="h-4 w-4" />}
                      destructive
                      onClick={handleLogout}
                    >
                      {t('common.logout')}
                    </DropdownItem>
                  </div>
                </Dropdown>
              </div>

              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label={mobileMenuOpen ? t('accessibility.close_menu') : t('accessibility.open_menu')}
                aria-expanded={mobileMenuOpen}
                aria-controls="mobile-menu"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </Button>
            </div>
          </div>
        </div>

        {mobileMenuOpen && (
          <div id="mobile-menu" className="lg:hidden py-4 border-t border-border-primary animate-slide-down" role="navigation" aria-label={t('navigation.main')}>
            <nav className="flex flex-col gap-1 px-4">
              {navItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-3 rounded-xl text-base font-medium',
                      isActive
                        ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                        : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
                    )
                  }
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                  <span>{item.label}</span>
                </NavLink>
              ))}
              <div className="pt-4 border-t border-border-primary">
                <Button
                  variant="ghost"
                  fullWidth
                  leftIcon={<LogOut className="h-5 w-5" />}
                  onClick={handleLogout}
                  className="justify-start text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20"
                >
                  {t('common.logout')}
                </Button>
              </div>
            </nav>
          </div>
        )}
      </header>

      <main
        className="flex-1 pt-20 pb-8 max-w-full w-full mx-auto px-4 sm:px-6 lg:px-8"
        id="main-content"
        role="main"
      >
        <Outlet />
      </main>

      <footer className="bg-bg-secondary border-t border-border-primary py-6 mt-auto">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-text-tertiary text-center md:text-left">
              {t('footer.copyright', { year: new Date().getFullYear() })}
            </p>
            <div className="flex items-center gap-6 text-sm">
              <a href="#" className="text-text-tertiary hover:text-text-primary transition-colors">
                {t('footer.privacy_policy')}
              </a>
              <a href="#" className="text-text-tertiary hover:text-text-primary transition-colors">
                {t('footer.terms_of_service')}
              </a>
              <a href="#" className="text-text-tertiary hover:text-text-primary transition-colors">
                {t('footer.contact')}
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}