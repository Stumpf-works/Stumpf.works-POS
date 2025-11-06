/**
 * Exports Page
 * GoBD/DSFinV-K compliant data exports for tax authorities
 */

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'

interface ExportHistoryItem {
  id: number
  export_type: string
  start_date: string
  end_date: string
  file_size: number
  created_at: string
  created_by: string
  download_url: string
}

export default function ExportsPage() {
  const [exportType, setExportType] = useState<'dsfink' | 'csv'>('dsfink')
  const [startDate, setStartDate] = useState(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  )
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])

  const { data: exportHistory } = useQuery<ExportHistoryItem[]>({
    queryKey: ['export-history'],
    queryFn: async () => {
      const response = await api.get('/admin/exports/history')
      return response.data
    },
  })

  const dsfinvkExportMutation = useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      })
      const response = await api.get(`/exports/dsfink?${params}`, {
        responseType: 'blob',
      })
      return response.data
    },
    onSuccess: (data) => {
      // Download file
      const url = window.URL.createObjectURL(new Blob([data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `dsfink_export_${startDate}_${endDate}.tar.gz`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    },
  })

  const csvExportMutation = useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      })
      const response = await api.get(`/exports/transactions/csv?${params}`, {
        responseType: 'blob',
      })
      return response.data
    },
    onSuccess: (data) => {
      const url = window.URL.createObjectURL(new Blob([data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `transactions_${startDate}_${endDate}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    },
  })

  const handleExport = () => {
    if (exportType === 'dsfink') {
      dsfinvkExportMutation.mutate()
    } else {
      csvExportMutation.mutate()
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div className="exports-page">
      <header className="page-header">
        <div>
          <h1>Datenexporte</h1>
          <p className="subtitle">GoBD-konforme Exporte für Betriebsprüfungen</p>
        </div>
      </header>

      <div className="export-section">
        <div className="card export-card">
          <h2>Neuer Export</h2>

          <div className="form-group">
            <label>Export-Typ</label>
            <div className="export-types">
              <label className="export-type-option">
                <input
                  type="radio"
                  value="dsfink"
                  checked={exportType === 'dsfink'}
                  onChange={(e) => setExportType(e.target.value as 'dsfink' | 'csv')}
                />
                <div className="option-content">
                  <div className="option-title">DSFinV-K Export</div>
                  <div className="option-description">
                    Offizielles Format für Betriebsprüfungen (TAR.GZ mit CSV-Dateien)
                  </div>
                  <div className="option-badge">Empfohlen für Finanzamt</div>
                </div>
              </label>

              <label className="export-type-option">
                <input
                  type="radio"
                  value="csv"
                  checked={exportType === 'csv'}
                  onChange={(e) => setExportType(e.target.value as 'dsfink' | 'csv')}
                />
                <div className="option-content">
                  <div className="option-title">Einfacher CSV Export</div>
                  <div className="option-description">
                    Vereinfachtes Format für interne Berichte und Analysen
                  </div>
                  <div className="option-badge">Für interne Nutzung</div>
                </div>
              </label>
            </div>
          </div>

          <div className="date-range">
            <div className="form-group">
              <label>Startdatum</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Enddatum</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
          </div>

          {exportType === 'dsfink' && (
            <div className="info-box">
              <strong>📋 DSFinV-K Exportinhalt:</strong>
              <ul>
                <li>Stammdaten: Standorte, Kassen, Mitarbeiter, Artikel</li>
                <li>Bonköpfe: Transaktionsübersicht</li>
                <li>Bonpositionen: Einzelne Transaktionsposten</li>
                <li>TSE-Transaktionen: Technische Sicherheitseinrichtung-Daten</li>
              </ul>
              <p>
                Dieser Export erfüllt die Anforderungen der deutschen Finanzverwaltung gemäß
                DSFinV-K (Digitale Schnittstelle der Finanzverwaltung für Kassensysteme).
              </p>
            </div>
          )}

          <button
            className="btn btn-primary btn-large"
            onClick={handleExport}
            disabled={dsfinvkExportMutation.isPending || csvExportMutation.isPending}
          >
            {dsfinvkExportMutation.isPending || csvExportMutation.isPending
              ? '⏳ Exportiere...'
              : '📤 Export starten'}
          </button>
        </div>

        <div className="card compliance-card">
          <h2>🔒 Compliance-Hinweise</h2>
          <div className="compliance-list">
            <div className="compliance-item">
              <span className="check-icon">✅</span>
              <div>
                <strong>GoBD-konform</strong>
                <p>
                  Alle Exporte erfüllen die Grundsätze zur ordnungsmäßigen Führung und
                  Aufbewahrung von Büchern
                </p>
              </div>
            </div>
            <div className="compliance-item">
              <span className="check-icon">✅</span>
              <div>
                <strong>KassenSichV-konform</strong>
                <p>TSE-Signaturen werden in allen Exporten korrekt abgebildet</p>
              </div>
            </div>
            <div className="compliance-item">
              <span className="check-icon">✅</span>
              <div>
                <strong>Aufbewahrungspflicht</strong>
                <p>Daten werden revisionssicher gespeichert und können jederzeit exportiert werden</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Export History */}
      <div className="card history-card">
        <h2>Export-Verlauf</h2>
        {exportHistory && exportHistory.length > 0 ? (
          <div className="history-table">
            <table>
              <thead>
                <tr>
                  <th>Datum</th>
                  <th>Typ</th>
                  <th>Zeitraum</th>
                  <th>Größe</th>
                  <th>Erstellt von</th>
                  <th>Download</th>
                </tr>
              </thead>
              <tbody>
                {exportHistory.map((item) => (
                  <tr key={item.id}>
                    <td>{new Date(item.created_at).toLocaleString('de-DE')}</td>
                    <td>
                      <span className={`badge badge-${item.export_type}`}>
                        {item.export_type.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      {new Date(item.start_date).toLocaleDateString('de-DE')} -{' '}
                      {new Date(item.end_date).toLocaleDateString('de-DE')}
                    </td>
                    <td>{formatFileSize(item.file_size)}</td>
                    <td>{item.created_by}</td>
                    <td>
                      <button
                        className="btn-icon"
                        onClick={() => window.open(item.download_url, '_blank')}
                      >
                        📥 Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="empty-state">Noch keine Exporte erstellt</p>
        )}
      </div>

      <style>{`
        .exports-page {
          max-width: 1200px;
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

        .export-section {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .card {
          background: white;
          border-radius: 0.5rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .card h2 {
          margin: 0 0 1.5rem 0;
          font-size: 1.25rem;
          color: #1a1a2e;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #374151;
        }

        .form-group input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          font-size: 1rem;
        }

        .export-types {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .export-type-option {
          display: flex;
          gap: 1rem;
          padding: 1rem;
          border: 2px solid #e5e7eb;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .export-type-option:hover {
          border-color: #10b981;
          background: #f0fdf4;
        }

        .export-type-option input[type="radio"]:checked + .option-content {
          color: #065f46;
        }

        .export-type-option input[type="radio"]:checked ~ .option-content .option-badge {
          background: #10b981;
          color: white;
        }

        .option-content {
          flex: 1;
        }

        .option-title {
          font-weight: 600;
          font-size: 1.125rem;
          margin-bottom: 0.5rem;
        }

        .option-description {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .option-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          background: #e5e7eb;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .date-range {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .info-box {
          background: #f0f9ff;
          border-left: 4px solid #3b82f6;
          padding: 1rem;
          border-radius: 0.375rem;
          margin-bottom: 1.5rem;
        }

        .info-box strong {
          display: block;
          margin-bottom: 0.5rem;
          color: #1e40af;
        }

        .info-box ul {
          margin: 0.5rem 0;
          padding-left: 1.5rem;
        }

        .info-box li {
          margin: 0.25rem 0;
          font-size: 0.875rem;
        }

        .info-box p {
          margin: 0.5rem 0 0 0;
          font-size: 0.875rem;
          color: #1e40af;
        }

        .compliance-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .compliance-item {
          display: flex;
          gap: 1rem;
        }

        .check-icon {
          font-size: 1.5rem;
        }

        .compliance-item strong {
          display: block;
          margin-bottom: 0.25rem;
          color: #065f46;
        }

        .compliance-item p {
          margin: 0;
          font-size: 0.875rem;
          color: #6b7280;
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

        .btn-large {
          width: 100%;
          padding: 1rem 2rem;
          font-size: 1.125rem;
        }

        .history-table {
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th {
          background: #f9fafb;
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          color: #374151;
          border-bottom: 2px solid #e5e7eb;
          font-size: 0.875rem;
        }

        td {
          padding: 0.75rem;
          border-bottom: 1px solid #e5e7eb;
        }

        tbody tr:hover {
          background: #f9fafb;
        }

        .badge {
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: uppercase;
        }

        .badge-dsfink {
          background: #fce7f3;
          color: #831843;
        }

        .badge-csv {
          background: #dbeafe;
          color: #1e40af;
        }

        .btn-icon {
          background: none;
          border: none;
          color: #10b981;
          cursor: pointer;
          font-size: 0.875rem;
          padding: 0.5rem;
          transition: all 0.2s;
        }

        .btn-icon:hover {
          color: #059669;
        }

        .empty-state {
          text-align: center;
          padding: 2rem;
          color: #6b7280;
        }

        @media (max-width: 768px) {
          .export-section {
            grid-template-columns: 1fr;
          }

          .date-range {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  )
}
