import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Stumpf.works POS</h1>
            <p className="text-sm text-gray-600">
              Willkommen, {user?.first_name || user?.username}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Abmelden
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* POS Card */}
          <div
            onClick={() => navigate('/pos')}
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Kasse (POS)</h2>
                <p className="text-gray-600 mt-2">Verkäufe erfassen</p>
              </div>
              <div className="text-4xl">🛒</div>
            </div>
          </div>

          {/* Products Card */}
          <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Produkte</h2>
                <p className="text-gray-600 mt-2">Produktverwaltung</p>
              </div>
              <div className="text-4xl">📦</div>
            </div>
          </div>

          {/* Reports Card */}
          <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Berichte</h2>
                <p className="text-gray-600 mt-2">Umsätze & Statistiken</p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>

          {/* Transactions Card */}
          <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Transaktionen</h2>
                <p className="text-gray-600 mt-2">Verkaufshistorie</p>
              </div>
              <div className="text-4xl">🧾</div>
            </div>
          </div>

          {/* Settings Card */}
          <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Einstellungen</h2>
                <p className="text-gray-600 mt-2">Systemkonfiguration</p>
              </div>
              <div className="text-4xl">⚙️</div>
            </div>
          </div>

          {/* Users Card */}
          {user?.role === 'tenant_admin' && (
            <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Benutzer</h2>
                  <p className="text-gray-600 mt-2">Benutzerverwaltung</p>
                </div>
                <div className="text-4xl">👥</div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Übersicht</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">-</p>
              <p className="text-gray-600 mt-1">Heute Umsatz</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">-</p>
              <p className="text-gray-600 mt-1">Transaktionen</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">-</p>
              <p className="text-gray-600 mt-1">Produkte</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">-</p>
              <p className="text-gray-600 mt-1">Niedrig im Bestand</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
