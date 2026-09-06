import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Code, ArrowRight, BookOpen, FolderKanban, Trophy, Zap, Shield, Globe, Check, Layers, Brain, Menu, X as CloseIcon } from 'lucide-react';
import { Button, Card, Badge, cn } from '../components/ui';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import { GithubIcon, InstagramIcon, XIcon } from '../components/icons/BrandIcons';
import { useTranslation } from '../hooks/useTranslation';
import { SOCIAL_LINKS } from '../config/site';

const SECTION_IDS = ['features', 'roadmap', 'stats'] as const;

export function Landing() {
  const { t, isRTL } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<string>('');

  useEffect(() => {
    const sections = SECTION_IDS.map((id) => document.getElementById(id)).filter(
      (el): el is HTMLElement => el !== null,
    );
    if (sections.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) {
          setActiveSection(visible[0].target.id);
        }
      },
      { rootMargin: '-45% 0px -45% 0px', threshold: [0, 0.25, 0.5, 0.75, 1] },
    );
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  const scrollToSection = (event: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    event.preventDefault();
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setActiveSection(id);
    setMobileMenuOpen(false);
    window.history.replaceState(null, '', `#${id}`);
  };

  const features = [
    {
      icon: Brain,
      title: t('landing.features.learn.title'),
      description: t('landing.features.learn.description'),
      accent: 'primary',
    },
    {
      icon: Layers,
      title: t('landing.features.projects.title'),
      description: t('landing.features.projects.description'),
      accent: 'accent',
    },
    {
      icon: Trophy,
      title: t('landing.features.achievements.title'),
      description: t('landing.features.achievements.description'),
      accent: 'warning',
    },
    {
      icon: Zap,
      title: t('landing.features.visual.title'),
      description: t('landing.features.visual.description'),
      accent: 'success',
    },
    {
      icon: Shield,
      title: t('landing.features.safe.title'),
      description: t('landing.features.safe.description'),
      accent: 'primary',
    },
    {
      icon: Globe,
      title: t('landing.features.i18n.title'),
      description: t('landing.features.i18n.description'),
      accent: 'accent',
    },
  ];

  const stats = [
    { value: t('landing.stats.courses'), label: t('landing.stats.courses_label'), icon: BookOpen },
    { value: t('landing.stats.lessons'), label: t('landing.stats.lessons_label'), icon: Layers },
    { value: t('landing.stats.projects'), label: t('landing.stats.projects_label'), icon: FolderKanban },
    { value: t('landing.stats.languages'), label: t('landing.stats.languages_label'), icon: Globe },
  ];

  const roadmapPreview = [
    { id: 1, title: 'Variables & Types', type: 'lesson' as const, status: 'completed' as const, estimatedMinutes: 30, xpReward: 50 },
    { id: 2, title: 'Control Flow', type: 'lesson' as const, status: 'completed' as const, estimatedMinutes: 45, xpReward: 75 },
    { id: 3, title: 'Functions', type: 'lesson' as const, status: 'current' as const, estimatedMinutes: 40, xpReward: 100 },
    { id: 4, title: 'Data Structures', type: 'lesson' as const, status: 'available' as const, estimatedMinutes: 60, xpReward: 150 },
    { id: 5, title: 'Build a CLI Tool', type: 'project' as const, status: 'locked' as const, estimatedMinutes: 120, xpReward: 300 },
  ];

  return (
    <div className={cn('min-h-screen bg-bg-primary', isRTL ? 'rtl' : 'ltr')}>
      <header className="fixed top-0 left-0 right-0 z-50 bg-bg-primary/90 backdrop-blur-xl border-b border-border-primary/50">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/app/dashboard" className="flex items-center gap-2" aria-label={t('common.home')}>
              <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
                <Code className="h-5 w-5 text-white" aria-hidden="true" />
                <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-accent-500" aria-hidden="true" />
              </div>
              <span className="text-xl font-bold text-gradient-brand">
                AtlasCode
              </span>
            </Link>

            <nav className="hidden lg:flex items-center gap-6" aria-label={t('navigation.main')}>
              {SECTION_IDS.map((id) => (
                <a
                  key={id}
                  href={`#${id}`}
                  onClick={(e) => scrollToSection(e, id)}
                  aria-current={activeSection === id ? 'page' : undefined}
                  className={cn(
                    'relative text-sm font-medium transition-colors py-1',
                    'after:absolute after:left-0 after:-bottom-1 after:h-0.5 after:rounded-full after:transition-all after:duration-fast',
                    activeSection === id
                      ? 'text-text-primary after:w-full after:bg-accent-500'
                      : 'text-text-secondary after:w-0 hover:text-text-primary hover:after:w-full hover:after:bg-border-secondary',
                  )}
                >
                  {t(`landing.nav.${id}`)}
                </a>
              ))}
            </nav>

            <div className="flex items-center gap-2 sm:gap-4">
              <LanguageSwitcher className="hidden sm:inline-flex" />

              <div className="hidden sm:flex items-center gap-2">
                <Link to="/login" className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors rounded-xl">
                  {t('auth.sign_in')}
                </Link>
                <Link to="/register" className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 active:scale-[0.97] transition-all rounded-xl shadow-lg hover:shadow-glow-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-500 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary">
                  {t('auth.sign_up')}
                </Link>
              </div>

              <button
                type="button"
                onClick={() => setMobileMenuOpen((open) => !open)}
                aria-expanded={mobileMenuOpen}
                aria-controls="landing-mobile-menu"
                aria-label={mobileMenuOpen ? t('common.close') : t('navigation.main')}
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-text-secondary transition-colors hover:bg-bg-tertiary hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus lg:hidden"
              >
                {mobileMenuOpen ? <CloseIcon className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>

        {mobileMenuOpen && (
          <div
            id="landing-mobile-menu"
            className="border-t border-border-primary/50 bg-bg-primary/95 backdrop-blur-xl lg:hidden animate-fade-in"
          >
            <nav className="flex flex-col gap-1 px-4 py-4" aria-label={t('navigation.main')}>
              {SECTION_IDS.map((id) => (
                <a
                  key={id}
                  href={`#${id}`}
                  onClick={(e) => scrollToSection(e, id)}
                  aria-current={activeSection === id ? 'page' : undefined}
                  className={cn(
                    'rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                    activeSection === id
                      ? 'bg-primary-500/10 text-primary-400'
                      : 'text-text-secondary hover:bg-bg-tertiary hover:text-text-primary',
                  )}
                >
                  {t(`landing.nav.${id}`)}
                </a>
              ))}
            </nav>
            <div className="flex items-center justify-between gap-3 border-t border-border-primary/50 px-4 py-4">
              <LanguageSwitcher align="start" />
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium text-text-secondary transition-colors hover:text-text-primary"
                >
                  {t('auth.sign_in')}
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-accent-500 to-accent-600 px-4 py-2 text-sm font-semibold text-white shadow-lg transition-all hover:from-accent-600 hover:to-accent-700"
                >
                  {t('auth.sign_up')}
                </Link>
              </div>
            </div>
          </div>
        )}
      </header>

      <main>
        <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
          <div className="absolute inset-0 bg-mesh-gradient z-0" aria-hidden="true" />
          <div className="absolute inset-0 bg-grid-pattern z-0" aria-hidden="true" />
          <div className="absolute inset-0 overflow-hidden pointer-events-none z-0" aria-hidden="true">
            <div className="absolute top-20 left-10 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '0s' }} />
            <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1.5s' }} />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-primary-500/5 via-transparent to-accent-500/5 rounded-full blur-3xl" />
          </div>

          <div className="relative max-w-full mx-auto px-4 sm:px-6 lg:px-8 z-10">
            <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
              <div className="text-center lg:text-left animate-fade-in">
                <Badge variant="outline" size="lg" className="mb-6 border-primary-500/30 bg-primary-500/5 text-primary-400" dot dotColor="primary">
                  {t('landing.badge')}
                </Badge>
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-text-primary leading-tight mb-6">
                  {t('landing.hero.title')}
                  <br />
                  <span className="text-gradient-brand animate-gradient-shift">
                    {t('landing.hero.highlight')}
                  </span>
                </h1>
                <p className="text-lg sm:text-xl text-text-secondary max-w-xl mx-auto lg:mx-0 mb-10 leading-relaxed">
                  {t('landing.hero.description')}
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 mb-12">
                  <Link to="/register" className="w-full sm:w-auto">
                    <Button size="lg" fullWidth leftIcon={<ArrowRight className="h-5 w-5" />} className="bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent">
                      {t('landing.hero.cta_primary')}
                    </Button>
                  </Link>
                  <Link to="/app/courses" className="w-full sm:w-auto">
                    <Button variant="outline" size="lg" fullWidth className="border-primary-500/30 text-primary-400 hover:bg-primary-500/5 hover:border-primary-500/50">
                      {t('landing.hero.cta_secondary')}
                    </Button>
                  </Link>
                </div>
                <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 text-sm text-text-tertiary">
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-success-500 flex-shrink-0" aria-hidden="true" />
                    <span>{t('landing.hero.trust_1')}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-success-500 flex-shrink-0" aria-hidden="true" />
                    <span>{t('landing.hero.trust_2')}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5 text-success-500 flex-shrink-0" aria-hidden="true" />
                    <span>{t('landing.hero.trust_3')}</span>
                  </div>
                </div>
              </div>

              <div className="relative animate-slide-up">
                <div className="relative bg-bg-secondary/50 border border-border-primary/50 rounded-2xl p-1 backdrop-blur-xl">
                  <div className="bg-bg-code/80 rounded-xl overflow-hidden border border-border-primary/50 backdrop-blur-xl">
                    <div className="flex items-center gap-2 px-4 py-3 bg-bg-code-light/80 border-b border-border-primary/50">
                      <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                      </div>
                      <div className="flex-1 text-center text-xs text-text-tertiary font-mono">main.py</div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-1 bg-primary-500/10 text-primary-400 text-xs rounded font-mono">Python</span>
                        <span className="px-2 py-1 bg-accent-500/10 text-accent-400 text-xs rounded font-mono">3.11</span>
                      </div>
                    </div>
                    <pre dir="ltr" className="p-6 overflow-x-auto text-left"><code className="text-sm text-gray-100 font-mono leading-relaxed">{`# Welcome to AtlasCode
def learn_programming():
    skills = ["Python", "JavaScript", "TypeScript"]
    for skill in skills:
        print(f"Mastering {skill}...")
        practice(skill)
    
    return "Ready to build!"

def practice(skill):
    xp = complete_lessons(skill)
    build_projects(skill)
    earn_achievements(xp)

learn_programming()`}</code></pre>
                  </div>
                </div>
                <div className="absolute -bottom-6 -right-6 lg:-bottom-8 lg:-right-8 bg-bg-primary/90 border border-border-primary/50 rounded-xl p-4 shadow-2xl backdrop-blur-xl animate-fade-in" style={{ animationDelay: '200ms' }}>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary-500/10 rounded-lg">
                      <Trophy className="h-6 w-6 text-primary-400" />
                    </div>
                    <div>
                      <p className="text-sm text-text-tertiary">{t('landing.hero.card_label')}</p>
                      <p className="text-2xl font-bold text-gradient-brand">+2,847 XP</p>
                    </div>
                  </div>
                </div>
                <div className="absolute top-20 -left-10 w-64 h-64 bg-accent-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '3s' }} />
              </div>
            </div>
          </div>
        </section>

        <section id="roadmap" className="py-20 lg:py-28 bg-bg-secondary/50 relative">
          <div className="absolute inset-0 bg-grid-pattern-accent" aria-hidden="true" />
          <div className="relative max-w-full mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16 animate-fade-in">
              <Badge variant="primary" size="md" className="mb-4">
                {t('landing.roadmap.badge')}
              </Badge>
              <h2 className="text-3xl sm:text-4xl font-bold text-text-primary mb-4">
                {t('landing.roadmap.title')}
              </h2>
              <p className="text-lg text-text-secondary max-w-2xl mx-auto">
                {t('landing.roadmap.description')}
              </p>
            </div>

            <div className="bg-bg-primary/50 border border-border-primary/50 rounded-2xl p-6 lg:p-8 animate-slide-up">
              <div className="overflow-x-auto pb-4">
                {/*
                <QuestRoadmap nodes={roadmapPreview} variant="horizontal" />
                */}
                <div className="flex items-start gap-0 overflow-x-auto pb-4 scrollbar-thin" role="list" aria-label="Learning roadmap preview">
                  {roadmapPreview.map((node, index) => (
                    <div key={node.id} className="relative flex flex-col items-center flex-1 min-w-[180px] max-w-[220px] px-2">
                      <div className="relative flex flex-col items-center transition-all duration-300 group">
                        <div className={cn(
                          'relative flex items-center justify-center rounded-full border-2 transition-all duration-300 z-10',
                          node.status === 'completed'
                            ? 'bg-success-500 border-success-500 text-white shadow-glow-success w-14 h-14'
                            : node.status === 'current'
                            ? 'bg-primary-500 border-primary-500 text-white shadow-glow-primary animate-pulse-glow w-14 h-14'
                            : node.status === 'locked'
                            ? 'bg-bg-tertiary border-border-primary text-text-tertiary w-14 h-14'
                            : 'bg-bg-secondary border-border-secondary text-text-secondary w-14 h-14'
                        )}>
                          {node.status === 'completed' ? (
                            <Check className="h-6 w-6" aria-hidden="true" />
                          ) : node.status === 'locked' ? (
                            <span className="text-xl" aria-hidden="true">🔒</span>
                          ) : (
                            <span className="font-bold text-lg" aria-hidden="true">{index + 1}</span>
                          )}
                        </div>
                        <div className="mt-3 w-full px-2 text-center">
                          <h4 className={cn(
                            'font-medium truncate transition-colors',
                            node.status === 'current' ? 'text-text-primary' : node.status === 'completed' ? 'text-text-secondary' : node.status === 'locked' ? 'text-text-tertiary' : 'text-text-secondary'
                          )}>
                            {node.title}
                          </h4>
                          <div className="flex items-center justify-center gap-2 mt-1.5 flex-wrap">
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-bg-tertiary text-text-tertiary border border-border-primary">
                              <span className="h-3 w-3" style={{ backgroundImage: 'url("data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2216%22 height=%2216%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22currentColor%22 stroke-width=%222%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22><circle cx=%2212%22 cy=%2212%22 r=%2210%22></circle><polyline points=%2212 6 12 12 16 14%22></polyline></svg>")' }} />
                              <span>{node.estimatedMinutes} min</span>
                            </span>
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-accent-900/30 text-accent-400 border border-accent-500/30">
                              ⚡ +{node.xpReward} XP
                            </span>
                          </div>
                        </div>
                      </div>
                      {index < roadmapPreview.length - 1 && (
                        <div className="absolute left-1/2 top-[calc(56px+8px)] w-[calc(100%-56px)] h-0.5 -translate-x-1/2" style={{
                          background: node.status === 'completed'
                            ? 'linear-gradient(90deg, #10B981, #10B981)'
                            : 'linear-gradient(90deg, var(--color-border-primary), var(--color-border-primary))',
                        }} aria-hidden="true" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="py-20 lg:py-28 bg-bg-primary relative">
          <div className="absolute inset-0 bg-grid-pattern" aria-hidden="true" />
          <div className="relative max-w-full mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16 animate-fade-in">
              <Badge variant="primary" size="md" className="mb-4">
                {t('landing.features.badge')}
              </Badge>
              <h2 className="text-3xl sm:text-4xl font-bold text-text-primary mb-4">
                {t('landing.features.title')}
              </h2>
              <p className="text-lg text-text-secondary max-w-2xl mx-auto">
                {t('landing.features.description')}
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <Card
                  key={feature.title}
                  variant="interactive"
                  padding="lg"
                  className="animate-fade-in group relative overflow-hidden"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" aria-hidden="true" />
                  <div className="relative z-10">
                    <div className={cn(
                      'p-3 rounded-xl w-fit mb-5 transition-all duration-300',
                      'group-hover:scale-110',
                      feature.accent === 'primary' && 'bg-primary-500/10 text-primary-400 border border-primary-500/20',
                      feature.accent === 'accent' && 'bg-accent-500/10 text-accent-400 border border-accent-500/20',
                      feature.accent === 'warning' && 'bg-warning-500/10 text-warning-400 border border-warning-500/20',
                      feature.accent === 'success' && 'bg-success-500/10 text-success-400 border border-success-500/20',
                    )}>
                      <feature.icon className="h-6 w-6" aria-hidden="true" />
                    </div>
                    <h3 className="text-xl font-semibold text-text-primary mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-text-secondary leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section id="stats" className="py-20 lg:py-28 bg-bg-secondary/50 relative">
          <div className="absolute inset-0 bg-grid-pattern-accent" aria-hidden="true" />
          <div className="relative max-w-full mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={stat.label} className="text-center animate-fade-in relative" style={{ animationDelay: `${index * 100}ms` }}>
                  <div className="p-3 bg-gradient-to-br from-primary-500/10 to-accent-500/10 rounded-2xl w-fit mx-auto mb-4 border border-primary-500/20">
                    <stat.icon className="h-8 w-8 text-primary-400 mx-auto" aria-hidden="true" />
                  </div>
                  <div className="text-4xl sm:text-5xl font-bold text-gradient-brand mb-2">
                    {stat.value}
                  </div>
                  <div className="text-text-secondary">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="cta" className="py-20 lg:py-28 bg-bg-primary relative overflow-hidden">
          <div className="absolute inset-0 bg-mesh-gradient" aria-hidden="true" />
          <div className="relative max-w-full mx-auto px-4 sm:px-6 lg:px-8">
            <Card variant="elevated" padding="lg" className="bg-gradient-to-br from-primary-900/30 via-bg-secondary to-accent-900/30 border-primary-500/30 relative overflow-hidden">
              <div className="absolute inset-0 bg-grid-pattern-opacity" aria-hidden="true" />
              <div className="absolute top-0 right-0 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl -translate-x-1/2 translate-y-1/2" aria-hidden="true" />
              <div className="absolute bottom-0 left-0 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl translate-x-1/2 -translate-y-1/2" aria-hidden="true" />
              <div className="relative text-center max-w-3xl mx-auto">
                <div className="flex items-center justify-center gap-2 mb-6">
                  <span className="px-3 py-1 bg-accent-500/20 text-accent-400 rounded-full text-sm font-medium">
                    {t('landing.cta.badge')}
                  </span>
                </div>
                <h2 className="text-3xl sm:text-4xl font-bold text-text-primary mb-4">
                  {t('landing.cta.title')}
                </h2>
                <p className="text-lg text-text-secondary mb-8 max-w-xl mx-auto">
                  {t('landing.cta.description')}
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link to="/register" className="w-full sm:w-auto">
                    <Button size="lg" fullWidth variant="secondary" leftIcon={<ArrowRight className="h-5 w-5" />} className="bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent">
                      {t('landing.cta.button')}
                    </Button>
                  </Link>
                  <Link to="/app/courses" className="w-full sm:w-auto">
                    <Button size="lg" fullWidth variant="outline" className="border-white/30 text-white hover:bg-white/5 hover:border-white/50">
                      {t('landing.cta.explore')}
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </div>
        </section>
      </main>

      <footer className="bg-bg-secondary border-t border-border-primary py-12">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <Link to="/app/dashboard" className="flex items-center gap-2 mb-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-accent-500">
                  <Code className="h-5 w-5 text-white" aria-hidden="true" />
                </div>
                <span className="text-xl font-bold text-gradient-brand">
                  AtlasCode
                </span>
              </Link>
              <p className="text-text-secondary max-w-sm">
                {t('landing.footer.description')}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-text-primary mb-4">{t('landing.footer.product')}</h4>
              <ul className="space-y-2 text-sm text-text-secondary">
                <li><Link to="/app/courses" className="hover:text-text-primary transition-colors">{t('navigation.courses')}</Link></li>
                <li><Link to="/app/projects" className="hover:text-text-primary transition-colors">{t('navigation.projects')}</Link></li>
                <li><Link to="/app/profile" className="hover:text-text-primary transition-colors">{t('navigation.profile')}</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-text-primary mb-4">{t('landing.footer.company')}</h4>
              <ul className="space-y-2 text-sm text-text-secondary">
                <li><Link to="/privacy" className="hover:text-text-primary transition-colors">{t('footer.privacy_policy')}</Link></li>
                <li><Link to="/terms" className="hover:text-text-primary transition-colors">{t('footer.terms_of_service')}</Link></li>
                <li><Link to="/contact" className="hover:text-text-primary transition-colors">{t('footer.contact')}</Link></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-border-primary flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-text-tertiary text-center md:text-left">
              {t('footer.copyright', { year: new Date().getFullYear() })}
            </p>
            <div className="flex items-center gap-4">
              <a
                href={SOCIAL_LINKS.instagram}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={t('footer.instagram')}
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-text-tertiary transition-all hover:-translate-y-0.5 hover:bg-bg-tertiary hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:ring-offset-2 focus-visible:ring-offset-bg-secondary"
              >
                <InstagramIcon className="h-5 w-5" />
              </a>
              <a
                href={SOCIAL_LINKS.x}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={t('footer.x')}
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-text-tertiary transition-all hover:-translate-y-0.5 hover:bg-bg-tertiary hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:ring-offset-2 focus-visible:ring-offset-bg-secondary"
              >
                <XIcon className="h-4 w-4" />
              </a>
              <a
                href={SOCIAL_LINKS.github}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={t('footer.github')}
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-text-tertiary transition-all hover:-translate-y-0.5 hover:bg-bg-tertiary hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:ring-offset-2 focus-visible:ring-offset-bg-secondary"
              >
                <GithubIcon className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}