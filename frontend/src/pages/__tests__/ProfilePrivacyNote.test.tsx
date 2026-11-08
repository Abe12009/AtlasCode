import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Profile } from '../Profile';
import { renderWithProviders, mockUser, mockProfile } from '../../test/setup.tsx';
import { authApi, dashboardApi } from '../../api/services';

const mockedAuth = vi.mocked(authApi);
const mockedDashboard = vi.mocked(dashboardApi);

/**
 * The profile-visibility switch has a consequence its own radio labels do
 * not mention: "Public" also lists the account on the leaderboard. The note
 * lives next to the switch, because that is where the decision is made --
 * saying it only on the leaderboard page tells people after the fact.
 */
async function openSettings(language = 'en') {
  const result = await renderWithProviders(<Profile />, {
    initialLanguage: language,
    authToken: 'a-token',
  });
  const tab = await screen.findByRole('button', { name: /settings|paramètres|الإعدادات/i });
  await userEvent.click(tab);
  return result;
}

describe('Profile privacy note about the leaderboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockedAuth.getMe.mockResolvedValue({ ...mockUser, profile_visibility: 'private' } as any);
    mockedAuth.getProfile.mockResolvedValue(mockProfile as any);
    mockedDashboard.get.mockResolvedValue({
      profile: mockProfile,
      course_progress: [],
      recent_achievements: [],
    } as any);
  });

  it('names what a public profile reveals, beside the switch', async () => {
    await openSettings();

    const note = await screen.findByTestId('privacy-leaderboard-note');
    expect(note).toHaveTextContent(/also listed on the leaderboard/i);
    // The four fields the leaderboard actually shows -- the same set its own
    // join control names.
    expect(note).toHaveTextContent(/username, avatar, level and XP/i);
  });

  it('links to the leaderboard', async () => {
    await openSettings();

    const note = await screen.findByTestId('privacy-leaderboard-note');
    const link = within(note).getByRole('link');
    expect(link).toHaveAttribute('href', '/app/leaderboard');
    expect(link).toHaveTextContent(/view the leaderboard/i);
  });

  it('sits in the same card as the public/private radios', async () => {
    await openSettings();

    const note = await screen.findByTestId('privacy-leaderboard-note');
    const card = note.closest('div')?.parentElement;
    expect(card?.textContent).toMatch(/Public — visible to other users/);
    expect(card?.textContent).toMatch(/Private — only visible to you/);
  });

  const translated: Record<string, RegExp> = {
    fr: /également affiché dans le classement/i,
    ar: /يظهر أيضًا في قائمة المتصدرين/,
  };

  for (const [language, pattern] of Object.entries(translated)) {
    it(`is translated in ${language}`, async () => {
      await openSettings(language);

      // A bare findBy, not a findBy nested inside waitFor: the nested form
      // retries a retry, and under a loaded parallel run its inner 1s budget
      // can expire inside the outer one. That shape failed once in a full
      // suite run and passed on its own, which is the signature.
      expect(await screen.findByTestId('privacy-leaderboard-note')).toHaveTextContent(pattern);
      // No raw i18n key leaked.
      expect(document.body.textContent).not.toMatch(/settings\.privacy_leaderboard/);
    });
  }
});
