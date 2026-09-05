import { GraduationCap } from 'lucide-react';
import { useTranslation } from '../../hooks/useTranslation';

interface ExamTipProps {
  /** Already resolved to the current language by the caller. */
  text: string;
}

/** A short, optional, visually distinct callout. Never claims to reflect an
 * official exam — it states a Python mechanic the student can verify in the
 * lesson itself. */
export function ExamTip({ text }: ExamTipProps) {
  const { t } = useTranslation();

  return (
    <div
      data-testid="exam-tip"
      className="flex items-start gap-3 rounded-xl border border-warning-500/30 bg-warning-500/10 p-4"
    >
      <GraduationCap className="h-5 w-5 flex-shrink-0 text-warning-400" />
      <div className="min-w-0">
        <p className="text-sm font-semibold text-warning-300">{t('microquest.exam_tip_label')}</p>
        <p className="mt-1 break-words text-sm text-text-secondary">{text}</p>
      </div>
    </div>
  );
}
