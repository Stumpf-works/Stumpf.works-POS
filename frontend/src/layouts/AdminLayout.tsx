/**
 * Admin Layout
 * Layout wrapper for admin pages with navigation sidebar
 */

import { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

interface NavItem {
  path: string
  label: string
  icon: string
  requiredRole?: string[]
}

const navItems: NavItem[] = [
  { path: '/admin', label: 'Dashboard', icon: '📊' },
  { path: '/admin/users', label: 'Benutzer', icon: '👥', requiredRole: ['admin'] },
  { path: '/admin/products', label: 'Produkte', icon: '📦' },
  { path: '/admin/transactions', label: 'Transaktionen', icon: '💳' },
  { path: '/admin/reports', label: 'Berichte', icon: '📈' },
  { path: '/admin/exports', label: 'Exporte', icon: '📤', requiredRole: ['admin'] },
  { path: '/admin/settings', label: 'Einstellungen', icon: '⚙️', requiredRole: ['admin'] },
]

export default function AdminLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const canAccessItem = (item: NavItem) => {
    if (!item.requiredRole) return true
    return item.requiredRole.includes(user?.role || '')
  }

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className={`admin-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h1 className="sidebar-title">Stumpf.works POS</h1>
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <ul>
            {navItems
              .filter(canAccessItem)
              .map((item) => (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`nav-item ${
                      location.pathname === item.path ? 'active' : ''
                    }`}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    {sidebarOpen && <span className="nav-label">{item.label}</span>}
                  </Link>
                </li>
              ))}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            {sidebarOpen && (
              <>
                <div className="user-name">{user?.username}</div>
                <div className="user-role">{user?.role}</div>
              </>
            )}
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            🚪 {sidebarOpen && 'Abmelden'}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="admin-content">
        <Outlet />
      </main>

      <style>{`
        .admin-layout {
          display: flex;
          min-height: 100vh;
          background: #f5f5f5;
        }

        .admin-sidebar {
          background: #1a1a2e;
          color: white;
          transition: width 0.3s ease;
          display: flex;
          flex-direction: column;
          position: sticky;
          top: 0;
          height: 100vh;
          overflow-y: auto;
        }

        .admin-sidebar.open {
          width: 250px;
        }

        .admin-sidebar.closed {
          width: 70px;
        }

        .sidebar-header {
          padding: 1.5rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .sidebar-title {
          font-size: 1.2rem;
          font-weight: 600;
          margin: 0;
          white-space: nowrap;
          overflow: hidden;
        }

        .sidebar-toggle {
          background: none;
          border: none;
          color: white;
          font-size: 1.2rem;
          cursor: pointer;
          padding: 0.5rem;
        }

        .sidebar-nav {
          flex: 1;
          padding: 1rem 0;
        }

        .sidebar-nav ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem 1.5rem;
          color: rgba(255, 255, 255, 0.7);
          text-decoration: none;
          transition: all 0.2s;
          cursor: pointer;
        }

        .nav-item:hover {
          background: rgba(255, 255, 255, 0.05);
          color: white;
        }

        .nav-item.active {
          background: rgba(16, 185, 129, 0.2);
          color: #10b981;
          border-left: 3px solid #10b981;
        }

        .nav-icon {
          font-size: 1.5rem;
          min-width: 1.5rem;
          text-align: center;
        }

        .nav-label {
          white-space: nowrap;
        }

        .sidebar-footer {
          padding: 1.5rem;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .user-info {
          margin-bottom: 1rem;
        }

        .user-name {
          font-weight: 600;
          margin-bottom: 0.25rem;
        }

        .user-role {
          font-size: 0.875rem;
          color: rgba(255, 255, 255, 0.6);
          text-transform: uppercase;
        }

        .logout-btn {
          width: 100%;
          padding: 0.75rem;
          background: rgba(239, 68, 68, 0.2);
          border: 1px solid rgba(239, 68, 68, 0.4);
          color: #f87171;
          border-radius: 0.375rem;
          cursor: pointer;
          font-size: 1rem;
          transition: all 0.2s;
        }

        .logout-btn:hover {
          background: rgba(239, 68, 68, 0.3);
        }

        .admin-content {
          flex: 1;
          padding: 2rem;
          overflow-y: auto;
        }

        @media (max-width: 768px) {
          .admin-sidebar.open {
            position: fixed;
            z-index: 100;
            box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
          }
        }
      `}</style>
    </div>
  )
}
