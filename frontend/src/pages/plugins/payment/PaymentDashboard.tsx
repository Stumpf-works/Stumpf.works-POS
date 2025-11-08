import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { TrendingUp, CreditCard, DollarSign, AlertCircle } from 'lucide-react'
import { usePaymentProviders, usePaymentTransactions, usePaymentTerminals } from '@/hooks/usePayment'

export function PaymentDashboard() {
  const { data: providers, isLoading: providersLoading, error: providersError } = usePaymentProviders()
  const { data: transactions, isLoading: transactionsLoading, error: transactionsError } = usePaymentTransactions()
  const { data: terminals, isLoading: terminalsLoading, error: terminalsError } = usePaymentTerminals()

  const isLoading = providersLoading || transactionsLoading || terminalsLoading
  const error = providersError || transactionsError || terminalsError

  if (isLoading) return <LoadingState message="Lade Dashboard..." />
  if (error) return <ErrorState message="Fehler beim Laden des Dashboards" />

  // Calculate metrics
  const activeProviders = providers?.filter((p) => p.is_active).length || 0
  const totalTransactions = transactions?.length || 0
  const totalRevenue = transactions?.reduce((sum, t) => sum + t.amount, 0) || 0
  const successfulTransactions = transactions?.filter((t) => t.status === 'completed').length || 0
  const successRate = totalTransactions > 0 ? (successfulTransactions / totalTransactions) * 100 : 0
  const onlineTerminals = terminals?.filter((t) => t.is_online).length || 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Payment Gateway Dashboard</h1>
          <p className="text-muted-foreground">Übersicht über alle Zahlungsaktivitäten</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Gesamtumsatz</p>
              <p className="text-3xl font-bold">{totalRevenue.toFixed(2)} €</p>
              <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                <TrendingUp className="h-4 w-4" />
                <span>+12.5%</span>
              </div>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <DollarSign className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Transaktionen</p>
              <p className="text-3xl font-bold">{totalTransactions}</p>
              <p className="text-sm text-muted-foreground mt-2">
                {successfulTransactions} erfolgreich
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <CreditCard className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Erfolgsrate</p>
              <p className="text-3xl font-bold">{successRate.toFixed(1)}%</p>
              <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                <TrendingUp className="h-4 w-4" />
                <span>+2.3%</span>
              </div>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Aktive Anbieter</p>
              <p className="text-3xl font-bold">{activeProviders}</p>
              <p className="text-sm text-muted-foreground mt-2">
                {onlineTerminals} Terminals online
              </p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <CreditCard className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Provider Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Anbieter-Status</h2>
          <div className="space-y-3">
            {providers?.map((provider) => (
              <div key={provider.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">
                    {provider.provider_type === 'stripe' && '💳'}
                    {provider.provider_type === 'paypal' && '🅿️'}
                    {provider.provider_type === 'square' && '⬛'}
                    {provider.provider_type === 'sumup' && '🔷'}
                  </div>
                  <div>
                    <p className="font-medium">{provider.provider_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {provider.transaction_fee_percentage}% + {provider.transaction_fee_fixed}€
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={provider.is_active ? 'default' : 'secondary'}>
                    {provider.is_active ? 'Aktiv' : 'Inaktiv'}
                  </Badge>
                  {provider.health_status !== 'healthy' && (
                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Kürzliche Transaktionen</h2>
          <div className="space-y-3">
            {transactions?.slice(0, 5).map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex-1">
                  <p className="font-mono text-sm">{transaction.transaction_id}</p>
                  <p className="text-xs text-muted-foreground">{transaction.provider_name}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="font-semibold">{transaction.amount.toFixed(2)} €</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(transaction.created_at).toLocaleTimeString('de-DE')}
                    </p>
                  </div>
                  <Badge
                    variant={
                      transaction.status === 'completed'
                        ? 'default'
                        : transaction.status === 'failed'
                        ? 'destructive'
                        : 'secondary'
                    }
                  >
                    {transaction.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Terminal Status */}
      {terminals && terminals.length > 0 && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Terminal-Übersicht</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {terminals.map((terminal) => (
              <div key={terminal.id} className="p-4 bg-muted/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium">{terminal.terminal_id}</p>
                  <Badge variant={terminal.is_online ? 'default' : 'secondary'}>
                    {terminal.connection_status}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{terminal.location_name}</p>
                {terminal.last_seen_at && (
                  <p className="text-xs text-muted-foreground mt-1">
                    Zuletzt: {new Date(terminal.last_seen_at).toLocaleString('de-DE')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
