import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/authStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()

  const [credentials, setCredentials] = useState({
    username_or_email: '',
    password: '',
  })

  const loginMutation = useMutation({
    mutationFn: (data: typeof credentials) =>
      api.auth.login(data.username_or_email, data.password),
    onSuccess: async (data) => {
      setTokens(data.access_token, data.refresh_token)

      // Fetch user info
      try {
        const user = await api.auth.me()
        setUser(user)
        toast.success('Login erfolgreich!')
        navigate('/')
      } catch (error) {
        toast.error('Fehler beim Laden der Benutzerdaten')
      }
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Login fehlgeschlagen')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    loginMutation.mutate(credentials)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Stumpf.works POS</h1>
          <p className="text-gray-600 mt-2">Anmelden um fortzufahren</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="username_or_email"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Benutzername oder E-Mail
            </label>
            <input
              id="username_or_email"
              type="text"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={credentials.username_or_email}
              onChange={(e) =>
                setCredentials({ ...credentials, username_or_email: e.target.value })
              }
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Passwort
            </label>
            <input
              id="password"
              type="password"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={credentials.password}
              onChange={(e) =>
                setCredentials({ ...credentials, password: e.target.value })
              }
            />
          </div>

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 focus:ring-4 focus:ring-primary-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loginMutation.isPending ? 'Anmelden...' : 'Anmelden'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            className="text-primary-600 hover:text-primary-700 font-medium text-sm"
            onClick={() => toast('PIN-Login in Entwicklung', { icon: '🔧' })}
          >
            Mit PIN anmelden
          </button>
        </div>
      </div>
    </div>
  )
}
