import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { Code, Eye, EyeOff, Loader2, CheckCircle, AlertCircle, Mail, Lock, User, Globe, Sparkles } from 'lucide-react';
import { Button, Input, Card, Alert, Select, cn } from '../components/ui';

export function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    preferred_language: 'en',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { t, isRTL } = useTranslation();
  const navigate = useNavigate();

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.username.trim()) {
      newErrors.username = t('auth.username_required');
    } else if (formData.username.length < 3) {
      newErrors.username = t('auth.username_min_length');
    } else if (formData.username.length > 100) {
      newErrors.username = t('auth.username_max_length');
    }

    if (!formData.email.trim()) {
      newErrors.email = t('auth.email_required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = t('auth.email_invalid');
    }

    if (!formData.password) {
      newErrors.password = t('auth.password_required');
    } else if (formData.password.length < 8) {
      newErrors.password = t('auth.password_min_length');
    } else if (formData.password.length > 100) {
      newErrors.password = t('auth.password_max_length');
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = t('auth.passwords_dont_match');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const checkPasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);

    try {
      await register({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
        preferred_language: formData.preferred_language,
      });
      navigate('/app/dashboard');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrors({ form: axiosError.response?.data?.detail || t('auth.registration_failed') });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const passwordStrength = checkPasswordStrength(formData.password);

  const strengthLabels = [
    t('auth.very_weak'),
    t('auth.weak'),
    t('auth.fair'),
    t('auth.good'),
    t('auth.strong')
  ];

  const strengthColors = [
    'bg-error-500',
    'bg-error-500',
    'bg-warning-500',
    'bg-primary-500',
    'bg-success-500'
  ];

  const languageOptions = [
    { value: 'en', label: t('common.english') },
    { value: 'fr', label: t('common.french') },
    { value: 'ar', label: t('common.arabic') },
  ];

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
              <span className="text-2xl font-bold text-text-primary bg-gradient-to-r from-text-primary via-primary-400 to-accent-400 bg-clip-text text-transparent">
                AtlasCode
              </span>
            </Link>
            <h1 className="text-2xl font-bold text-text-primary mb-2">{t('auth.create_account_text')}</h1>
            <p className="text-text-secondary">{t('auth.start_journey')}</p>
          </div>

          <div className="space-y-6">
            {errors.form && (
              <Alert variant="error" title={t('common.error')} dismissible onDismiss={() => setErrors(prev => ({ ...prev, form: '' }))}>
                {errors.form}
              </Alert>
            )}

            <form onSubmit={handleSubmit} noValidate className="space-y-5" role="form">
              <Input
                label={t('common.username')}
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                placeholder="Choose a username"
                disabled={loading}
                error={errors.username}
                leftIcon={<User className="h-4 w-4" />}
              />

              <Input
                label={t('common.email')}
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="you@example.com"
                disabled={loading}
                error={errors.email}
                leftIcon={<Mail className="h-4 w-4" />}
              />

              <Input
                label={t('common.password')}
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                autoComplete="new-password"
                required
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"
                disabled={loading}
                error={errors.password}
                leftIcon={<Lock className="h-4 w-4" />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-text-tertiary hover:text-text-primary transition-colors"
                    aria-label={showPassword ? t('accessibility.toggle_password_visibility') : t('accessibility.toggle_password_visibility')}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" aria-hidden="true" />
                    ) : (
                      <Eye className="h-4 w-4" aria-hidden="true" />
                    )}
                  </button>
                }
              />

              {!errors.password && formData.password && (
                <div className="space-y-2">
                  <div className="flex gap-1" role="progressbar" aria-valuenow={passwordStrength} aria-valuemin={0} aria-valuemax={5} aria-label={t('auth.password_strength')}>
                    {[1, 2, 3, 4, 5].map((level) => (
                      <div
                        key={level}
                        className={cn('h-2 flex-1 rounded transition-colors',
                          level <= passwordStrength
                            ? strengthColors[level - 1]
                            : 'bg-border-primary'
                        )}
                      />
                    ))}
                  </div>
                  <p className="text-xs text-text-tertiary">
                    {strengthLabels[passwordStrength - 1] || t('auth.very_weak')}
                  </p>
                </div>
              )}

              <Input
                label={t('common.confirm_password')}
                type={showPassword ? 'text' : 'password'}
                id="confirmPassword"
                name="confirmPassword"
                autoComplete="new-password"
                required
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                placeholder="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"
                disabled={loading}
                error={errors.confirmPassword}
                leftIcon={<Lock className="h-4 w-4" />}
              />

              <Select
                label={t('common.preferred_language')}
                id="preferred_language"
                name="preferred_language"
                value={formData.preferred_language}
                onChange={(e) => handleChange('preferred_language', e.target.value)}
                options={languageOptions}
                placeholder={t('common.preferred_language')}
                disabled={loading}
              />

              <Button
                type="submit"
                fullWidth
                loading={loading}
                leftIcon={loading ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : <CheckCircle className="h-5 w-5" />}
                size="lg"
                className="bg-gradient-to-r from-accent-500 to-accent-600 hover:from-accent-600 hover:to-accent-700 shadow-lg hover:shadow-glow-accent"
              >
                {t('auth.create_account')}
              </Button>
            </form>

            <div className="text-center">
              <p className="text-text-secondary">
                {t('auth.already_have_account')}{' '}
                <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
                  {t('auth.sign_in_link')}
                </Link>
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}