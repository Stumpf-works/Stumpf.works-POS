/**
 * Settings Page
 * System configuration and tenant settings
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tantml:parameter>
import { api } from '../../services/api'

interface TenantSettings {
  name: string
  address_street: string
  address_postal_code: string
  address_city: string
  address_country: string
  tax_id: string
  vat_id: string
  sumup_enabled: boolean
  sumup_merchant_code: string
  tse_enabled: boolean
  fiskaly_api_key: string
  fiskaly_api_secret: string
  fiskaly_tss_id: string
}

interface SystemSettings {
  receipt_footer_text: string
  currency: string
  default_vat_rate: number
  low_stock_threshold: number
  enable_offline_mode: boolean
  auto_print_receipts: boolean
}

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'tenant' | 'system' | 'security'>('tenant')

  const { data: tenantSettings, isLoading: tenantLoading } = useQuery<TenantSettings>({
    queryKey: ['tenant-settings'],
    queryFn: async () => {
      const response = await api.get('/admin/settings/tenant')
      return response.data
    },
  })

  const { data: systemSettings, isLoading: systemLoading } = useQuery<SystemSettings>({
    queryKey: ['system-settings'],
    queryFn: async () => {
      const response = await api.get('/admin/settings/system')
      return response.data
    },
  })

  const updateTenantMutation = useMutation({
    mutationFn: async (data: Partial<TenantSettings>) => {
      const response = await api.patch('/admin/settings/tenant', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant-settings'] })
    },
  })

  const updateSystemMutation = useMutation({
    mutationFn: async (data: Partial<SystemSettings>) => {
      const response = await api.patch('/admin/settings/system', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['system-settings'] })
    },
  })

  return (
    <div className="settings-page">
      <header className="page-header">
        <div>
          <h1>Einstellungen</h1>
          <p className="subtitle">System- und Mandantenkonfiguration</p>
        </div>
      </header>

      <div className="settings-tabs">
        <button
          className={`tab ${activeTab === 'tenant' ? 'active' : ''}`}
          onClick={() => setActiveTab('tenant')}
        >
          🏢 Mandant
        </button>
        <button
          className={`tab ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          ⚙️ System
        </button>
        <button
          className={`tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          🔒 Sicherheit
        </button>
      </div>

      <div className="settings-content">
        {activeTab === 'tenant' && (
          <TenantSettingsForm
            settings={tenantSettings}
            loading={tenantLoading}
            onSubmit={(data) => updateTenantMutation.mutate(data)}
            saving={updateTenantMutation.isPending}
          />
        )}

        {activeTab === 'system' && (
          <SystemSettingsForm
            settings={systemSettings}
            loading={systemLoading}
            onSubmit={(data) => updateSystemMutation.mutate(data)}
            saving={updateSystemMutation.isPending}
          />
        )}

        {activeTab === 'security' && <SecuritySettings />}
      </div>

      <style>{`
        .settings-page {
          max-width: 1000px;
        }

        .page-header {
          margin-bottom: 2rem;
        }

        .page-header h1 {
          margin: 0 0 0.5rem 0;
          font-size: 2rem;
          color: #1a1a2e;
        }

        .subtitle {
          margin: 0;
          color: #6b7280;
        }

        .settings-tabs {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 2rem;
          border-bottom: 2px solid #e5e7eb;
        }

        .tab {
          padding: 1rem 1.5rem;
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
          font-size: 1rem;
          font-weight: 500;
          color: #6b7280;
          transition: all 0.2s;
          margin-bottom: -2px;
        }

        .tab:hover {
          color: #1a1a2e;
        }

        .tab.active {
          color: #10b981;
          border-bottom-color: #10b981;
        }

        .settings-content {
          background: white;
          border-radius: 0.5rem;
          padding: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
      `}</style>
    </div>
  )
}

interface TenantSettingsFormProps {
  settings?: TenantSettings
  loading: boolean
  onSubmit: (data: Partial<TenantSettings>) => void
  saving: boolean
}

function TenantSettingsForm({ settings, loading, onSubmit, saving }: TenantSettingsFormProps) {
  const [formData, setFormData] = useState<Partial<TenantSettings>>(settings || {})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  if (loading) return <div className="loading">Lade Einstellungen...</div>

  return (
    <form onSubmit={handleSubmit} className="settings-form">
      <h2>Mandanteninformationen</h2>

      <div className="form-group">
        <label>Firmenname *</label>
        <input
          type="text"
          required
          value={formData.name || ''}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
      </div>

      <div className="form-group">
        <label>Straße und Hausnummer</label>
        <input
          type="text"
          value={formData.address_street || ''}
          onChange={(e) => setFormData({ ...formData, address_street: e.target.value })}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>PLZ</label>
          <input
            type="text"
            value={formData.address_postal_code || ''}
            onChange={(e) => setFormData({ ...formData, address_postal_code: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label>Stadt</label>
          <input
            type="text"
            value={formData.address_city || ''}
            onChange={(e) => setFormData({ ...formData, address_city: e.target.value })}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Land</label>
        <input
          type="text"
          value={formData.address_country || 'DE'}
          onChange={(e) => setFormData({ ...formData, address_country: e.target.value })}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Steuernummer</label>
          <input
            type="text"
            value={formData.tax_id || ''}
            onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label>USt-IdNr.</label>
          <input
            type="text"
            value={formData.vat_id || ''}
            onChange={(e) => setFormData({ ...formData, vat_id: e.target.value })}
          />
        </div>
      </div>

      <hr />

      <h2>SumUp Integration</h2>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.sumup_enabled || false}
            onChange={(e) => setFormData({ ...formData, sumup_enabled: e.target.checked })}
          />
          SumUp Zahlungen aktivieren
        </label>
      </div>

      {formData.sumup_enabled && (
        <div className="form-group">
          <label>SumUp Merchant Code</label>
          <input
            type="text"
            value={formData.sumup_merchant_code || ''}
            onChange={(e) => setFormData({ ...formData, sumup_merchant_code: e.target.value })}
          />
        </div>
      )}

      <hr />

      <h2>Cloud-TSE (Fiskaly)</h2>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.tse_enabled || false}
            onChange={(e) => setFormData({ ...formData, tse_enabled: e.target.checked })}
          />
          TSE-Signierung aktivieren
        </label>
      </div>

      {formData.tse_enabled && (
        <>
          <div className="form-group">
            <label>Fiskaly API Key</label>
            <input
              type="password"
              value={formData.fiskaly_api_key || ''}
              onChange={(e) => setFormData({ ...formData, fiskaly_api_key: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Fiskaly API Secret</label>
            <input
              type="password"
              value={formData.fiskaly_api_secret || ''}
              onChange={(e) => setFormData({ ...formData, fiskaly_api_secret: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Fiskaly TSS ID</label>
            <input
              type="text"
              value={formData.fiskaly_tss_id || ''}
              onChange={(e) => setFormData({ ...formData, fiskaly_tss_id: e.target.value })}
            />
          </div>
        </>
      )}

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Speichere...' : 'Speichern'}
        </button>
      </div>

      <style>{`
        .settings-form h2 {
          margin: 0 0 1.5rem 0;
          font-size: 1.25rem;
          color: #1a1a2e;
        }

        .settings-form hr {
          border: none;
          border-top: 1px solid #e5e7eb;
          margin: 2rem 0;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #374151;
        }

        .form-group input[type="text"],
        .form-group input[type="password"],
        .form-group input[type="number"],
        .form-group textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          font-size: 1rem;
        }

        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
        }

        .checkbox-label input[type="checkbox"] {
          width: 1.25rem;
          height: 1.25rem;
          cursor: pointer;
        }

        .form-actions {
          display: flex;
          justify-content: flex-end;
          margin-top: 2rem;
        }

        .btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 0.375rem;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #10b981;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #059669;
        }

        .btn-primary:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading {
          text-align: center;
          padding: 3rem;
          color: #6b7280;
        }
      `}</style>
    </form>
  )
}

interface SystemSettingsFormProps {
  settings?: SystemSettings
  loading: boolean
  onSubmit: (data: Partial<SystemSettings>) => void
  saving: boolean
}

function SystemSettingsForm({ settings, loading, onSubmit, saving }: SystemSettingsFormProps) {
  const [formData, setFormData] = useState<Partial<SystemSettings>>(settings || {})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  if (loading) return <div className="loading">Lade Einstellungen...</div>

  return (
    <form onSubmit={handleSubmit} className="settings-form">
      <h2>Allgemeine Einstellungen</h2>

      <div className="form-group">
        <label>Währung</label>
        <select
          value={formData.currency || 'EUR'}
          onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
        >
          <option value="EUR">EUR (€)</option>
          <option value="USD">USD ($)</option>
          <option value="CHF">CHF (Fr.)</option>
        </select>
      </div>

      <div className="form-group">
        <label>Standard-Mehrwertsteuersatz (%)</label>
        <input
          type="number"
          step="0.01"
          value={formData.default_vat_rate || 19}
          onChange={(e) =>
            setFormData({ ...formData, default_vat_rate: parseFloat(e.target.value) })
          }
        />
      </div>

      <div className="form-group">
        <label>Niedrigbestand-Schwellenwert</label>
        <input
          type="number"
          value={formData.low_stock_threshold || 10}
          onChange={(e) =>
            setFormData({ ...formData, low_stock_threshold: parseInt(e.target.value) })
          }
        />
      </div>

      <hr />

      <h2>Kassenbon-Einstellungen</h2>

      <div className="form-group">
        <label>Fußzeilentext für Kassenbon</label>
        <textarea
          rows={4}
          value={formData.receipt_footer_text || ''}
          onChange={(e) => setFormData({ ...formData, receipt_footer_text: e.target.value })}
          placeholder="z.B. Vielen Dank für Ihren Einkauf!"
        />
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.auto_print_receipts || false}
            onChange={(e) => setFormData({ ...formData, auto_print_receipts: e.target.checked })}
          />
          Kassenbons automatisch drucken
        </label>
      </div>

      <hr />

      <h2>Offline-Modus</h2>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.enable_offline_mode || false}
            onChange={(e) => setFormData({ ...formData, enable_offline_mode: e.target.checked })}
          />
          Offline-Modus aktivieren
        </label>
        <p className="help-text">
          Ermöglicht Verkäufe, wenn keine Internetverbindung besteht. Transaktionen werden
          synchronisiert, sobald die Verbindung wiederhergestellt ist.
        </p>
      </div>

      <div className="form-actions">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Speichere...' : 'Speichern'}
        </button>
      </div>

      <style>{`
        .help-text {
          margin: 0.5rem 0 0 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          font-size: 1rem;
          background: white;
        }

        textarea {
          font-family: inherit;
        }
      `}</style>
    </form>
  )
}

function SecuritySettings() {
  return (
    <div className="security-settings">
      <h2>Sicherheitseinstellungen</h2>

      <div className="security-section">
        <h3>🔐 Passwort-Richtlinien</h3>
        <ul>
          <li>Mindestlänge: 8 Zeichen</li>
          <li>Mindestens ein Großbuchstabe erforderlich</li>
          <li>Mindestens eine Zahl erforderlich</li>
          <li>Passwort-Ablauf: 90 Tage</li>
        </ul>
      </div>

      <div className="security-section">
        <h3>🔒 Zugriffskontrolle</h3>
        <ul>
          <li>Maximale Anmeldeversuche: 5</li>
          <li>Kontosperrung nach Fehlversuchen: 15 Minuten</li>
          <li>Sitzungsdauer: 8 Stunden</li>
        </ul>
      </div>

      <div className="security-section">
        <h3>📋 Audit-Log</h3>
        <p>
          Alle sicherheitsrelevanten Ereignisse werden protokolliert und können für Audits
          eingesehen werden.
        </p>
        <button className="btn btn-secondary">Audit-Log anzeigen</button>
      </div>

      <style>{`
        .security-settings h2 {
          margin: 0 0 1.5rem 0;
          font-size: 1.25rem;
          color: #1a1a2e;
        }

        .security-section {
          margin-bottom: 2rem;
          padding: 1.5rem;
          background: #f9fafb;
          border-radius: 0.375rem;
        }

        .security-section h3 {
          margin: 0 0 1rem 0;
          font-size: 1.125rem;
          color: #374151;
        }

        .security-section ul {
          margin: 0;
          padding-left: 1.5rem;
        }

        .security-section li {
          margin: 0.5rem 0;
          color: #6b7280;
        }

        .security-section p {
          margin: 0 0 1rem 0;
          color: #6b7280;
        }

        .btn-secondary {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 0.375rem;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          background: #e5e7eb;
          color: #374151;
          transition: all 0.2s;
        }

        .btn-secondary:hover {
          background: #d1d5db;
        }
      `}</style>
    </div>
  )
}
