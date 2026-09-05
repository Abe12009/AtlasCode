import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useAuth } from '../AuthContext'
import { renderWithProviders } from '../../test/setup.tsx'
import { authApi } from '../../api/services'

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('provides login function', async () => {
    authApi.login.mockResolvedValue({ access_token: 'test-token', token_type: 'bearer' })
    authApi.getMe.mockResolvedValue({ id: 1, email: 'test@example.com', username: 'testuser', preferred_language: 'en', is_active: true, created_at: new Date().toISOString() })
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, completed_lessons: 0, completed_projects: 0, level: 1 })

    function TestComponent() {
      const { login } = useAuth()
      return <button onClick={() => login('test@example.com', 'password')}>Login</button>
    }

    await renderWithProviders(<TestComponent />)

    await userEvent.click(screen.getByText('Login'))

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('test-token')
    })
  })

  it('provides logout function', async () => {
    authApi.getMe.mockResolvedValue({ id: 1, email: 'test@example.com', username: 'testuser', preferred_language: 'en', is_active: true, created_at: new Date().toISOString() })
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, completed_lessons: 0, completed_projects: 0, level: 1 })
    
    localStorage.setItem('access_token', 'test-token')

    let logoutFn: () => void

    function TestComponent() {
      const { logout } = useAuth()
      logoutFn = logout
      return <button onClick={logout}>Logout</button>
    }

    await renderWithProviders(<TestComponent />)

    // Call logout directly
    logoutFn!()

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBeNull()
    })
  })

  it('provides register function', async () => {
    authApi.register.mockResolvedValue({ access_token: 'test-token', token_type: 'bearer' })
    authApi.getMe.mockResolvedValue({ id: 1, email: 'test@example.com', username: 'testuser', preferred_language: 'en', is_active: true, created_at: new Date().toISOString() })
    authApi.getProfile.mockResolvedValue({ user_id: 1, xp: 0, streak: 0, completed_lessons: 0, completed_projects: 0, level: 1 })

    function TestComponent() {
      const { register } = useAuth()
      return <button onClick={() => register({ email: 'test@example.com', username: 'testuser', password: 'password123', preferred_language: 'en' })}>Register</button>
    }

    await renderWithProviders(<TestComponent />)

    await userEvent.click(screen.getByText('Register'))

    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('test-token')
    })
  })
})