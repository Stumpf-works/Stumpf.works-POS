/**
 * Super Admin - Plugin License Management
 * Manage plugin licenses for all tenants
 * Only accessible by SUPER_ADMIN role
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../services/api'

interface PluginLicense {
  id: number
  tenant_id: string
  tenant_name: string
  plugin_name: string
  plugin_display_name: string
  is_active: boolean
  is_valid: boolean
  license_type: string
  valid_from: string
  valid_until: string | null
  days_remaining: number | null
  max_users: number | null
  max_locations: number | null
  notes: string | null
  granted_at: string
  created_at: string
}

interface TenantWithLicenses {
  tenant_id: string
  tenant_name: string
  active_licenses: number
  total_licenses: number
  plugins: string[]
}

interface GrantLicenseForm {
  tenant_id: string
  plugin_name: string
  license_type: string
  valid_days: number | null
  max_users: number | null
  max_locations: number | null
  notes: string
}

export default function PluginLicensesPage() {
  const queryClient = useQueryClient()
  const [view, setView] = useState<'licenses' | 'tenants'>('tenants')
  const [showGrantModal, setShowGrantModal] = useState(false)
  const [, setSelectedLicense] = useState<PluginLicense | null>(null)
  const [filterTenant, setFilterTenant] = useState('')
  const [filterPlugin, setFilterPlugin] = useState('')

  const [grantForm, setGrantForm] = useState<GrantLicenseForm>({
    tenant_id: '',
    plugin_name: '',
    license_type: 'standard',
    valid_days: null,
    max_users: null,
    max_locations: null,
    notes: '',
  })

  // Fetch tenants with licenses
  const { data: tenants = [] } = useQuery<TenantWithLicenses[]>({
    queryKey: ['super-admin-tenants'],
    queryFn: async () => {
      const response = await api.get('/super-admin/plugin-licenses/tenants')
      return response.data
    },
  })

  // Fetch all licenses
  const { data: licenses = [] } = useQuery<PluginLicense[]>({
    queryKey: ['super-admin-licenses', filterTenant, filterPlugin],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filterTenant) params.append('tenant_id', filterTenant)
      if (filterPlugin) params.append('plugin_name', filterPlugin)

      const response = await api.get(`/super-admin/plugin-licenses?${params}`)
      return response.data
    },
  })

  // Grant license mutation
  const grantLicenseMutation = useMutation({
    mutationFn: async (data: GrantLicenseForm) => {
      const response = await api.post('/super-admin/plugin-licenses', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['super-admin-licenses'] })
      queryClient.invalidateQueries({ queryKey: ['super-admin-tenants'] })
      setShowGrantModal(false)
      resetGrantForm()
    },
  })

  // Update license mutation
  const updateLicenseMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Record<string, unknown> }) => {
      const response = await api.patch(`/super-admin/plugin-licenses/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['super-admin-licenses'] })
      queryClient.invalidateQueries({ queryKey: ['super-admin-tenants'] })
      setSelectedLicense(null)
    },
  })

  // Revoke license mutation
  const revokeLicenseMutation = useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/super-admin/plugin-licenses/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['super-admin-licenses'] })
      queryClient.invalidateQueries({ queryKey: ['super-admin-tenants'] })
    },
  })

  // Extend license mutation
  const extendLicenseMutation = useMutation({
    mutationFn: async ({ id, days }: { id: number; days: number }) => {
      const response = await api.post(`/super-admin/plugin-licenses/${id}/extend`, null, {
        params: { days },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['super-admin-licenses'] })
    },
  })

  const resetGrantForm = () => {
    setGrantForm({
      tenant_id: '',
      plugin_name: '',
      license_type: 'standard',
      valid_days: null,
      max_users: null,
      max_locations: null,
      notes: '',
    })
  }

  const handleGrantLicense = () => {
    grantLicenseMutation.mutate(grantForm)
  }

  const handleRevokeLicense = (license: PluginLicense) => {
    if (
      confirm(
        `Lizenz für "${license.plugin_display_name}" von "${license.tenant_name}" widerrufen?\n\nDas Plugin wird automatisch deaktiviert.`
      )
    ) {
      revokeLicenseMutation.mutate(license.id)
    }
  }

  const handleExtendLicense = (license: PluginLicense) => {
    const days = prompt('Lizenz um wie viele Tage verlängern?', '30')
    if (days) {
      extendLicenseMutation.mutate({
        id: license.id,
        days: parseInt(days, 10),
      })
    }
  }

  const handleToggleActive = (license: PluginLicense) => {
    updateLicenseMutation.mutate({
      id: license.id,
      data: { is_active: !license.is_active },
    })
  }

  const getLicenseTypeBadge = (type: string) => {
    const badges: Record<string, { label: string; className: string }> = {
      trial: { label: 'Trial', className: 'badge-warning' },
      standard: { label: 'Standard', className: 'badge-success' },
      enterprise: { label: 'Enterprise', className: 'badge-premium' },
    }
    const badge = badges[type] || { label: type, className: 'badge-info' }
    return <span className={`badge ${badge.className}`}>{badge.label}</span>
  }

  return (
    <div className="plugin-licenses-page">
      <header className="page-header">
        <div>
          <h1>🔐 Plugin-Lizenzverwaltung</h1>
          <p className="subtitle">Super Admin - Lizenzen für alle Tenants verwalten</p>
        </div>
        <button
          className="button button-primary"
          onClick={() => setShowGrantModal(true)}
        >
          + Neue Lizenz
        </button>
      </header>

      {/* View Tabs */}
      <div className="view-tabs">
        <button
          className={`tab ${view === 'tenants' ? 'active' : ''}`}
          onClick={() => setView('tenants')}
        >
          🏢 Tenants ({tenants.length})
        </button>
        <button
          className={`tab ${view === 'licenses' ? 'active' : ''}`}
          onClick={() => setView('licenses')}
        >
          📜 Alle Lizenzen ({licenses.length})
        </button>
      </div>

      {/* Tenants View */}
      {view === 'tenants' && (
        <div className="tenants-grid">
          {tenants.map((tenant) => (
            <div key={tenant.tenant_id} className="tenant-card">
              <div className="tenant-header">
                <h3>{tenant.tenant_name}</h3>
                <span className="tenant-id">{tenant.tenant_id}</span>
              </div>
              <div className="tenant-stats">
                <div className="stat">
                  <span className="stat-value">{tenant.active_licenses}</span>
                  <span className="stat-label">Aktive Lizenzen</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{tenant.total_licenses}</span>
                  <span className="stat-label">Gesamt</span>
                </div>
              </div>
              {tenant.plugins.length > 0 && (
                <div className="tenant-plugins">
                  <strong>Plugins:</strong>
                  <div className="plugin-tags">
                    {tenant.plugins.map((plugin) => (
                      <span key={plugin} className="plugin-tag">
                        {plugin}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <button
                className="button button-secondary"
                onClick={() => {
                  setFilterTenant(tenant.tenant_id)
                  setView('licenses')
                }}
              >
                Lizenzen anzeigen
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Licenses View */}
      {view === 'licenses' && (
        <>
          {/* Filters */}
          <div className="filters">
            <input
              type="text"
              placeholder="Filter nach Tenant..."
              value={filterTenant}
              onChange={(e) => setFilterTenant(e.target.value)}
              className="filter-input"
            />
            <input
              type="text"
              placeholder="Filter nach Plugin..."
              value={filterPlugin}
              onChange={(e) => setFilterPlugin(e.target.value)}
              className="filter-input"
            />
            {(filterTenant || filterPlugin) && (
              <button
                className="button button-secondary"
                onClick={() => {
                  setFilterTenant('')
                  setFilterPlugin('')
                }}
              >
                Filter löschen
              </button>
            )}
          </div>

          {/* Licenses Table */}
          <div className="licenses-table-container">
            <table className="licenses-table">
              <thead>
                <tr>
                  <th>Tenant</th>
                  <th>Plugin</th>
                  <th>Typ</th>
                  <th>Status</th>
                  <th>Gültig bis</th>
                  <th>Tage</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {licenses.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty-row">
                      Keine Lizenzen gefunden
                    </td>
                  </tr>
                ) : (
                  licenses.map((license) => (
                    <tr key={license.id} className={!license.is_active ? 'inactive' : ''}>
                      <td>
                        <div className="tenant-cell">
                          <strong>{license.tenant_name}</strong>
                          <span className="tenant-id-small">{license.tenant_id}</span>
                        </div>
                      </td>
                      <td>{license.plugin_display_name}</td>
                      <td>{getLicenseTypeBadge(license.license_type)}</td>
                      <td>
                        {license.is_valid ? (
                          <span className="badge badge-success">Gültig</span>
                        ) : (
                          <span className="badge badge-error">Abgelaufen</span>
                        )}
                        {!license.is_active && (
                          <span className="badge badge-disabled">Deaktiviert</span>
                        )}
                      </td>
                      <td>
                        {license.valid_until
                          ? new Date(license.valid_until).toLocaleDateString('de-DE')
                          : 'Unbegrenzt'}
                      </td>
                      <td>
                        {license.days_remaining !== null ? (
                          <span
                            className={
                              license.days_remaining <= 7
                                ? 'days-warning'
                                : license.days_remaining <= 30
                                ? 'days-caution'
                                : ''
                            }
                          >
                            {license.days_remaining}
                          </span>
                        ) : (
                          '∞'
                        )}
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button
                            className="btn-icon"
                            onClick={() => handleToggleActive(license)}
                            title={license.is_active ? 'Deaktivieren' : 'Aktivieren'}
                          >
                            {license.is_active ? '⏸️' : '▶️'}
                          </button>
                          <button
                            className="btn-icon"
                            onClick={() => handleExtendLicense(license)}
                            title="Verlängern"
                          >
                            ⏱️
                          </button>
                          <button
                            className="btn-icon btn-danger"
                            onClick={() => handleRevokeLicense(license)}
                            title="Widerrufen"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Grant License Modal */}
      {showGrantModal && (
        <div className="modal-overlay" onClick={() => setShowGrantModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Neue Lizenz vergeben</h2>
              <button
                className="modal-close"
                onClick={() => setShowGrantModal(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="tenant_id">Tenant ID *</label>
                <input
                  type="text"
                  id="tenant_id"
                  value={grantForm.tenant_id}
                  onChange={(e) =>
                    setGrantForm({ ...grantForm, tenant_id: e.target.value })
                  }
                  className="form-control"
                  placeholder="z.B. restaurant_mueller"
                />
              </div>

              <div className="form-group">
                <label htmlFor="plugin_name">Plugin Name *</label>
                <input
                  type="text"
                  id="plugin_name"
                  value={grantForm.plugin_name}
                  onChange={(e) =>
                    setGrantForm({ ...grantForm, plugin_name: e.target.value })
                  }
                  className="form-control"
                  placeholder="z.B. table_management"
                />
              </div>

              <div className="form-group">
                <label htmlFor="license_type">Lizenz-Typ *</label>
                <select
                  id="license_type"
                  value={grantForm.license_type}
                  onChange={(e) =>
                    setGrantForm({ ...grantForm, license_type: e.target.value })
                  }
                  className="form-control"
                >
                  <option value="trial">Trial</option>
                  <option value="standard">Standard</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="valid_days">Gültigkeitsdauer (Tage)</label>
                <input
                  type="number"
                  id="valid_days"
                  value={grantForm.valid_days || ''}
                  onChange={(e) =>
                    setGrantForm({
                      ...grantForm,
                      valid_days: e.target.value ? parseInt(e.target.value, 10) : null,
                    })
                  }
                  className="form-control"
                  placeholder="Leer = Unbegrenzt"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="max_users">Max. Benutzer</label>
                  <input
                    type="number"
                    id="max_users"
                    value={grantForm.max_users || ''}
                    onChange={(e) =>
                      setGrantForm({
                        ...grantForm,
                        max_users: e.target.value ? parseInt(e.target.value, 10) : null,
                      })
                    }
                    className="form-control"
                    placeholder="Unbegrenzt"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="max_locations">Max. Standorte</label>
                  <input
                    type="number"
                    id="max_locations"
                    value={grantForm.max_locations || ''}
                    onChange={(e) =>
                      setGrantForm({
                        ...grantForm,
                        max_locations: e.target.value ? parseInt(e.target.value, 10) : null,
                      })
                    }
                    className="form-control"
                    placeholder="Unbegrenzt"
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="notes">Notizen</label>
                <textarea
                  id="notes"
                  value={grantForm.notes}
                  onChange={(e) =>
                    setGrantForm({ ...grantForm, notes: e.target.value })
                  }
                  className="form-control"
                  rows={3}
                  placeholder="z.B. Jahres-Vertrag, Kontakt: ..."
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="button button-secondary"
                onClick={() => setShowGrantModal(false)}
              >
                Abbrechen
              </button>
              <button
                className="button button-primary"
                onClick={handleGrantLicense}
                disabled={
                  !grantForm.tenant_id ||
                  !grantForm.plugin_name ||
                  grantLicenseMutation.isPending
                }
              >
                {grantLicenseMutation.isPending ? 'Speichere...' : 'Lizenz vergeben'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        /* ... (similar styles to PluginsPage, adapted for tables and super admin view) ... */

        .plugin-licenses-page {
          padding: 2rem;
          max-width: 1600px;
          margin: 0 auto;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 2rem;
        }

        .page-header h1 {
          font-size: 2rem;
          margin-bottom: 0.5rem;
        }

        .subtitle {
          color: #666;
        }

        .view-tabs {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 2rem;
          border-bottom: 2px solid #e0e0e0;
        }

        .tab {
          padding: 1rem 1.5rem;
          border: none;
          background: none;
          border-bottom: 3px solid transparent;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s;
        }

        .tab:hover {
          background: #f8f9fa;
        }

        .tab.active {
          border-bottom-color: #007bff;
          color: #007bff;
        }

        .tenants-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .tenant-card {
          border: 2px solid #e0e0e0;
          border-radius: 12px;
          padding: 1.5rem;
          background: white;
        }

        .tenant-header h3 {
          margin: 0 0 0.5rem 0;
        }

        .tenant-id {
          color: #666;
          font-size: 0.875rem;
          font-family: monospace;
        }

        .tenant-stats {
          display: flex;
          gap: 2rem;
          margin: 1rem 0;
          padding: 1rem 0;
          border-top: 1px solid #e0e0e0;
          border-bottom: 1px solid #e0e0e0;
        }

        .stat {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .stat-value {
          font-size: 2rem;
          font-weight: 700;
          color: #007bff;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #666;
        }

        .tenant-plugins {
          margin: 1rem 0;
        }

        .plugin-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 0.5rem;
        }

        .plugin-tag {
          background: #f0f0f0;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .filters {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .filter-input {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 6px;
        }

        .licenses-table-container {
          background: white;
          border-radius: 12px;
          overflow: hidden;
          border: 1px solid #e0e0e0;
        }

        .licenses-table {
          width: 100%;
          border-collapse: collapse;
        }

        .licenses-table th {
          background: #f8f9fa;
          padding: 1rem;
          text-align: left;
          font-weight: 600;
          border-bottom: 2px solid #e0e0e0;
        }

        .licenses-table td {
          padding: 1rem;
          border-bottom: 1px solid #f0f0f0;
        }

        .licenses-table tr.inactive {
          opacity: 0.6;
          background: #f8f9fa;
        }

        .tenant-cell {
          display: flex;
          flex-direction: column;
        }

        .tenant-id-small {
          font-size: 0.75rem;
          color: #999;
          font-family: monospace;
        }

        .action-buttons {
          display: flex;
          gap: 0.5rem;
        }

        .btn-icon {
          background: none;
          border: 1px solid #ddd;
          padding: 0.5rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 1.2rem;
          transition: all 0.2s;
        }

        .btn-icon:hover {
          background: #f8f9fa;
        }

        .btn-danger:hover {
          background: #fee;
          border-color: #dc3545;
        }

        .days-warning {
          color: #dc3545;
          font-weight: 700;
        }

        .days-caution {
          color: #ff9800;
          font-weight: 600;
        }

        .badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
          margin-right: 0.25rem;
        }

        .badge-success { background: #28a745; color: white; }
        .badge-warning { background: #ffc107; color: #000; }
        .badge-error { background: #dc3545; color: white; }
        .badge-disabled { background: #6c757d; color: white; }
        .badge-premium { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .badge-info { background: #17a2b8; color: white; }

        .button {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s;
        }

        .button-primary {
          background: #007bff;
          color: white;
        }

        .button-primary:hover:not(:disabled) {
          background: #0056b3;
        }

        .button-secondary {
          background: #6c757d;
          color: white;
        }

        .button-secondary:hover:not(:disabled) {
          background: #545b62;
        }

        .button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        /* Modal styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal {
          background: white;
          border-radius: 12px;
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem;
          border-bottom: 1px solid #e0e0e0;
        }

        .modal-header h2 {
          margin: 0;
        }

        .modal-close {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
        }

        .modal-body {
          padding: 1.5rem;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }

        .form-control {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 6px;
        }

        .form-control:focus {
          outline: none;
          border-color: #007bff;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 0.5rem;
          padding: 1.5rem;
          border-top: 1px solid #e0e0e0;
        }

        .empty-row {
          text-align: center;
          padding: 3rem;
          color: #999;
        }
      `}</style>
    </div>
  )
}
