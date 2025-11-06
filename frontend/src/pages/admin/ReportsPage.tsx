/**
 * Reports Page
 * Sales analytics, transaction reports, and insights
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../services/api'
import { formatCurrency } from '../../utils/format'

interface ReportFilters {
  start_date: string
  end_date: string
  groupBy: 'day' | 'week' | 'month'
}

interface SalesReport {
  total_sales: number
  total_transactions: number
  average_basket: number
  sales_by_payment_method: {
    cash: number
    card: number
    sumup: number
  }
  sales_by_day: Array<{
    date: string
    sales: number
    transactions: number
  }>
  top_products: Array<{
    product_id: number
    product_name: string
    quantity_sold: number
    total_sales: number
  }>
  sales_by_hour: Array<{
    hour: number
    sales: number
    transactions: number
  }>
}

export default function ReportsPage() {
  const [filters, setFilters] = useState<ReportFilters>({
    start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    groupBy: 'day',
  })

  const { data: report, isLoading } = useQuery<SalesReport>({
    queryKey: ['sales-report', filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        start_date: filters.start_date,
        end_date: filters.end_date,
        group_by: filters.groupBy,
      })
      const response = await api.get(`/admin/reports/sales?${params}`)
      return response.data
    },
  })

  const exportReport = async (format: 'csv' | 'pdf') => {
    const params = new URLSearchParams({
      start_date: filters.start_date,
      end_date: filters.end_date,
      format,
    })
    const response = await api.get(`/admin/reports/export?${params}`, {
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `sales_report_${filters.start_date}_${filters.end_date}.${format}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  return (
    <div className="reports-page">
      <header className="page-header">
        <div>
          <h1>Berichte & Analysen</h1>
          <p className="subtitle">Umsätze, Transaktionen und Insights</p>
        </div>
        <div className="export-buttons">
          <button className="btn btn-secondary" onClick={() => exportReport('csv')}>
            📊 CSV Export
          </button>
          <button className="btn btn-secondary" onClick={() => exportReport('pdf')}>
            📄 PDF Export
          </button>
        </div>
      </header>

      {/* Filters */}
      <div className="filters-card">
        <div className="filter-group">
          <label>Von</label>
          <input
            type="date"
            value={filters.start_date}
            onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
          />
        </div>
        <div className="filter-group">
          <label>Bis</label>
          <input
            type="date"
            value={filters.end_date}
            onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
          />
        </div>
        <div className="filter-group">
          <label>Gruppierung</label>
          <select
            value={filters.groupBy}
            onChange={(e) =>
              setFilters({ ...filters, groupBy: e.target.value as 'day' | 'week' | 'month' })
            }
          >
            <option value="day">Täglich</option>
            <option value="week">Wöchentlich</option>
            <option value="month">Monatlich</option>
          </select>
        </div>
        <div className="filter-group">
          <button
            className="btn btn-primary"
            onClick={() =>
              setFilters({
                start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
                  .toISOString()
                  .split('T')[0],
                end_date: new Date().toISOString().split('T')[0],
                groupBy: 'day',
              })
            }
          >
            Letzte 30 Tage
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="loading">Lade Berichte...</div>
      ) : report ? (
        <>
          {/* Summary Cards */}
          <div className="summary-grid">
            <SummaryCard
              title="Gesamtumsatz"
              value={formatCurrency(report.total_sales)}
              icon="💰"
              color="#10b981"
            />
            <SummaryCard
              title="Transaktionen"
              value={report.total_transactions}
              icon="🛒"
              color="#3b82f6"
            />
            <SummaryCard
              title="Ø Warenkorbwert"
              value={formatCurrency(report.average_basket)}
              icon="📊"
              color="#8b5cf6"
            />
          </div>

          <div className="reports-grid">
            {/* Sales by Payment Method */}
            <div className="card">
              <h2>Umsatz nach Zahlungsmethode</h2>
              <div className="payment-methods">
                <PaymentMethodBar
                  label="Bargeld"
                  amount={report.sales_by_payment_method.cash}
                  total={report.total_sales}
                  color="#10b981"
                />
                <PaymentMethodBar
                  label="Karte"
                  amount={report.sales_by_payment_method.card}
                  total={report.total_sales}
                  color="#3b82f6"
                />
                <PaymentMethodBar
                  label="SumUp"
                  amount={report.sales_by_payment_method.sumup}
                  total={report.total_sales}
                  color="#8b5cf6"
                />
              </div>
            </div>

            {/* Sales by Day */}
            <div className="card">
              <h2>Umsatz über Zeit</h2>
              <div className="chart">
                {report.sales_by_day.map((day) => (
                  <div key={day.date} className="chart-bar">
                    <div className="bar-container">
                      <div
                        className="bar"
                        style={{
                          height: `${
                            (day.sales / Math.max(...report.sales_by_day.map((d) => d.sales))) *
                            100
                          }%`,
                        }}
                      >
                        <span className="bar-value">{formatCurrency(day.sales)}</span>
                      </div>
                    </div>
                    <div className="bar-label">
                      {new Date(day.date).toLocaleDateString('de-DE', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Products */}
            <div className="card">
              <h2>Top Produkte</h2>
              <div className="top-products">
                {report.top_products.map((product, index) => (
                  <div key={product.product_id} className="product-item">
                    <div className="product-rank">#{index + 1}</div>
                    <div className="product-info">
                      <div className="product-name">{product.product_name}</div>
                      <div className="product-stats">
                        {product.quantity_sold}x verkauft
                      </div>
                    </div>
                    <div className="product-sales">{formatCurrency(product.total_sales)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Sales by Hour */}
            <div className="card">
              <h2>Umsatz nach Tageszeit</h2>
              <div className="hourly-chart">
                {report.sales_by_hour.map((hour) => (
                  <div key={hour.hour} className="hourly-bar">
                    <div
                      className="bar"
                      style={{
                        height: `${
                          (hour.sales / Math.max(...report.sales_by_hour.map((h) => h.sales))) *
                          100
                        }%`,
                      }}
                      title={`${hour.hour}:00 - ${formatCurrency(hour.sales)}`}
                    />
                    <div className="hour-label">{hour.hour}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      ) : null}

      <style>{`
        .reports-page {
          max-width: 1400px;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
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

        .export-buttons {
          display: flex;
          gap: 0.75rem;
        }

        .filters-card {
          background: white;
          border-radius: 0.5rem;
          padding: 1.5rem;
          margin-bottom: 2rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
          align-items: flex-end;
        }

        .filter-group {
          flex: 1;
          min-width: 150px;
        }

        .filter-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
          color: #374151;
        }

        .filter-group input,
        .filter-group select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          font-size: 1rem;
        }

        .summary-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .reports-grid {
          display: grid;
          gap: 1.5rem;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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

        .payment-methods {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .chart {
          display: flex;
          gap: 0.5rem;
          align-items: flex-end;
          height: 200px;
        }

        .chart-bar {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .bar-container {
          flex: 1;
          width: 100%;
          display: flex;
          align-items: flex-end;
        }

        .bar {
          width: 100%;
          background: linear-gradient(to top, #10b981, #34d399);
          border-radius: 0.25rem 0.25rem 0 0;
          position: relative;
          min-height: 20px;
          transition: all 0.3s;
        }

        .bar:hover {
          opacity: 0.8;
        }

        .bar-value {
          position: absolute;
          top: -1.5rem;
          left: 50%;
          transform: translateX(-50%);
          font-size: 0.75rem;
          font-weight: 600;
          white-space: nowrap;
        }

        .bar-label {
          margin-top: 0.5rem;
          font-size: 0.75rem;
          color: #6b7280;
          text-align: center;
        }

        .top-products {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .product-item {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          background: #f9fafb;
          border-radius: 0.375rem;
        }

        .product-rank {
          font-size: 1.5rem;
          font-weight: 700;
          color: #10b981;
          min-width: 2.5rem;
          text-align: center;
        }

        .product-info {
          flex: 1;
        }

        .product-name {
          font-weight: 600;
          color: #1a1a2e;
          margin-bottom: 0.25rem;
        }

        .product-stats {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .product-sales {
          font-weight: 600;
          font-size: 1.125rem;
          color: #10b981;
        }

        .hourly-chart {
          display: flex;
          gap: 0.25rem;
          align-items: flex-end;
          height: 150px;
        }

        .hourly-bar {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          height: 100%;
        }

        .hourly-bar .bar {
          width: 100%;
          background: linear-gradient(to top, #3b82f6, #60a5fa);
          border-radius: 0.25rem 0.25rem 0 0;
          min-height: 10px;
        }

        .hour-label {
          margin-top: 0.25rem;
          font-size: 0.625rem;
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

        .btn-primary:hover {
          background: #059669;
        }

        .btn-secondary {
          background: #e5e7eb;
          color: #374151;
        }

        .btn-secondary:hover {
          background: #d1d5db;
        }

        .loading {
          text-align: center;
          padding: 3rem;
          color: #6b7280;
        }

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            gap: 1rem;
          }

          .reports-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  )
}

interface SummaryCardProps {
  title: string
  value: string | number
  icon: string
  color: string
}

function SummaryCard({ title, value, icon, color }: SummaryCardProps) {
  return (
    <div className="summary-card" style={{ borderTopColor: color }}>
      <div className="summary-icon" style={{ color }}>
        {icon}
      </div>
      <div className="summary-content">
        <div className="summary-title">{title}</div>
        <div className="summary-value" style={{ color }}>
          {value}
        </div>
      </div>
      <style>{`
        .summary-card {
          background: white;
          border-radius: 0.5rem;
          padding: 1.5rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          border-top: 4px solid;
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .summary-icon {
          font-size: 2.5rem;
        }

        .summary-content {
          flex: 1;
        }

        .summary-title {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .summary-value {
          font-size: 1.875rem;
          font-weight: 700;
          font-variant-numeric: tabular-nums;
        }
      `}</style>
    </div>
  )
}

interface PaymentMethodBarProps {
  label: string
  amount: number
  total: number
  color: string
}

function PaymentMethodBar({ label, amount, total, color }: PaymentMethodBarProps) {
  const percentage = total > 0 ? (amount / total) * 100 : 0

  return (
    <div className="payment-method-bar">
      <div className="method-header">
        <span className="method-label">{label}</span>
        <span className="method-amount">{formatCurrency(amount)}</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${percentage}%`, backgroundColor: color }}>
          <span className="progress-text">{percentage.toFixed(1)}%</span>
        </div>
      </div>
      <style>{`
        .payment-method-bar {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .method-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .method-label {
          font-weight: 500;
          color: #374151;
        }

        .method-amount {
          font-weight: 600;
          color: #1a1a2e;
        }

        .progress-bar {
          height: 2rem;
          background: #e5e7eb;
          border-radius: 0.375rem;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: flex-end;
          padding: 0 0.75rem;
          transition: width 0.3s;
        }

        .progress-text {
          color: white;
          font-weight: 600;
          font-size: 0.875rem;
        }
      `}</style>
    </div>
  )
}
