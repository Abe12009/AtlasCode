import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Orientini } from '../Orientini';
import { renderWithProviders } from '../../test/setup.tsx';
import { orientiniApi } from '../../api/services';
import type { Institution, OrientiniQuestion, OrientiniResult } from '../../types';

const mockedApi = vi.mocked(orientiniApi);

const QUESTIONS: OrientiniQuestion[] = [
  {
    id: 1,
    order: 1,
    translations: [{ language: 'en', text: 'What feels most satisfying?' }],
    options: [
      { id: 10, order: 1, translations: [{ language: 'en', text: 'Building something hands-on' }] },
      { id: 11, order: 2, translations: [{ language: 'en', text: 'Understanding deeply why it works' }] },
    ],
  },
];

const INSTITUTIONS: Institution[] = [
  {
    id: 100,
    slug: '1337',
    type: 'code_school',
    order: 1,
    icon: '🧩',
    translations: [{ language: 'en', name: '1337 Coding School', description: 'Peer-to-peer coding school.', career_outcomes: null }],
    requirement: {
      eligible_bac_tracks: null,
      min_bac_average: null,
      entrance_exam_name: null,
      entrance_exam_format: null,
      application_window: null,
      data_verified: false,
      verification_notes: null,
    },
  },
];

const RESULT: OrientiniResult = {
  id: 1,
  bac_track: 'sciences_math_a',
  scores: [{ institution_id: 100, score: 0.87, eligible: true, trait_breakdown: {} }],
  created_at: new Date().toISOString(),
};

describe('Orientini quiz page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedApi.getQuestions.mockResolvedValue(QUESTIONS);
    mockedApi.getInstitutions.mockResolvedValue(INSTITUTIONS);
    mockedApi.getLatestResult.mockRejectedValue(new Error('no prior result'));
    mockedApi.submit.mockResolvedValue(RESULT);
  });

  it('shows the intro screen with a start-quiz action', async () => {
    await renderWithProviders(<Orientini />);
    expect(await screen.findByTestId('orientini-start-quiz')).toBeInTheDocument();
    expect(screen.getByText('Find your path')).toBeInTheDocument();
  });

  it('walks through the bac-track step and a question, then submits and shows ranked results', async () => {
    const user = userEvent.setup();
    await renderWithProviders(<Orientini />);

    await user.click(await screen.findByTestId('orientini-start-quiz'));

    // Step 1: bac track (optional, but pick one to exercise the selection).
    expect(await screen.findByText("What's your Bac track?")).toBeInTheDocument();
    await user.click(screen.getByText('Sciences Math A'));
    await user.click(screen.getByText('Next'));

    // Step 2: the single seeded question.
    expect(await screen.findByText('What feels most satisfying?')).toBeInTheDocument();
    await user.click(screen.getByText('Building something hands-on'));
    await user.click(screen.getByText('See my results'));

    await waitFor(() => {
      expect(mockedApi.submit).toHaveBeenCalledWith({
        answers: { 1: 10 },
        bac_track: 'sciences_math_a',
      });
    });

    expect(await screen.findByText('Your matches')).toBeInTheDocument();
    expect(await screen.findByText('1337 Coding School')).toBeInTheDocument();
    expect(screen.getByText('87% match')).toBeInTheDocument();
  });

  it('keeps the submit action disabled until the current step has an answer', async () => {
    const user = userEvent.setup();
    await renderWithProviders(<Orientini />);
    await user.click(await screen.findByTestId('orientini-start-quiz'));

    await screen.findByText("What's your Bac track?");
    // The bac-track step itself still requires a pick before "Next" enables
    // (its copy calls the *answer* optional for matching purposes, not the
    // step itself) -- select one, then move to the question step below.
    await user.click(screen.getByText('Sciences Math A'));
    await user.click(screen.getByText('Next'));

    expect(await screen.findByText('What feels most satisfying?')).toBeInTheDocument();
    expect(screen.getByText('See my results').closest('button')).toBeDisabled();

    await user.click(screen.getByText('Understanding deeply why it works'));
    expect(screen.getByText('See my results').closest('button')).not.toBeDisabled();
  });
});
