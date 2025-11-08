import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  username: string
  first_name?: string
  last_name?: string
  role: string
  tenant_id: string
}

interface AuthState {
  user: User | null
  token: string | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean

  // Actions
  login: (user: User, token: string) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  setUser: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (user, token) => {
        set({
          user,
          token,
          accessToken: token,
          isAuthenticated: true,
        })
        localStorage.setItem('pos_token', token)
      },

      setTokens: (accessToken, refreshToken) =>
        set({
          accessToken,
          refreshToken,
          token: accessToken,
          isAuthenticated: true,
        }),

      setUser: (user) =>
        set({
          user,
          isAuthenticated: true,
        }),

      logout: () => {
        set({
          user: null,
          token: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
        localStorage.removeItem('pos_token')
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
