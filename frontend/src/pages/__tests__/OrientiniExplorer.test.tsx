import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { OrientiniExplorer } from '../OrientiniExplorer';
import { renderWithProviders } from '../../test/setup.tsx';
import { orientiniApi } from '../../api/services';
import type { Institution } from '../../types';

const mockedApi = vi.mocked(orientiniApi);

const UNVERIFIED: Institution = {
  id: 1,
  slug: '1337',
  type: 'code_school',
  order: 1,
  icon: '🧩',
  translations: [{ language: 'en', name: '1337 Coding School', description: 'Peer-to-peer coding school.', career_outcomes: 'Software development roles.' }],
  requirement: {
    eligible_bac_tracks: null,
    min_bac_average: null,
    entrance_exam_name: null,
    entrance_exam_format: null,
    application_window: null,
    data_verified: false,
    verification_notes: 'Not confirmed yet.',
  },
};

const VERIFIED: Institution = {
  id: 2,
  slug: 'cpge',
  type: 'cpge',
  order: 2,
  icon: '📐',
  translations: [{ language: 'en', name: 'CPGE', description: 'Prep classes.', career_outcomes: null }],
  requirement: {
    eligible_bac_tracks: ['sciences_math_a', 'pc'],
    min_bac_average: 16.5,
    entrance_exam_name: 'Concours National Commun',
    entrance_exam_format: null,
    application_window: 'June',
    data_verified: true,
    verification_notes: null,
  },
};

describe('OrientiniExplorer page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders every institution with its name and requirements', async () => {
    mockedApi.getInstitutions.mockResolvedValue([UNVERIFIED, VERIFIED]);
    await renderWithProviders(<OrientiniExplorer />);

    expect(await screen.findByText('1337 Coding School')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'CPGE' })).toBeInTheDocument();
  });

  it('shows a needs-verification badge for an institution with data_verified=false, and no fabricated numbers', async () => {
    mockedApi.getInstitutions.mockResolvedValue([UNVERIFIED]);
    await renderWithProviders(<OrientiniExplorer />);

    await screen.findByText('1337 Coding School');
    expect(screen.getByText('Needs verification')).toBeInTheDocument();
    expect(screen.getByText(/haven't been confirmed yet/)).toBeInTheDocument();
    // The unverified branch must not also render the structured requirement
    // fields -- those would present placeholder/absent data as real facts.
    expect(screen.queryByText('Minimum Bac average')).not.toBeInTheDocument();
  });

  it('shows the real requirement figures once data_verified=true, with no verification badge', async () => {
    mockedApi.getInstitutions.mockResolvedValue([VERIFIED]);
    await renderWithProviders(<OrientiniExplorer />);

    await screen.findByRole('heading', { name: 'CPGE' });
    expect(screen.queryByText('Needs verification')).not.toBeInTheDocument();
    expect(screen.getByText('16.5')).toBeInTheDocument();
    expect(screen.getByText('Concours National Commun')).toBeInTheDocument();
    expect(screen.getByText('Sciences Math A, PC (Physique-Chimie)')).toBeInTheDocument();
  });

  it('shows a loading state before institutions arrive', async () => {
    mockedApi.getInstitutions.mockImplementation(() => new Promise(() => {}));
    await renderWithProviders(<OrientiniExplorer />);
    expect(screen.getByText('Institution Explorer')).toBeInTheDocument();
    expect(screen.queryByText('1337 Coding School')).not.toBeInTheDocument();
  });
});
