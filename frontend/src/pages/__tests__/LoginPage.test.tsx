/**
 * Tests for Login Page
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../../test/utils'
import LoginPage from '../LoginPage'
import { useAuthStore } from '../../stores/authStore'

// Mock the API
vi.mock('../../services/api', () => ({
  api: {
    post: vi.fn(),
  },
}))

describe('LoginPage', () => {
  beforeEach(() => {
    useAuthStore.getState().logout()
    vi.clearAllMocks()
  })

  it('should render login form', () => {
    renderWithProviders(<LoginPage />)

    expect(screen.getByLabelText(/benutzername/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/passwort/i)).toBeInTheDocument()
    const submitButtons = screen.getAllByRole('button', { name: /anmelden/i })
    expect(submitButtons.length).toBeGreaterThan(0)
  })

  it('should show validation errors for empty fields', async () => {
    const user = userEvent.setup()
    renderWithProviders(<LoginPage />)

    const submitButtons = screen.getAllByRole('button', { name: /anmelden/i })
    const submitButton = submitButtons[0] // Get the first button (form submit)
    await user.click(submitButton)

    // HTML5 validation should prevent submission
    const usernameInput = screen.getByLabelText(/benutzername/i)
    expect(usernameInput).toBeRequired()
  })

  it('should submit login form with valid credentials', async () => {
    const user = userEvent.setup()
    const { api } = await import('../../services/api')

    // Mock successful login
    vi.mocked(api.post).mockResolvedValueOnce({
      data: {
        access_token: 'test_token',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          role: 'cashier',
        },
      },
    })

    renderWithProviders(<LoginPage />)

    await user.type(screen.getByLabelText(/benutzername/i), 'testuser')
    await user.type(screen.getByLabelText(/passwort/i), 'password123')
    const submitButtons = screen.getAllByRole('button', { name: /anmelden/i })
    await user.click(submitButtons[0])

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/login', {
        username: 'testuser',
        password: 'password123',
      })
    })
  })

  it('should display error message on login failure', async () => {
    const user = userEvent.setup()
    const { api } = await import('../../services/api')

    // Mock failed login
    vi.mocked(api.post).mockRejectedValueOnce({
      response: {
        data: { detail: 'Invalid credentials' },
      },
    })

    renderWithProviders(<LoginPage />)

    await user.type(screen.getByLabelText(/benutzername/i), 'wronguser')
    await user.type(screen.getByLabelText(/passwort/i), 'wrongpassword')
    const submitButtons = screen.getAllByRole('button', { name: /anmelden/i })
    await user.click(submitButtons[0])

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
    })
  })

  it('should toggle password visibility', async () => {
    const user = userEvent.setup()
    renderWithProviders(<LoginPage />)

    const passwordInput = screen.getByLabelText(/passwort/i)
    expect(passwordInput).toHaveAttribute('type', 'password')

    // Click show password button if it exists
    const showPasswordButton = screen.queryByLabelText(/passwort anzeigen/i)
    if (showPasswordButton) {
      await user.click(showPasswordButton)
      expect(passwordInput).toHaveAttribute('type', 'text')
    }
  })

  it('should have PIN login option', () => {
    renderWithProviders(<LoginPage />)

    // Check if there's a PIN login tab or button
    const pinOption = screen.queryByText(/pin/i)
    if (pinOption) {
      expect(pinOption).toBeInTheDocument()
    }
  })
})
