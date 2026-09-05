import { Link } from 'react-router-dom';
import { Code, ArrowRight, BookOpen, FolderKanban, Trophy, Zap, Shield, Globe, ChevronRight, Check, Star, Sparkles, Terminal, Layers, Brain } from 'lucide-react';
import { Button, Card, Badge, cn } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';

export function Landing() {
  const { t, currentLanguage, changeLanguage, languages, isRTL } = useTranslation();

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
              <span className="text-xl font-bold text-text-primary bg-gradient-to-r from-text-primary via-primary-400 to-accent-400 bg-clip-text text-transparent">
                AtlasCode
              </span>
            </Link>

            <nav className="hidden lg:flex items-center gap-6" aria-label={t('navigation.main')}>
              <Link to="#features" className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                {t('landing.nav.features')}
              </Link>
              <Link to="#roadmap" className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                {t('landing.nav.roadmap')}
              </Link>
              <Link to="#stats" className="text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                {t('landing.nav.stats')}
              </Link>
            </nav>

            <div className="flex items-center gap-4">
              <div className="relative hidden sm:block">
                <Button
                  variant="ghost"
                  size="sm"
                  leftIcon={<Globe className="h-4 w-4" />}
                  onClick={() => { }}
                  aria-label={t('common.language')}
                  className="gap-1.5"
                >
                  <span className="hidden sm:inline text-sm font-medium text-text-secondary">
                    {languages.find(l => l.code === currentLanguage)?.nativeName || currentLanguage}
                  </span>
                  <ChevronRight className="h-4 w-4 text-text-tertiary" />
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <Link to="/login" className="hidden sm:inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors rounded-xl">
                  {t('auth.sign_in')}
                </Link>
                <Link to="/register" className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 transition-all rounded-xl shadow-lg hover:shadow-glow-accent">
                  {t('auth.sign_up')}
                </Link>
              </div>
            </div>
          </div>
        </div>
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
                  <span className="bg-gradient-to-r from-primary-400 via-accent-400 to-primary-400 bg-clip-text text-transparent animate-gradient-shift">
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
                      <p className="text-2xl font-bold text-text-primary bg-gradient-to-r from-primary-400 to-accent-400 bg-clip-text text-transparent">+2,847 XP</p>
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
                  <div className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-primary-400 via-accent-400 to-primary-400 bg-clip-text text-transparent mb-2">
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
                <span className="text-xl font-bold text-text-primary bg-gradient-to-r from-text-primary via-primary-400 to-accent-400 bg-clip-text text-transparent">
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
                <li><a href="#" className="hover:text-text-primary transition-colors">{t('footer.privacy_policy')}</a></li>
                <li><a href="#" className="hover:text-text-primary transition-colors">{t('footer.terms_of_service')}</a></li>
                <li><a href="#" className="hover:text-text-primary transition-colors">{t('footer.contact')}</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-border-primary flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-text-tertiary text-center md:text-left">
              {t('footer.copyright', { year: new Date().getFullYear() })}
            </p>
            <div className="flex items-center gap-6">
              <a href="#" className="text-text-tertiary hover:text-text-primary transition-colors" aria-label="GitHub">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                </svg>
              </a>
              <a href="#" className="text-text-tertiary hover:text-text-primary transition-colors" aria-label="Discord">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.618-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.682 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.083.083 0 0 0 .031.057 19.9 19.9 0 0 0 5.994 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 1 .077-.032c.818-.414 1.672-.748 2.553-.999a.077.077 0 0 1 .077.032c.126.252.29.542.48.886a14.36 14.36 0 0 0 1.19 1.967.077.077 0 0 0 .083.028 19.839 19.839 0 0 0 6.005-3.03.077.077 0 0 0 .032-.054c.428-4.534-.354-9.097-1.551-13.66a.061.061 0 0 0-.032-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333 1.007-2.419 2.157-2.419 1.177 0 2.133.97 2.133 2.3 0 1.373-.956 2.383-2.133 2.383zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333 1.007-2.419 2.157-2.419 1.177 0 2.133.97 2.133 2.3 0 1.373-.956 2.383-2.133 2.383z"/>
                </svg>
              </a>
              <a href="#" className="text-text-tertiary hover:text-text-primary transition-colors" aria-label="Twitter">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}