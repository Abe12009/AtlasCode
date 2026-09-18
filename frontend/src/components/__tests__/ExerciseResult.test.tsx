import React from 'react';
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../test/setup.tsx';
import { ExerciseResult } from '../ExerciseAnswer';
import type { ExerciseSubmitResponse } from '../../types';

function buildResult(overrides: Partial<ExerciseSubmitResponse> = {}): ExerciseSubmitResponse {
  return {
    is_correct: true,
    xp_earned: 10,
    feedback: 'Nice work!',
    output: null,
    error: null,
    ...overrides,
  };
}

describe('ExerciseResult test-case checklist', () => {
  it('renders no checklist when test_results is absent (non-code exercise types)', async () => {
    await renderWithProviders(<ExerciseResult result={buildResult({ test_results: null })} />);
    expect(screen.queryByTestId('test-results-checklist')).not.toBeInTheDocument();
  });

  it('renders a passing row with a checkmark for each passed assertion', async () => {
    await renderWithProviders(
      <ExerciseResult
        result={buildResult({
          test_results: [
            { assertion: 'assert double(2) == 4', passed: true, message: null },
            { assertion: 'assert double(0) == 0', passed: true, message: null },
          ],
        })}
      />
    );
    const list = screen.getByTestId('test-results-checklist');
    expect(list).toHaveTextContent('assert double(2) == 4');
    expect(list).toHaveTextContent('assert double(0) == 0');
    expect(list.querySelectorAll('.lucide-x')).toHaveLength(0);
  });

  it('renders a failing row with an X and the failure message, alongside passing rows', async () => {
    await renderWithProviders(
      <ExerciseResult
        result={buildResult({
          is_correct: false,
          test_results: [
            { assertion: 'assert double(2) == 4', passed: true, message: null },
            { assertion: 'assert double(3) == 6', passed: false, message: 'the decorator must accept any signature' },
          ],
        })}
      />
    );
    const list = screen.getByTestId('test-results-checklist');
    const rows = list.querySelectorAll('li');
    expect(rows).toHaveLength(2);
    expect(list).toHaveTextContent('assert double(3) == 6');
    expect(list).toHaveTextContent('the decorator must accept any signature');
    // Exactly one failing row -> exactly one X icon, one check icon.
    expect(list.querySelectorAll('.lucide-x')).toHaveLength(1);
    expect(list.querySelectorAll('.lucide-check')).toHaveLength(1);
  });

  it('does not render an empty checklist container when test_results is an empty array', async () => {
    await renderWithProviders(<ExerciseResult result={buildResult({ test_results: [] })} />);
    expect(screen.queryByTestId('test-results-checklist')).not.toBeInTheDocument();
  });
});
