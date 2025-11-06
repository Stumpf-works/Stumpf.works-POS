/**
 * Admin Dashboard Page
 * Overview with analytics, metrics, and recent activity
 */

import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'
import { formatCurrency } from '../../utils/format'

interface DashboardStats {
  today_sales: number
  today_transactions: number
  today_average_basket: number
  month_sales: number
  month_transactions: number
  active_products: number
  low_stock_products: number
  pending_tse_signatures: number
}

interface RecentTransaction {
  id: number
  receipt_number: string
  total: number
  payment_method: string
  completed_at: string
  is_tse_signed: boolean
}

export default function DashboardPage() {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await api.get('/admin/dashboard/stats')
      return response.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const { data: recentTransactions, isLoading: transactionsLoading } = useQuery<
    RecentTransaction[]
  >({
    queryKey: ['recent-transactions'],
    queryFn: async () => {
      const response = await api.get('/admin/dashboard/recent-transactions?limit=10')
      return response.data
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p className="subtitle">Willkommen im Stumpf.works POS Admin-Bereich</p>
        </div>
        <div className="current-time">
          <div className="time">{currentTime.toLocaleTimeString('de-DE')}</div>
          <div className="date">{currentTime.toLocaleDateString('de-DE')}</div>
        </div>
      </header>

      {/* Key Metrics */}
      <section className="metrics-grid">
        <MetricCard
          title="Heutige Umsätze"
          value={formatCurrency(stats?.today_sales || 0)}
          icon="💰"
          color="#10b981"
          loading={statsLoading}
        />
        <MetricCard
          title="Transaktionen (Heute)"
          value={stats?.today_transactions || 0}
          icon="🛒"
          color="#3b82f6"
          loading={statsLoading}
        />
        <MetricCard
          title="Ø Warenkorbwert"
          value={formatCurrency(stats?.today_average_basket || 0)}
          icon="📊"
          color="#8b5cf6"
          loading={statsLoading}
        />
        <MetricCard
          title="Monatsumsatz"
          value={formatCurrency(stats?.month_sales || 0)}
          icon="📈"
          color="#f59e0b"
          loading={statsLoading}
        />
      </section>

      <div className="dashboard-grid">
        {/* Alerts/Warnings */}
        <section className="card alerts-card">
          <h2>Warnungen & Hinweise</h2>
          <div className="alerts-list">
            {stats?.low_stock_products > 0 && (
              <div className="alert alert-warning">
                <span className="alert-icon">⚠️</span>
                <div>
                  <strong>Niedriger Lagerbestand</strong>
                  <p>{stats.low_stock_products} Produkte haben einen niedrigen Lagerbestand</p>
                </div>
              </div>
            )}
            {stats?.pending_tse_signatures > 0 && (
              <div className="alert alert-info">
                <span className="alert-icon">🔐</span>
                <div>
                  <strong>Ausstehende TSE-Signaturen</strong>
                  <p>{stats.pending_tse_signatures} Transaktionen warten auf TSE-Signatur</p>
                </div>
              </div>
            )}
            {(!stats?.low_stock_products && !stats?.pending_tse_signatures) && (
              <div className="alert alert-success">
                <span className="alert-icon">✅</span>
                <div>
                  <strong>Alles in Ordnung</strong>
                  <p>Keine Warnungen oder Probleme</p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Recent Transactions */}
        <section className="card transactions-card">
          <h2>Letzte Transaktionen</h2>
          {transactionsLoading ? (
            <div className="loading">Lade Transaktionen...</div>
          ) : (
            <div className="transactions-list">
              {recentTransactions?.map((txn) => (
                <div key={txn.id} className="transaction-item">
                  <div className="transaction-info">
                    <div className="transaction-number">#{txn.receipt_number}</div>
                    <div className="transaction-time">
                      {new Date(txn.completed_at).toLocaleString('de-DE')}
                    </div>
                  </div>
                  <div className="transaction-details">
                    <div className="transaction-amount">{formatCurrency(txn.total)}</div>
                    <div className="transaction-badges">
                      <span className={`badge badge-${txn.payment_method}`}>
                        {txn.payment_method}
                      </span>
                      {txn.is_tse_signed && <span className="badge badge-tse">TSE ✓</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <style>{`
        .dashboard-page {
          max-width: 1400px;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 2rem;
        }

        .dashboard-header h1 {
          margin: 0 0 0.5rem 0;
          font-size: 2rem;
          color: #1a1a2e;
        }

        .subtitle {
          margin: 0;
          color: #6b7280;
        }

        .current-time {
          text-align: right;
        }

        .time {
          font-size: 2rem;
          font-weight: 600;
          color: #1a1a2e;
          font-variant-numeric: tabular-nums;
        }

        .date {
          color: #6b7280;
          margin-top: 0.25rem;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .dashboard-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 1.5rem;
        }

        .card {
          background: white;
          border-radius: 0.5rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .card h2 {
          margin: 0 0 1rem 0;
          font-size: 1.25rem;
          color: #1a1a2e;
        }

        .alerts-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .alert {
          display: flex;
          gap: 1rem;
          padding: 1rem;
          border-radius: 0.375rem;
          border-left: 4px solid;
        }

        .alert-icon {
          font-size: 1.5rem;
        }

        .alert strong {
          display: block;
          margin-bottom: 0.25rem;
        }

        .alert p {
          margin: 0;
          font-size: 0.875rem;
        }

        .alert-warning {
          background: #fef3c7;
          border-color: #f59e0b;
          color: #92400e;
        }

        .alert-info {
          background: #dbeafe;
          border-color: #3b82f6;
          color: #1e40af;
        }

        .alert-success {
          background: #d1fae5;
          border-color: #10b981;
          color: #065f46;
        }

        .transactions-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .transaction-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 0.375rem;
          border: 1px solid #e5e7eb;
        }

        .transaction-number {
          font-weight: 600;
          color: #1a1a2e;
        }

        .transaction-time {
          font-size: 0.875rem;
          color: #6b7280;
          margin-top: 0.25rem;
        }

        .transaction-details {
          text-align: right;
        }

        .transaction-amount {
          font-weight: 600;
          font-size: 1.125rem;
          color: #10b981;
        }

        .transaction-badges {
          display: flex;
          gap: 0.5rem;
          justify-content: flex-end;
          margin-top: 0.25rem;
        }

        .badge {
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: uppercase;
        }

        .badge-cash {
          background: #d1fae5;
          color: #065f46;
        }

        .badge-card {
          background: #dbeafe;
          color: #1e40af;
        }

        .badge-sumup {
          background: #e0e7ff;
          color: #3730a3;
        }

        .badge-tse {
          background: #fce7f3;
          color: #831843;
        }

        .loading {
          text-align: center;
          padding: 2rem;
          color: #6b7280;
        }

        @media (max-width: 768px) {
          .dashboard-header {
            flex-direction: column;
            gap: 1rem;
          }

          .current-time {
            text-align: left;
          }

          .dashboard-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  )
}

interface MetricCardProps {
  title: string
  value: string | number
  icon: string
  color: string
  loading?: boolean
}

function MetricCard({ title, value, icon, color, loading }: MetricCardProps) {
  return (
    <div className="metric-card" style={{ borderTopColor: color }}>
      <div className="metric-icon" style={{ color }}>
        {icon}
      </div>
      <div className="metric-content">
        <div className="metric-title">{title}</div>
        <div className="metric-value" style={{ color }}>
          {loading ? '...' : value}
        </div>
      </div>
      <style>{`
        .metric-card {
          background: white;
          border-radius: 0.5rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          border-top: 4px solid;
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .metric-icon {
          font-size: 2.5rem;
        }

        .metric-content {
          flex: 1;
        }

        .metric-title {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .metric-value {
          font-size: 1.875rem;
          font-weight: 700;
          font-variant-numeric: tabular-nums;
        }
      `}</style>
    </div>
  )
}
