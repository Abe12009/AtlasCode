import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useTranslation } from '../../hooks/useTranslation';
import { renderWithProviders } from '../../test/setup.tsx';

function TestTranslationComponent() {
  const { t, currentLanguage, changeLanguage, isRTL, languages } = useTranslation();
  
  return (
    <div>
      <span data-testid="welcome">{t('common.welcome')}</span>
      <span data-testid="current-lang">{currentLanguage}</span>
      <span data-testid="is-rtl">{isRTL.toString()}</span>
      <select data-testid="lang-select" value={currentLanguage} onChange={(e) => changeLanguage(e.target.value)}>
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>{lang.nativeName}</option>
        ))}
      </select>
    </div>
  );
}

describe('Internationalization (i18n)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders English by default', async () => {
    await renderWithProviders(<TestTranslationComponent />);
    
    expect(screen.getByTestId('welcome')).toHaveTextContent('Welcome');
    expect(screen.getByTestId('current-lang')).toHaveTextContent('en');
    expect(screen.getByTestId('is-rtl')).toHaveTextContent('false');
  });

  it('switches to French', async () => {
    await renderWithProviders(<TestTranslationComponent />);
    
    await userEvent.selectOptions(screen.getByTestId('lang-select'), 'fr');
    
    await waitFor(() => {
      expect(screen.getByTestId('current-lang')).toHaveTextContent('fr');
      expect(screen.getByTestId('is-rtl')).toHaveTextContent('false');
      expect(screen.getByTestId('welcome')).toHaveTextContent('Bienvenue');
    });
  });

  it('switches to Arabic with RTL', async () => {
    await renderWithProviders(<TestTranslationComponent />);
    
    await userEvent.selectOptions(screen.getByTestId('lang-select'), 'ar');
    
    await waitFor(() => {
      expect(screen.getByTestId('current-lang')).toHaveTextContent('ar');
      expect(screen.getByTestId('is-rtl')).toHaveTextContent('true');
      expect(screen.getByTestId('welcome')).toHaveTextContent('مرحباً');
    });
  });

  it('persists language in localStorage', async () => {
    await renderWithProviders(<TestTranslationComponent />);
    
    await userEvent.selectOptions(screen.getByTestId('lang-select'), 'fr');
    
    await waitFor(() => {
      expect(localStorage.getItem('i18nextLng')).toBe('fr');
    });
  });

  it('loads language from localStorage on mount', async () => {
    localStorage.setItem('i18nextLng', 'ar');
    
    // Need to pass initialLanguage to renderWithProviders for this test
    await renderWithProviders(<TestTranslationComponent />, { initialLanguage: 'ar' });
    
    await waitFor(() => {
      expect(screen.getByTestId('current-lang')).toHaveTextContent('ar');
      expect(screen.getByTestId('is-rtl')).toHaveTextContent('true');
    });
  });

  it('has all three languages available', async () => {
    await renderWithProviders(<TestTranslationComponent />);
    
    const selectElement = screen.getByTestId('lang-select') as HTMLSelectElement;
    const options = selectElement.querySelectorAll('option');
    expect(options).toHaveLength(3);
    expect(options[0]).toHaveValue('en');
    expect(options[1]).toHaveValue('fr');
    expect(options[2]).toHaveValue('ar');
  });
});