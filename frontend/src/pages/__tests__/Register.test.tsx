import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Register } from '../Register';
import { renderWithProviders, mockUser } from '../../test/setup.tsx';
import { authApi } from '../../api/services';

describe('Register Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders registration form with all required fields', async () => {
    await renderWithProviders(<Register />);
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(document.getElementById('password')).toBeInTheDocument();
    expect(document.getElementById('confirmPassword')).toBeInTheDocument();
    expect(screen.getByLabelText(/preferred language/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    await renderWithProviders(<Register />);
    
    const form = screen.getByRole('form');
    await fireEvent.submit(form);
    
    await waitFor(() => {
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it('validates username minimum length', async () => {
    await renderWithProviders(<Register />);
    
    const usernameInput = screen.getByLabelText(/username/i);
    await userEvent.type(usernameInput, 'ab');
    
    const form = screen.getByRole('form');
    fireEvent.submit(form);
    
    await waitFor(() => {
      expect(screen.getByText(/at least 3 characters/i)).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    await renderWithProviders(<Register />);
    
    const emailInput = screen.getByLabelText(/email/i);
    await userEvent.type(emailInput, 'invalid-email');
    
    const form = screen.getByRole('form');
    fireEvent.submit(form);
    
    await waitFor(() => {
      expect(screen.getByText(/valid email address/i)).toBeInTheDocument();
    });
  });

  it('validates password minimum length', async () => {
    await renderWithProviders(<Register />);
    
    const passwordInput = document.getElementById('password');
    await userEvent.type(passwordInput!, 'short');
    
    const form = screen.getByRole('form');
    fireEvent.submit(form);
    
    await waitFor(() => {
      expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it('shows password strength indicator', async () => {
    await renderWithProviders(<Register />);
    
    const passwordInput = document.getElementById('password');
    await userEvent.type(passwordInput!, 'StrongPass123!');
    
    await waitFor(() => {
      expect(screen.getByText(/strong/i)).toBeInTheDocument();
    });
  });

  it('validates password confirmation matches', async () => {
    await renderWithProviders(<Register />);
    
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirmPassword');
    
    await userEvent.type(passwordInput!, 'Password123!');
    await userEvent.type(confirmInput!, 'DifferentPass123!');
    
    const form = screen.getByRole('form');
    fireEvent.submit(form);
    
    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it('successfully registers and redirects', async () => {
    authApi.register.mockResolvedValue({ access_token: 'test-token', token_type: 'bearer' });
    authApi.getMe.mockResolvedValue(mockUser);
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, preferred_language: 'en' });
    
    await renderWithProviders(<Register />);
    
    await userEvent.type(screen.getByLabelText(/username/i), 'newuser');
    await userEvent.type(screen.getByLabelText(/email/i), 'new@example.com');
    await userEvent.type(document.getElementById('password')!, 'Password123!');
    await userEvent.type(document.getElementById('confirmPassword')!, 'Password123!');
    
    await userEvent.selectOptions(screen.getByLabelText(/preferred language/i), 'en');
    
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });
  });

  it('shows error when registration fails', async () => {
    authApi.register.mockRejectedValue({
      response: { data: { detail: 'Email already registered' } },
    });
    
    await renderWithProviders(<Register />);
    
    await userEvent.type(screen.getByLabelText(/username/i), 'existinguser');
    await userEvent.type(screen.getByLabelText(/email/i), 'existing@example.com');
    await userEvent.type(document.getElementById('password')!, 'Password123!');
    await userEvent.type(document.getElementById('confirmPassword')!, 'Password123!');
    
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/email already registered/i)).toBeInTheDocument();
    });
  });

  it('has link to login page', async () => {
    await renderWithProviders(<Register />);
    
    expect(screen.getByRole('link', { name: /sign in/i })).toHaveAttribute('href', '/login');
  });

  it('shows loading state during registration', async () => {
    let resolveRegister: (value: any) => void;
    const registerPromise = new Promise((resolve) => { resolveRegister = resolve; });
    authApi.register.mockReturnValue(registerPromise);
    authApi.getMe.mockResolvedValue(mockUser);
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, preferred_language: 'en' });
    
    await renderWithProviders(<Register />);
    
    await userEvent.type(screen.getByLabelText(/username/i), 'newuser');
    await userEvent.type(screen.getByLabelText(/email/i), 'new@example.com');
    await userEvent.type(document.getElementById('password')!, 'Password123!');
    await userEvent.type(document.getElementById('confirmPassword')!, 'Password123!');
    
    await userEvent.selectOptions(screen.getByLabelText(/preferred language/i), 'en');
    
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    
    // During loading, the button shows "Create Account" with a spinner and is disabled
    expect(screen.getByRole('button', { name: /create account/i })).toBeDisabled();
    expect(screen.getByText(/create account/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toHaveAttribute('disabled', '');
    
    resolveRegister!({ access_token: 'test-token', token_type: 'bearer' });
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });
  });
});