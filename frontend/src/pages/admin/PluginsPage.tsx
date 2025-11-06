/**
 * Plugins Page (Tenant Admin)
 * View and manage licensed plugins for the tenant
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../services/api'

interface PluginInfo {
  name: string
  display_name: string
  description: string
  version: string
  author?: string
  category: string
  is_enabled: boolean
  is_loaded: boolean
  requires: string[]
  config_schema?: any
  // License info
  is_licensed: boolean
  license_type?: string
  license_valid: boolean
  license_expires?: string
  days_remaining?: number
}

interface PluginCategory {
  name: string
  description: string
  icon: string
}

type CategoryKey = 'all' | 'restaurant' | 'retail' | 'pharmacy' | 'bakery' | 'general' | 'hardware' | 'payment' | 'analytics'

export default function PluginsPage() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<CategoryKey>('all')
  const [selectedPlugin, setSelectedPlugin] = useState<PluginInfo | null>(null)
  const [showConfigModal, setShowConfigModal] = useState(false)
  const [pluginConfig, setPluginConfig] = useState<any>({})

  // Fetch plugins
  const { data: plugins = [], isLoading } = useQuery<PluginInfo[]>({
    queryKey: ['plugins'],
    queryFn: async () => {
      const response = await api.get('/plugins')
      return response.data
    },
  })

  // Fetch categories
  const { data: categories = {} } = useQuery<Record<string, PluginCategory>>({
    queryKey: ['plugin-categories'],
    queryFn: async () => {
      const response = await api.get('/plugins/categories/available')
      return response.data
    },
  })

  // Enable plugin mutation
  const enablePluginMutation = useMutation({
    mutationFn: async ({ name, config }: { name: string; config?: any }) => {
      const response = await api.post(`/plugins/${name}/enable`, { config })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins'] })
      setShowConfigModal(false)
      setSelectedPlugin(null)
    },
  })

  // Disable plugin mutation
  const disablePluginMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await api.post(`/plugins/${name}/disable`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins'] })
    },
  })

  // Update plugin config mutation
  const updateConfigMutation = useMutation({
    mutationFn: async ({ name, config }: { name: string; config: any }) => {
      const response = await api.patch(`/plugins/${name}/config`, config)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins'] })
      setShowConfigModal(false)
      setSelectedPlugin(null)
    },
  })

  // Filter plugins by category
  const filteredPlugins = selectedCategory === 'all'
    ? plugins
    : plugins.filter(p => p.category === selectedCategory)

  // Count plugins per category
  const categoryCount = (cat: string) =>
    plugins.filter(p => p.category === cat).length

  const handleEnablePlugin = (plugin: PluginInfo) => {
    if (plugin.config_schema) {
      // Show config modal
      setSelectedPlugin(plugin)
      setPluginConfig({})
      setShowConfigModal(true)
    } else {
      // Enable without config
      enablePluginMutation.mutate({ name: plugin.name })
    }
  }

  const handleDisablePlugin = (plugin: PluginInfo) => {
    if (confirm(`Plugin "${plugin.display_name}" deaktivieren?`)) {
      disablePluginMutation.mutate(plugin.name)
    }
  }

  const handleConfigurePlugin = (plugin: PluginInfo) => {
    setSelectedPlugin(plugin)
    setPluginConfig({}) // TODO: Load existing config
    setShowConfigModal(true)
  }

  const handleSaveConfig = () => {
    if (!selectedPlugin) return

    if (selectedPlugin.is_enabled) {
      // Update existing config
      updateConfigMutation.mutate({
        name: selectedPlugin.name,
        config: pluginConfig,
      })
    } else {
      // Enable with config
      enablePluginMutation.mutate({
        name: selectedPlugin.name,
        config: pluginConfig,
      })
    }
  }

  const getCategoryIcon = (category: string): string => {
    return categories[category]?.icon || '⚙️'
  }

  const getLicenseTypeBadge = (licenseType?: string) => {
    if (!licenseType) return null

    const badges: Record<string, { label: string; className: string }> = {
      trial: { label: 'Trial', className: 'badge-warning' },
      standard: { label: 'Standard', className: 'badge-success' },
      enterprise: { label: 'Enterprise', className: 'badge-premium' },
    }

    const badge = badges[licenseType] || { label: licenseType, className: 'badge-info' }

    return <span className={`badge ${badge.className}`}>{badge.label}</span>
  }

  if (isLoading) {
    return (
      <div className="plugins-page">
        <div className="loading">
          <div className="spinner" />
          <p>Lade Plugins...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="plugins-page">
      <header className="page-header">
        <div>
          <h1>🧩 Plugins</h1>
          <p className="subtitle">Verwalten Sie Ihre lizenzierten Erweiterungen</p>
        </div>
      </header>

      {/* No licensed plugins message */}
      {plugins.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <h3>Keine Plugins lizenziert</h3>
          <p>
            Kontaktieren Sie Stumpf.works Support, um Plugins für Ihr
            Unternehmen freizuschalten.
          </p>
          <a
            href="mailto:support@stumpf.works"
            className="button button-primary"
          >
            Support kontaktieren
          </a>
        </div>
      )}

      {/* Category filters */}
      {plugins.length > 0 && (
        <div className="category-filters">
          <button
            className={`filter-btn ${selectedCategory === 'all' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('all')}
          >
            Alle ({plugins.length})
          </button>
          {Object.entries(categories).map(([key, category]) => {
            const count = categoryCount(key)
            if (count === 0) return null

            return (
              <button
                key={key}
                className={`filter-btn ${selectedCategory === key ? 'active' : ''}`}
                onClick={() => setSelectedCategory(key as CategoryKey)}
              >
                {category.icon} {category.name} ({count})
              </button>
            )
          })}
        </div>
      )}

      {/* Plugin Grid */}
      <div className="plugins-grid">
        {filteredPlugins.map((plugin) => (
          <div key={plugin.name} className={`plugin-card ${plugin.is_enabled ? 'enabled' : ''}`}>
            <div className="plugin-header">
              <div className="plugin-icon">
                {getCategoryIcon(plugin.category)}
              </div>
              <div className="plugin-title">
                <h3>{plugin.display_name}</h3>
                <div className="plugin-meta">
                  <span className="version">v{plugin.version}</span>
                  {getLicenseTypeBadge(plugin.license_type)}
                  {plugin.is_enabled && (
                    <span className="badge badge-success">Aktiv</span>
                  )}
                </div>
              </div>
            </div>

            <p className="plugin-description">{plugin.description}</p>

            {/* License warning */}
            {!plugin.license_valid && (
              <div className="alert alert-error">
                ⚠️ Lizenz abgelaufen. Kontaktieren Sie Support.
              </div>
            )}

            {plugin.license_type === 'trial' && plugin.days_remaining !== null && (
              <div className={`alert ${plugin.days_remaining <= 7 ? 'alert-warning' : 'alert-info'}`}>
                🕐 Trial endet in {plugin.days_remaining} Tagen
                {plugin.days_remaining <= 7 && (
                  <span> - Jetzt upgraden!</span>
                )}
              </div>
            )}

            {/* Dependencies */}
            {plugin.requires && plugin.requires.length > 0 && (
              <div className="plugin-requires">
                <small>
                  <strong>Benötigt:</strong> {plugin.requires.join(', ')}
                </small>
              </div>
            )}

            {/* Actions */}
            <div className="plugin-actions">
              {!plugin.is_enabled ? (
                <button
                  className="button button-primary"
                  onClick={() => handleEnablePlugin(plugin)}
                  disabled={!plugin.license_valid || enablePluginMutation.isPending}
                >
                  {enablePluginMutation.isPending ? 'Aktiviere...' : 'Aktivieren'}
                </button>
              ) : (
                <>
                  {plugin.config_schema && (
                    <button
                      className="button button-secondary"
                      onClick={() => handleConfigurePlugin(plugin)}
                    >
                      ⚙️ Konfigurieren
                    </button>
                  )}
                  <button
                    className="button button-danger"
                    onClick={() => handleDisablePlugin(plugin)}
                    disabled={disablePluginMutation.isPending}
                  >
                    {disablePluginMutation.isPending ? 'Deaktiviere...' : 'Deaktivieren'}
                  </button>
                </>
              )}
            </div>

            {/* Footer info */}
            <div className="plugin-footer">
              {plugin.author && <span className="author">von {plugin.author}</span>}
              {plugin.license_expires && (
                <span className="expires">
                  Läuft ab: {new Date(plugin.license_expires).toLocaleDateString('de-DE')}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Configuration Modal */}
      {showConfigModal && selectedPlugin && (
        <div className="modal-overlay" onClick={() => setShowConfigModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                {selectedPlugin.is_enabled ? 'Konfigurieren' : 'Aktivieren'}:{' '}
                {selectedPlugin.display_name}
              </h2>
              <button
                className="modal-close"
                onClick={() => setShowConfigModal(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <p className="modal-description">
                {selectedPlugin.description}
              </p>

              {selectedPlugin.config_schema && (
                <div className="config-form">
                  <h3>Einstellungen</h3>
                  {Object.entries(
                    selectedPlugin.config_schema.properties || {}
                  ).map(([key, schema]: [string, any]) => (
                    <div key={key} className="form-group">
                      <label htmlFor={key}>
                        {schema.description || key}
                        {selectedPlugin.config_schema.required?.includes(key) && (
                          <span className="required">*</span>
                        )}
                      </label>

                      {schema.type === 'boolean' ? (
                        <div className="checkbox-wrapper">
                          <input
                            type="checkbox"
                            id={key}
                            checked={pluginConfig[key] ?? schema.default ?? false}
                            onChange={(e) =>
                              setPluginConfig({
                                ...pluginConfig,
                                [key]: e.target.checked,
                              })
                            }
                          />
                          <span className="checkbox-label">
                            {schema.description || key}
                          </span>
                        </div>
                      ) : schema.type === 'integer' || schema.type === 'number' ? (
                        <input
                          type="number"
                          id={key}
                          value={pluginConfig[key] ?? schema.default ?? ''}
                          onChange={(e) =>
                            setPluginConfig({
                              ...pluginConfig,
                              [key]: parseFloat(e.target.value),
                            })
                          }
                          className="form-control"
                        />
                      ) : (
                        <input
                          type="text"
                          id={key}
                          value={pluginConfig[key] ?? schema.default ?? ''}
                          onChange={(e) =>
                            setPluginConfig({
                              ...pluginConfig,
                              [key]: e.target.value,
                            })
                          }
                          className="form-control"
                        />
                      )}

                      {schema.description && schema.type === 'boolean' && (
                        <small className="form-hint">{schema.description}</small>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="button button-secondary"
                onClick={() => setShowConfigModal(false)}
              >
                Abbrechen
              </button>
              <button
                className="button button-primary"
                onClick={handleSaveConfig}
                disabled={
                  enablePluginMutation.isPending || updateConfigMutation.isPending
                }
              >
                {enablePluginMutation.isPending || updateConfigMutation.isPending
                  ? 'Speichere...'
                  : selectedPlugin.is_enabled
                  ? 'Speichern'
                  : 'Aktivieren'}
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .plugins-page {
          padding: 2rem;
          max-width: 1400px;
          margin: 0 auto;
        }

        .page-header {
          margin-bottom: 2rem;
        }

        .page-header h1 {
          font-size: 2rem;
          margin-bottom: 0.5rem;
        }

        .subtitle {
          color: #666;
          font-size: 1rem;
        }

        /* Empty State */
        .empty-state {
          text-align: center;
          padding: 4rem 2rem;
        }

        .empty-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }

        .empty-state h3 {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
        }

        .empty-state p {
          color: #666;
          margin-bottom: 2rem;
        }

        /* Category Filters */
        .category-filters {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 2rem;
          flex-wrap: wrap;
        }

        .filter-btn {
          padding: 0.5rem 1rem;
          border: 2px solid #e0e0e0;
          background: white;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .filter-btn:hover {
          border-color: #007bff;
          background: #f8f9fa;
        }

        .filter-btn.active {
          border-color: #007bff;
          background: #007bff;
          color: white;
        }

        /* Plugin Grid */
        .plugins-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
        }

        .plugin-card {
          border: 2px solid #e0e0e0;
          border-radius: 12px;
          padding: 1.5rem;
          background: white;
          transition: all 0.3s;
        }

        .plugin-card:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }

        .plugin-card.enabled {
          border-color: #28a745;
          background: #f8fff9;
        }

        .plugin-header {
          display: flex;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .plugin-icon {
          font-size: 2.5rem;
          line-height: 1;
        }

        .plugin-title h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.25rem;
        }

        .plugin-meta {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .version {
          font-size: 0.875rem;
          color: #666;
          background: #f0f0f0;
          padding: 0.125rem 0.5rem;
          border-radius: 4px;
        }

        .badge {
          font-size: 0.75rem;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-weight: 600;
        }

        .badge-success {
          background: #28a745;
          color: white;
        }

        .badge-warning {
          background: #ffc107;
          color: #000;
        }

        .badge-premium {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .badge-info {
          background: #17a2b8;
          color: white;
        }

        .plugin-description {
          color: #666;
          margin-bottom: 1rem;
          line-height: 1.5;
        }

        .alert {
          padding: 0.75rem;
          border-radius: 6px;
          margin-bottom: 1rem;
          font-size: 0.875rem;
        }

        .alert-info {
          background: #d1ecf1;
          color: #0c5460;
        }

        .alert-warning {
          background: #fff3cd;
          color: #856404;
        }

        .alert-error {
          background: #f8d7da;
          color: #721c24;
        }

        .plugin-requires {
          margin-bottom: 1rem;
          padding: 0.5rem;
          background: #f8f9fa;
          border-radius: 4px;
        }

        .plugin-actions {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .button {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s;
          flex: 1;
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

        .button-danger {
          background: #dc3545;
          color: white;
        }

        .button-danger:hover:not(:disabled) {
          background: #c82333;
        }

        .button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .plugin-footer {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
          color: #999;
          padding-top: 1rem;
          border-top: 1px solid #e0e0e0;
        }

        /* Modal */
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
          font-size: 1.5rem;
        }

        .modal-close {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: #999;
        }

        .modal-close:hover {
          color: #000;
        }

        .modal-body {
          padding: 1.5rem;
        }

        .modal-description {
          color: #666;
          margin-bottom: 2rem;
        }

        .config-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }

        .required {
          color: #dc3545;
          margin-left: 0.25rem;
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

        .checkbox-wrapper {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .checkbox-wrapper input[type="checkbox"] {
          width: 20px;
          height: 20px;
        }

        .checkbox-label {
          font-weight: normal;
        }

        .form-hint {
          display: block;
          margin-top: 0.25rem;
          color: #666;
          font-size: 0.875rem;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 0.5rem;
          padding: 1.5rem;
          border-top: 1px solid #e0e0e0;
        }

        .modal-footer .button {
          flex: initial;
        }

        /* Loading */
        .loading {
          text-align: center;
          padding: 4rem 2rem;
        }

        .spinner {
          border: 4px solid #f3f3f3;
          border-top: 4px solid #007bff;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
