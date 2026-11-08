import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../../test/setup.tsx';
import { StatusBadge, type Status } from '../StatusBadge';

/**
 * StatusBadge used to hardcode English labels, so a French or Arabic student
 * reading an otherwise translated page saw "Completed" / "Locked". The labels
 * come from `lessons.*` -- the same keys QuestNode already uses for the same
 * four states, so a badge and a roadmap node cannot drift apart.
 */
const EXPECTED: Record<string, Partial<Record<Status, string>>> = {
  en: {
    completed: 'Completed',
    current: 'In progress',
    available: 'Available',
    locked: 'Locked',
    in_progress: 'In progress',
    pending: 'Pending',
  },
  fr: {
    completed: 'Terminé',
    current: 'En cours',
    available: 'Disponible',
    locked: 'Verrouillé',
    in_progress: 'En cours',
    pending: 'En attente',
  },
  ar: {
    completed: 'مكتمل',
    current: 'قيد التقدم',
    available: 'متاح',
    locked: 'مقفل',
    in_progress: 'قيد التقدم',
    pending: 'قيد الانتظار',
  },
};

const ALL_STATUSES: Status[] = [
  'completed',
  'current',
  'available',
  'locked',
  'in_progress',
  'pending',
];

describe('StatusBadge labels are translated', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  for (const [language, labels] of Object.entries(EXPECTED)) {
    it(`renders every status in ${language}`, async () => {
      await renderWithProviders(
        <div>
          {ALL_STATUSES.map((status) => (
            <span key={status} data-testid={`badge-${status}`}>
              <StatusBadge status={status} />
            </span>
          ))}
        </div>,
        { initialLanguage: language },
      );

      for (const status of ALL_STATUSES) {
        expect(screen.getByTestId(`badge-${status}`)).toHaveTextContent(labels[status]!);
      }
    });
  }

  it('shows no raw i18n key when a label is missing', async () => {
    await renderWithProviders(<StatusBadge status="locked" />, { initialLanguage: 'ar' });
    expect(screen.queryByText(/lessons\./)).not.toBeInTheDocument();
  });
});
