import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { Code, Loader2, Mail, Lock } from 'lucide-react';
import { Button, Input, PasswordInput, Card, Alert, cn } from '../components/ui';
import { GoogleIcon, GithubIcon } from '../components/icons/BrandIcons';
import { describeFirebaseAuthError } from '../lib/firebase';
import { authApi } from '../api/services';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<'google' | 'github' | null>(null);
  const { login, loginWithGoogle, loginWithGithub } = useAuth();
  const { t, isRTL } = useTranslation();
  const navigate = useNavigate();
  const { data: authConfig } = useQuery({
    queryKey: ['auth-config'],
    queryFn: authApi.getConfig,
    staleTime: Infinity,
    retry: false,
  });
  // Assume available while loading so the buttons don't flash disabled on a slow network.
  const oauthAvailable = authConfig?.firebase_enabled ?? true;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/app/dashboard');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || t('auth.login_failed'));
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'github') => {
    setError('');
    setOauthLoading(provider);
    try {
      await (provider === 'google' ? loginWithGoogle() : loginWithGithub());
      navigate('/app/dashboard');
    } catch (err: unknown) {
      setError(describeFirebaseAuthError(err));
    } finally {
      setOauthLoading(null);
    }
  };

  return (
    <div className={cn('min-h-screen flex items-center justify-center bg-bg-primary px-4 py-12 relative overflow-hidden', isRTL ? 'rtl' : 'ltr')}>
      <div className="absolute inset-0 bg-mesh-gradient" aria-hidden="true" />
      <div className="absolute inset-0 bg-grid-pattern" aria-hidden="true" />
      <div className="relative w-full max-w-md">
        <Card variant="elevated" padding="lg" className="bg-bg-secondary/80 backdrop-blur-xl border-border-primary/50 relative z-10">
          <div className="text-center pb-8">
            <Link to="/" className="inline-flex items-center gap-2 mb-6" aria-label={t('common.home')}>
              <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
                <Code className="h-6 w-6 text-white" aria-hidden="true" />
                <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-accent-500" aria-hidden="true" />
              </div>
              <span className="text-2xl font-bold text-gradient-brand">
                AtlasCode
              </span>
            </Link>
            <h1 className="text-2xl font-bold text-text-primary mb-2">{t('auth.welcome_back')}</h1>
            <p className="text-text-secondary">{t('auth.sign_in_continue')}</p>
          </div>

          <div className="space-y-6">
            {error && (
              <Alert variant="error" title={t('common.error')} dismissible onDismiss={() => setError('')}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit} noValidate className="space-y-5">
              <Input
                label={t('common.email')}
                type="email"
                id="email"
                name="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                disabled={loading}
                leftIcon={<Mail className="h-4 w-4" />}
              />

              <PasswordInput
                label={t('common.password')}
                id="password"
                name="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"
                disabled={loading}
                leftIcon={<Lock className="h-4 w-4" />}
              />

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-border-primary text-primary-500 focus:ring-2 focus:ring-primary-500/20"
                  />
                  <span className="text-sm text-text-secondary">{t('auth.remember_me')}</span>
                </label>
                <Link to="/forgot-password" className="text-sm text-primary-400 hover:text-primary-300 font-medium">
                  {t('auth.forgot_password')}
                </Link>
              </div>

              <Button
                type="submit"
                fullWidth
                loading={loading}
                leftIcon={loading ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : undefined}
                size="lg"
                className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-glow-primary"
              >
                {t('auth.sign_in')}
              </Button>
            </form>

            {oauthAvailable && (
              <>
                <div className="relative">
                  <div className="absolute inset-0 flex items-center" aria-hidden="true">
                    <div className="w-full border-t border-border-primary/50" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-bg-secondary/80 text-text-tertiary">{t('auth.or_continue_with')}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    fullWidth
                    loading={oauthLoading === 'google'}
                    disabled={oauthLoading !== null}
                    onClick={() => handleOAuth('google')}
                    className="border-border-primary/50 hover:border-primary-500/50 hover:bg-primary-500/5"
                  >
                    {oauthLoading !== 'google' && <GoogleIcon className="h-5 w-5" />}
                    <span>Google</span>
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    fullWidth
                    loading={oauthLoading === 'github'}
                    disabled={oauthLoading !== null}
                    onClick={() => handleOAuth('github')}
                    className="border-border-primary/50 hover:border-primary-500/50 hover:bg-primary-500/5"
                  >
                    {oauthLoading !== 'github' && <GithubIcon className="h-5 w-5" />}
                    <span>GitHub</span>
                  </Button>
                </div>
              </>
            )}

            <div className="text-center mt-6">
              <p className="text-text-secondary">
                {t('auth.dont_have_account')}{' '}
                <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium">
                  {t('auth.sign_up')}
                </Link>
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}