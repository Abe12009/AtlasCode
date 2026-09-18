import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ChevronLeft, AlertTriangle } from 'lucide-react';
import { orientiniApi } from '../api/services';
import { useTranslation } from '../hooks/useTranslation';
import { Card, Badge, Skeleton } from '../components/ui';
import type { InstitutionType } from '../types';

function translationFor<T extends { language: string }>(items: T[], language: string): T | undefined {
  return items.find((item) => item.language === language) || items[0];
}

const INSTITUTION_TYPE_KEYS: Record<InstitutionType, string> = {
  code_school: 'orientini.type_code_school',
  est: 'orientini.type_est',
  fst: 'orientini.type_fst',
  cpge: 'orientini.type_cpge',
  engineering_school: 'orientini.type_engineering_school',
};

export function OrientiniExplorer() {
  const { t, currentLanguage, isRTL } = useTranslation();

  const { data: institutions, isLoading } = useQuery({
    queryKey: ['orientini-institutions', currentLanguage],
    queryFn: () => orientiniApi.getInstitutions(currentLanguage),
  });

  return (
    <div className="space-y-8 animate-fade-in" dir={isRTL ? 'rtl' : 'ltr'}>
      <div>
        <Link to="/app/orientini" className="inline-flex items-center gap-2 text-text-tertiary hover:text-primary-400 dark:hover:text-primary-300 text-sm font-medium transition-colors mb-3">
          <ChevronLeft className="h-4 w-4" />
          <span>{t('orientini.nav_label')}</span>
        </Link>
        <h1 className="text-2xl font-bold text-text-primary">{t('orientini.explorer_title')}</h1>
        <p className="text-text-tertiary text-sm mt-1">{t('orientini.explorer_description')}</p>
      </div>

      {isLoading ? (
        <div className="grid md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} variant="rectangular" height={220} />
          ))}
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {(institutions ?? []).map((institution) => {
            const translation = translationFor(institution.translations, currentLanguage);
            const requirement = institution.requirement;
            return (
              <Card key={institution.id} padding="lg" className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl" aria-hidden="true">{institution.icon}</span>
                  <div>
                    <h2 className="font-semibold text-text-primary">{translation?.name}</h2>
                    <Badge variant="outline" size="sm">{t(INSTITUTION_TYPE_KEYS[institution.type])}</Badge>
                  </div>
                </div>

                {translation?.description && (
                  <p className="text-sm text-text-secondary">{translation.description}</p>
                )}

                {translation?.career_outcomes && (
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-text-tertiary mb-1">
                      {t('orientini.career_outcomes')}
                    </h3>
                    <p className="text-sm text-text-secondary">{translation.career_outcomes}</p>
                  </div>
                )}

                <div className="rounded-xl border border-border-primary p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-semibold uppercase tracking-wide text-text-tertiary">
                      {t('orientini.requirements')}
                    </h3>
                    {!requirement?.data_verified && (
                      <Badge variant="warning" size="sm" dot dotColor="warning">
                        {t('orientini.needs_verification')}
                      </Badge>
                    )}
                  </div>

                  {!requirement?.data_verified ? (
                    <p className="text-xs text-text-tertiary flex items-start gap-1.5">
                      <AlertTriangle className="h-3.5 w-3.5 mt-0.5 flex-shrink-0 text-warning-500" />
                      {t('orientini.needs_verification_note')}
                    </p>
                  ) : (
                    <dl className="text-sm text-text-secondary space-y-1">
                      {requirement.eligible_bac_tracks ? (
                        <div>
                          <dt className="inline font-medium">{t('orientini.eligible_tracks')}: </dt>
                          <dd className="inline">
                            {requirement.eligible_bac_tracks.map((track) => t(`orientini.bac_track_${track}`)).join(', ')}
                          </dd>
                        </div>
                      ) : (
                        <div>{t('orientini.any_track')}</div>
                      )}
                      {requirement.min_bac_average !== null && (
                        <div>
                          <dt className="inline font-medium">{t('orientini.min_average')}: </dt>
                          <dd className="inline">{requirement.min_bac_average}</dd>
                        </div>
                      )}
                      {requirement.entrance_exam_name && (
                        <div>
                          <dt className="inline font-medium">{t('orientini.entrance_exam')}: </dt>
                          <dd className="inline">{requirement.entrance_exam_name}</dd>
                        </div>
                      )}
                      {requirement.application_window && (
                        <div>
                          <dt className="inline font-medium">{t('orientini.application_window')}: </dt>
                          <dd className="inline">{requirement.application_window}</dd>
                        </div>
                      )}
                    </dl>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
