import { useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Code, Lock, Loader2, ArrowLeft, CheckCircle2, XCircle } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import { Button, PasswordInput, Card, cn } from '../components/ui';
import { authApi } from '../api/services';

export function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const { t, isRTL } = useTranslation();

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!password) {
      newErrors.password = t('auth.password_required');
    } else if (password.length < 8) {
      newErrors.password = t('auth.password_min_length');
    } else if (password.length > 100) {
      newErrors.password = t('auth.password_max_length');
    }
    if (password !== confirmPassword) {
      newErrors.confirmPassword = t('auth.passwords_dont_match');
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || !validate()) return;

    setLoading(true);
    try {
      await authApi.resetPassword({ token, new_password: password });
      setDone(true);
    } catch {
      // 400 covers every failure mode (expired, tampered, already used) --
      // the token itself is invalid, not any one field on this form.
      setErrors({ form: t('auth.reset_password_invalid_link_description') });
    } finally {
      setLoading(false);
    }
  };

  const linkInvalid = !token || errors.form;

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
              </div>
              <span className="text-2xl font-bold text-text-primary">AtlasCode</span>
            </Link>
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              {done
                ? t('auth.reset_password_success_title')
                : linkInvalid
                ? t('auth.reset_password_invalid_link_title')
                : t('auth.reset_password_title')}
            </h1>
            <p className="text-text-secondary">
              {done
                ? t('auth.reset_password_success_description')
                : linkInvalid
                ? t('auth.reset_password_invalid_link_description')
                : t('auth.reset_password_description')}
            </p>
          </div>

          {done ? (
            <div className="flex flex-col items-center gap-4 text-center">
              <CheckCircle2 className="h-12 w-12 text-success-500" aria-hidden="true" />
            </div>
          ) : linkInvalid ? (
            <div className="flex flex-col items-center gap-4 text-center">
              <XCircle className="h-12 w-12 text-error-500" aria-hidden="true" />
              <Link to="/forgot-password">
                <Button size="lg">{t('auth.reset_password_request_new_link')}</Button>
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} noValidate className="space-y-5">
              <PasswordInput
                label={t('common.password')}
                id="password"
                name="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                error={errors.password}
                leftIcon={<Lock className="h-4 w-4" />}
              />
              <PasswordInput
                label={t('common.confirm_password')}
                id="confirmPassword"
                name="confirmPassword"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                error={errors.confirmPassword}
                leftIcon={<Lock className="h-4 w-4" />}
              />
              <Button
                type="submit"
                fullWidth
                loading={loading}
                leftIcon={loading ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : undefined}
                size="lg"
              >
                {t('auth.reset_password_submit')}
              </Button>
            </form>
          )}

          <div className="text-center mt-6">
            <Link to="/login" className="inline-flex items-center gap-1.5 text-primary-400 hover:text-primary-300 font-medium">
              <ArrowLeft className="h-4 w-4 rtl:rotate-180" aria-hidden="true" />
              {t('auth.back_to_login')}
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
