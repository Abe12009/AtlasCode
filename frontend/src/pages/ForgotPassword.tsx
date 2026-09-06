import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Code, Mail, Loader2, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { Button, Input, Card, Alert, cn } from '../components/ui';
import { isFirebaseConfigured } from '../lib/firebase';

export function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const { sendPasswordReset } = useAuth();
  const { t, isRTL } = useTranslation();

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      await sendPasswordReset(email.trim());
    } catch {
      // Deliberately swallowed: whether the send failed because the address
      // doesn't exist or for any other reason, the UI shows the same neutral
      // confirmation so it never reveals which emails are registered.
    } finally {
      setLoading(false);
      setSent(true);
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
              </div>
              <span className="text-2xl font-bold text-text-primary">AtlasCode</span>
            </Link>
            <h1 className="text-2xl font-bold text-text-primary mb-2">
              {sent ? t('auth.reset_password_sent_title') : t('auth.reset_password_title')}
            </h1>
            <p className="text-text-secondary">
              {sent ? t('auth.reset_password_sent_description') : t('auth.reset_password_description')}
            </p>
          </div>

          {!isFirebaseConfigured ? (
            <Alert variant="warning">{t('auth.reset_password_not_configured')}</Alert>
          ) : sent ? (
            <div className="flex flex-col items-center gap-4 text-center">
              <CheckCircle2 className="h-12 w-12 text-success-500" aria-hidden="true" />
            </div>
          ) : (
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
              <Button
                type="submit"
                fullWidth
                loading={loading}
                leftIcon={loading ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : undefined}
                size="lg"
              >
                {t('auth.reset_password_send')}
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
