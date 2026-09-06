import { useState, type FormEvent } from 'react';
import { Mail } from 'lucide-react';
import { LegalLayout } from '../components/LegalLayout';
import { Button, Input, Textarea } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';
import { CONTACT_EMAIL } from '../config/site';

/**
 * There is no backend ticketing endpoint yet, so submitting hands the message
 * off to the visitor's own email client via a pre-filled `mailto:` link rather
 * than pretending to call an API that doesn't exist. Swap this for a real POST
 * to a support endpoint once one is built.
 */
export function Contact() {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const body = `${message}\n\n— ${name} (${email})`;
    const mailto = `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(
      subject || 'AtlasCode contact form',
    )}&body=${encodeURIComponent(body)}`;
    window.location.href = mailto;
    setSent(true);
  };

  return (
    <LegalLayout title={t('legal.contact.title')} intro={t('legal.contact.intro')} showLastUpdated={false}>
      {sent ? (
        <div className="rounded-xl border border-success-500/30 bg-success-500/5 p-6 text-success-700 dark:text-success-300">
          {t('legal.contact.form.success')}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div className="grid gap-5 sm:grid-cols-2">
            <Input
              label={t('legal.contact.form.name')}
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoComplete="name"
            />
            <Input
              type="email"
              label={t('legal.contact.form.email')}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <Input
            label={t('legal.contact.form.subject')}
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
          />
          <Textarea
            label={t('legal.contact.form.message')}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
            rows={6}
          />
          <Button type="submit" size="lg">
            {t('legal.contact.form.submit')}
          </Button>
        </form>
      )}

      <div className="flex items-center gap-2 border-t border-border-primary pt-6 text-sm text-text-secondary">
        <Mail className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
        <span>
          {t('legal.contact.fallback')}{' '}
          <a href={`mailto:${CONTACT_EMAIL}`} className="font-medium text-primary-400 hover:underline">
            {CONTACT_EMAIL}
          </a>
        </span>
      </div>
      <p className="text-sm text-text-tertiary">{t('legal.contact.response_time')}</p>
    </LegalLayout>
  );
}
