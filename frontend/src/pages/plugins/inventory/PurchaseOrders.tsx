import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, FileText, Calendar } from 'lucide-react'
import { usePurchaseOrders } from '@/hooks/useInventory'
import { PurchaseOrderStatus } from '@/types/plugins'

export function PurchaseOrders() {
  const [filter, setFilter] = useState<PurchaseOrderStatus | 'all'>('all')
  const { data: orders, isLoading, error, refetch } = usePurchaseOrders(
    filter === 'all' ? undefined : filter
  )

  if (isLoading) return <LoadingState message="Lade Bestellungen..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getStatusVariant = (status: PurchaseOrderStatus) => {
    switch (status) {
      case 'draft':
        return 'secondary'
      case 'sent':
        return 'default'
      case 'partial':
        return 'outline'
      case 'received':
        return 'outline'
      case 'cancelled':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  const getStatusLabel = (status: PurchaseOrderStatus) => {
    const labels: Record<PurchaseOrderStatus, string> = {
      draft: 'Entwurf',
      sent: 'Gesendet',
      partial: 'Teilweise empfangen',
      received: 'Empfangen',
      cancelled: 'Storniert',
    }
    return labels[status]
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Bestellungen</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Neue Bestellung
        </Button>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex gap-2">
          <Button variant={filter === 'all' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('all')}>
            Alle
          </Button>
          <Button variant={filter === 'draft' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('draft')}>
            Entwürfe
          </Button>
          <Button variant={filter === 'sent' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('sent')}>
            Gesendet
          </Button>
          <Button variant={filter === 'partial' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('partial')}>
            Teilweise
          </Button>
          <Button variant={filter === 'received' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('received')}>
            Empfangen
          </Button>
        </div>
      </Card>

      {/* Orders */}
      <div className="space-y-3">
        {orders?.map((order) => (
          <Card key={order.id} className="p-4">
            <div className="flex flex-col md:flex-row justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <h3 className="font-semibold">PO #{order.po_number}</h3>
                    <p className="text-sm text-muted-foreground">{order.supplier_name}</p>
                  </div>
                  <Badge variant={getStatusVariant(order.status)}>
                    {getStatusLabel(order.status)}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground mb-1">Bestelldatum</p>
                    <p className="font-medium flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {new Date(order.order_date).toLocaleDateString('de-DE')}
                    </p>
                  </div>
                  {order.expected_delivery_date && (
                    <div>
                      <p className="text-muted-foreground mb-1">Erwartete Lieferung</p>
                      <p className="font-medium">
                        {new Date(order.expected_delivery_date).toLocaleDateString('de-DE')}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-muted-foreground mb-1">Artikel</p>
                    <p className="font-medium">{order.items.length}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground mb-1">Gesamtbetrag</p>
                    <p className="font-semibold text-lg">{order.total_amount.toFixed(2)} €</p>
                  </div>
                </div>

                {order.notes && (
                  <div className="mt-3 p-2 bg-muted/50 rounded text-sm">
                    <p className="text-muted-foreground">{order.notes}</p>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2 min-w-[120px]">
                <Button variant="outline" size="sm">Details</Button>
                {order.status === 'sent' && (
                  <Button variant="default" size="sm">Empfangen</Button>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {!orders || orders.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Bestellungen gefunden</p>
        </Card>
      )}
    </div>
  )
}
