import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'

// Pages
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import POSPage from '@/pages/POSPage'

// Admin Layout and Pages
import AdminLayout from '@/layouts/AdminLayout'
import AdminDashboardPage from '@/pages/admin/DashboardPage'
import UsersPage from '@/pages/admin/UsersPage'
import ReportsPage from '@/pages/admin/ReportsPage'
import ExportsPage from '@/pages/admin/ExportsPage'
import PluginsPage from '@/pages/admin/PluginsPage'
import SettingsPage from '@/pages/admin/SettingsPage'

// Super Admin Pages
import PluginLicensesPage from '@/pages/super-admin/PluginLicensesPage'

function App() {
  const { isAuthenticated, user } = useAuthStore()

  const isAdmin = user?.role === 'admin' || user?.role === 'super_admin'
  const isSuperAdmin = user?.role === 'super_admin'

  return (
    <>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes */}
        <Route
          path="/"
          element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" />}
        />
        <Route
          path="/pos"
          element={isAuthenticated ? <POSPage /> : <Navigate to="/login" />}
        />

        {/* Admin routes */}
        <Route
          path="/admin"
          element={
            isAuthenticated ? (
              isAdmin ? (
                <AdminLayout />
              ) : (
                <Navigate to="/" />
              )
            ) : (
              <Navigate to="/login" />
            )
          }
        >
          <Route index element={<AdminDashboardPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="products" element={<Navigate to="/admin" />} />
          <Route path="transactions" element={<Navigate to="/admin" />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="exports" element={<ExportsPage />} />
          <Route path="plugins" element={<PluginsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Super Admin routes */}
        <Route
          path="/super-admin"
          element={
            isAuthenticated ? (
              isSuperAdmin ? (
                <AdminLayout />
              ) : (
                <Navigate to="/" />
              )
            ) : (
              <Navigate to="/login" />
            )
          }
        >
          <Route path="plugin-licenses" element={<PluginLicensesPage />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>

      {/* Global toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </>
  )
}

export default App
