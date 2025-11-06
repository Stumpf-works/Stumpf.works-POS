/**
 * Tests for Auth Store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthStore } from '../authStore'

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = useAuthStore.getState()
    store.logout()
    localStorage.clear()
  })

  it('should initialize with no user', () => {
    const { user, isAuthenticated } = useAuthStore.getState()
    expect(user).toBeNull()
    expect(isAuthenticated).toBe(false)
  })

  it('should set user on login', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'cashier',
      tenant_id: 'test_tenant',
    }

    const mockToken = 'test_token_123'

    useAuthStore.getState().login(mockUser, mockToken)

    const { user, token, isAuthenticated } = useAuthStore.getState()
    expect(user).toEqual(mockUser)
    expect(token).toBe(mockToken)
    expect(isAuthenticated).toBe(true)
  })

  it('should persist token to localStorage on login', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'cashier',
      tenant_id: 'test_tenant',
    }

    const mockToken = 'test_token_123'

    useAuthStore.getState().login(mockUser, mockToken)

    expect(localStorage.getItem('pos_token')).toBe(mockToken)
  })

  it('should clear user on logout', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'cashier',
      tenant_id: 'test_tenant',
    }

    useAuthStore.getState().login(mockUser, 'test_token')
    useAuthStore.getState().logout()

    const { user, token, isAuthenticated } = useAuthStore.getState()
    expect(user).toBeNull()
    expect(token).toBeNull()
    expect(isAuthenticated).toBe(false)
  })

  it('should clear localStorage on logout', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'cashier',
      tenant_id: 'test_tenant',
    }

    useAuthStore.getState().login(mockUser, 'test_token')
    useAuthStore.getState().logout()

    expect(localStorage.getItem('pos_token')).toBeNull()
  })

  it('should identify admin users correctly', () => {
    const adminUser = {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      role: 'admin',
      tenant_id: 'test_tenant',
    }

    useAuthStore.getState().login(adminUser, 'test_token')

    const { user } = useAuthStore.getState()
    expect(user?.role).toBe('admin')
  })

  it('should identify cashier users correctly', () => {
    const cashierUser = {
      id: 1,
      username: 'cashier',
      email: 'cashier@example.com',
      role: 'cashier',
      tenant_id: 'test_tenant',
    }

    useAuthStore.getState().login(cashierUser, 'test_token')

    const { user } = useAuthStore.getState()
    expect(user?.role).toBe('cashier')
  })
})
