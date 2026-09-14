import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { feedbackApi } from '../api/services';
import { Modal, Select, Textarea, Button, Alert } from './ui';
import { useTranslation } from '../hooks/useTranslation';

const FEEDBACK_CATEGORIES = ['bug', 'suggestion', 'other'] as const;

export function FeedbackModal({ onClose }: { onClose: () => void }) {
  const { t } = useTranslation();
  const location = useLocation();
  const [category, setCategory] = useState<string>(FEEDBACK_CATEGORIES[0]);
  const [message, setMessage] = useState('');

  const submitMutation = useMutation({
    mutationFn: () => feedbackApi.submit({ category, message: message.trim(), page_path: location.pathname }),
  });

  return (
    <Modal isOpen onClose={onClose} title={t('feedback.title')} description={t('feedback.description')} size="sm">
      {submitMutation.isSuccess ? (
        <Alert variant="success">{t('feedback.success')}</Alert>
      ) : (
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            submitMutation.mutate();
          }}
        >
          <Select
            label={t('feedback.category_label')}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            options={FEEDBACK_CATEGORIES.map((c) => ({ value: c, label: t(`feedback.category_${c}`) }))}
          />
          <Textarea
            label={t('feedback.message_label')}
            placeholder={t('feedback.message_placeholder')}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={4}
            maxLength={4000}
            required
          />
          {submitMutation.isError && <Alert variant="error">{t('feedback.error')}</Alert>}
          <Button type="submit" fullWidth loading={submitMutation.isPending} disabled={!message.trim()}>
            {t('feedback.submit')}
          </Button>
        </form>
      )}
    </Modal>
  );
}
