import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { BarChart3, TrendingUp, TrendingDown, DollarSign, Users, ShoppingCart } from 'lucide-react'
import { useKPIs } from '@/hooks/useAnalytics'

export function AnalyticsDashboard() {
  const { data: kpis, isLoading, error, refetch } = useKPIs('today')

  if (isLoading) return <LoadingState message="Lade Analytics..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getTrendIcon = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />
      default:
        return null
    }
  }

  const getTrendColor = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
          <p className="text-muted-foreground">Übersicht über wichtige Kennzahlen</p>
        </div>
        <Button variant="outline">
          Zeitraum: Heute
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {kpis?.map((kpi) => (
          <Card key={kpi.metric_name} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">{kpi.metric_name}</p>
                <p className="text-3xl font-bold">
                  {kpi.metric_value}
                  {kpi.metric_unit && <span className="text-lg ml-1">{kpi.metric_unit}</span>}
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                {kpi.metric_name.includes('Umsatz') && <DollarSign className="h-6 w-6 text-blue-600" />}
                {kpi.metric_name.includes('Kunde') && <Users className="h-6 w-6 text-blue-600" />}
                {kpi.metric_name.includes('Bestellung') && <ShoppingCart className="h-6 w-6 text-blue-600" />}
                {!kpi.metric_name.includes('Umsatz') && !kpi.metric_name.includes('Kunde') && !kpi.metric_name.includes('Bestellung') && (
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                )}
              </div>
            </div>

            {kpi.previous_value !== null && kpi.previous_value !== undefined && kpi.change_percentage !== null && kpi.change_percentage !== undefined && (
              <div className="flex items-center gap-2">
                {getTrendIcon(kpi.trend)}
                <span className={`text-sm font-medium ${getTrendColor(kpi.trend)}`}>
                  {kpi.change_percentage > 0 ? '+' : ''}
                  {kpi.change_percentage.toFixed(1)}%
                </span>
                <span className="text-sm text-muted-foreground">vs. gestern</span>
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Mock Charts Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Umsatzentwicklung</h2>
          <div className="h-64 flex items-center justify-center bg-muted/50 rounded-lg">
            <p className="text-muted-foreground">Umsatz-Chart (Integration mit Recharts)</p>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Top Produkte</h2>
          <div className="h-64 flex items-center justify-center bg-muted/50 rounded-lg">
            <p className="text-muted-foreground">Produkt-Chart (Integration mit Recharts)</p>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Kundenverteilung</h2>
          <div className="h-64 flex items-center justify-center bg-muted/50 rounded-lg">
            <p className="text-muted-foreground">Kunden-Chart (Integration mit Recharts)</p>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Bestellungen nach Stunde</h2>
          <div className="h-64 flex items-center justify-center bg-muted/50 rounded-lg">
            <p className="text-muted-foreground">Bestellungs-Chart (Integration mit Recharts)</p>
          </div>
        </Card>
      </div>
    </div>
  )
}
