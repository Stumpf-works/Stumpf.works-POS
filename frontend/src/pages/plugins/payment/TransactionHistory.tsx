import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Download, Search, RefreshCcw, Eye } from 'lucide-react'
import { usePaymentTransactions } from '@/hooks/usePayment'
import { PaymentStatus } from '@/types/plugins'

export function TransactionHistory() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filter, setFilter] = useState<PaymentStatus | 'all'>('all')

  const { data: transactions, isLoading, error, refetch } = usePaymentTransactions(
    filter === 'all' ? undefined : { status: filter }
  )

  const getStatusVariant = (status: PaymentStatus) => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'processing':
        return 'secondary'
      case 'pending':
        return 'outline'
      case 'failed':
        return 'destructive'
      case 'refunded':
      case 'partially_refunded':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const getStatusLabel = (status: PaymentStatus) => {
    const labels: Record<PaymentStatus, string> = {
      pending: 'Ausstehend',
      processing: 'In Bearbeitung',
      completed: 'Erfolgreich',
      failed: 'Fehlgeschlagen',
      refunded: 'Erstattet',
      partially_refunded: 'Teilweise erstattet',
    }
    return labels[status] || status
  }

  const filteredTransactions = transactions?.filter(
    (t) =>
      t.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.customer_email?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (isLoading) return <LoadingState message="Lade Transaktionen..." />
  if (error) return <ErrorState message="Fehler beim Laden der Transaktionen" onRetry={() => refetch()} />

  // Calculate stats
  const totalAmount = transactions?.reduce((sum, t) => sum + t.amount, 0) || 0
  const successCount = transactions?.filter((t) => t.status === 'completed').length || 0
  const pendingCount = transactions?.filter((t) => t.status === 'pending').length || 0
  const failedCount = transactions?.filter((t) => t.status === 'failed').length || 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transaktionen</h1>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Exportieren
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Gesamt</p>
          <p className="text-2xl font-bold">{totalAmount.toFixed(2)} €</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Erfolgreich</p>
          <p className="text-2xl font-bold text-green-600">{successCount}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Ausstehend</p>
          <p className="text-2xl font-bold text-yellow-600">{pendingCount}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Fehlgeschlagen</p>
          <p className="text-2xl font-bold text-red-600">{failedCount}</p>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Suche nach Transaktionsnummer oder Email..."
              className="pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as PaymentStatus | 'all')}
            className="border rounded px-3 py-2 bg-background"
          >
            <option value="all">Alle Status</option>
            <option value="completed">Erfolgreich</option>
            <option value="pending">Ausstehend</option>
            <option value="failed">Fehlgeschlagen</option>
            <option value="refunded">Erstattet</option>
          </select>

          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCcw className="h-4 w-4" />
          </Button>
        </div>
      </Card>

      {/* Transactions List */}
      <div className="space-y-3">
        {filteredTransactions?.map((transaction) => (
          <Card key={transaction.id} className="p-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-mono font-semibold">{transaction.transaction_id}</span>
                  <Badge variant={getStatusVariant(transaction.status)}>
                    {getStatusLabel(transaction.status)}
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>Anbieter: {transaction.provider_name}</p>
                  <p>Zahlungsmethode: {transaction.payment_method}</p>
                  {transaction.customer_email && <p>Email: {transaction.customer_email}</p>}
                  {transaction.error_message && (
                    <p className="text-red-600">Fehler: {transaction.error_message}</p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-2xl font-bold">
                    {transaction.amount.toFixed(2)} {transaction.currency}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(transaction.created_at).toLocaleString('de-DE')}
                  </p>
                </div>

                <Button variant="ghost" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredTransactions?.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <p>Keine Transaktionen gefunden</p>
        </Card>
      )}
    </div>
  )
}
