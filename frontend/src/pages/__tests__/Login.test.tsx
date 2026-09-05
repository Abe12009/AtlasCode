import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Login } from '../Login';
import { renderWithProviders, mockUser } from '../../test/setup.tsx';
import { authApi } from '../../api/services';

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders login form with email and password fields', async () => {
    await renderWithProviders(<Login />);
    
    expect(screen.getByText(/^Email/i)).toBeInTheDocument();
    expect(screen.getByText(/^Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('submits form and calls API with correct data', async () => {
    let loginResolve: (value: any) => void;
    const loginPromise = new Promise((resolve) => { loginResolve = resolve; });
    authApi.login.mockReturnValue(loginPromise);
    authApi.getMe.mockResolvedValue(mockUser);
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, preferred_language: 'en' });
    
    await renderWithProviders(<Login />);
    
    const emailInput = screen.getByLabelText(/^Email/i);
    const passwordInput = screen.getByLabelText(/^Password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);
    
    // Verify API was called with correct data
    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password123' });
    });
    
    // Resolve to complete login
    loginResolve!({ access_token: 'test-token', token_type: 'bearer' });
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });
  });

  it('shows error when login fails', async () => {
    authApi.login.mockRejectedValue({
      response: { data: { detail: 'Incorrect email or password' } },
    });
    
    await renderWithProviders(<Login />);
    
    const emailInput = screen.getByLabelText(/^Email/i);
    const passwordInput = screen.getByLabelText(/^Password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'wrongpassword');
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      const alerts = screen.getAllByRole('alert');
      expect(alerts.length).toBeGreaterThan(0);
      expect(alerts[0]).toHaveTextContent(/incorrect email or password/i);
    });
  });

  it('successfully logs in and redirects', async () => {
    authApi.login.mockResolvedValue({ access_token: 'test-token', token_type: 'bearer' });
    authApi.getMe.mockResolvedValue(mockUser);
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, preferred_language: 'en' });
    
    await renderWithProviders(<Login />);
    
    const emailInput = screen.getByLabelText(/^Email/i);
    const passwordInput = screen.getByLabelText(/^Password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });
  });

  it('toggles password visibility', async () => {
    await renderWithProviders(<Login />);
    
    const passwordInput = screen.getByLabelText(/^Password/i);
    const toggleButton = screen.getByLabelText(/toggle password/i);
    
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    await userEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    await userEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('has link to register page', async () => {
    await renderWithProviders(<Login />);
    
    expect(screen.getByRole('link', { name: /sign up/i })).toHaveAttribute('href', '/register');
  });

  it('shows loading state during login', async () => {
    let resolveLogin: (value: any) => void;
    const loginPromise = new Promise((resolve) => { resolveLogin = resolve; });
    authApi.login.mockReturnValue(loginPromise);
    authApi.getMe.mockResolvedValue(mockUser);
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, preferred_language: 'en' });
    
    await renderWithProviders(<Login />);
    
    const emailInput = screen.getByLabelText(/^Email/i);
    const passwordInput = screen.getByLabelText(/^Password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    
    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    
    fireEvent.click(submitButton);
    
    // Check for loading state - button should be disabled and show Sign In with spinner
    expect(submitButton).toBeDisabled();
    
    resolveLogin!({ access_token: 'test-token', token_type: 'bearer' });
    
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('test-token');
    });
  });
});