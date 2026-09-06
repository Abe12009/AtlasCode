import { LegalLayout } from '../components/LegalLayout';
import { Alert } from '../components/ui';
import { useTranslation } from '../hooks/useTranslation';

interface LegalSection {
  title: string;
  body: string;
}

export function Privacy() {
  const { t } = useTranslation();
  const sections = t('legal.privacy.sections', { returnObjects: true }) as LegalSection[];

  return (
    <LegalLayout title={t('legal.privacy.title')} intro={t('legal.privacy.intro')}>
      {sections.map((section) => (
        <section key={section.title}>
          <h2 className="text-xl font-semibold text-text-primary">{section.title}</h2>
          <p className="mt-2 leading-relaxed text-text-secondary">{section.body}</p>
        </section>
      ))}
      <Alert variant="info">{t('legal.placeholder_notice')}</Alert>
    </LegalLayout>
  );
}
