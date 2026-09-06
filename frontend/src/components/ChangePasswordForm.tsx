import { useState, type FormEvent } from 'react';
import { Lock } from 'lucide-react';
import { Button, PasswordInput, Alert } from './ui';
import { useTranslation } from '../hooks/useTranslation';
import { authApi } from '../api/services';

export function ChangePasswordForm() {
  const { t } = useTranslation();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setSuccess(false);

    if (newPassword.length < 8) {
      setError(t('auth.password_min_length'));
      return;
    }
    if (newPassword !== confirmPassword) {
      setError(t('auth.passwords_dont_match'));
      return;
    }

    setLoading(true);
    try {
      await authApi.changePassword({ current_password: currentPassword, new_password: newPassword });
      setSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: unknown) {
      const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
      if (axiosError.response?.status === 401) {
        setError(t('settings.current_password_incorrect'));
      } else {
        setError(axiosError.response?.data?.detail || t('settings.password_change_failed'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <Alert variant="error">{error}</Alert>}
      {success && <Alert variant="success">{t('settings.password_changed')}</Alert>}
      <PasswordInput
        label={t('settings.current_password')}
        value={currentPassword}
        onChange={(e) => setCurrentPassword(e.target.value)}
        required
        autoComplete="current-password"
        leftIcon={<Lock className="h-4 w-4" />}
        disabled={loading}
      />
      <PasswordInput
        label={t('settings.new_password')}
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        required
        autoComplete="new-password"
        leftIcon={<Lock className="h-4 w-4" />}
        disabled={loading}
      />
      <PasswordInput
        label={t('common.confirm_password')}
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        autoComplete="new-password"
        leftIcon={<Lock className="h-4 w-4" />}
        disabled={loading}
      />
      <Button type="submit" loading={loading}>
        {t('settings.change_password')}
      </Button>
    </form>
  );
}
