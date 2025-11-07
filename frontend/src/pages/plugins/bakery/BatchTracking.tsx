import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Package, Calendar, User, AlertCircle } from 'lucide-react'
import { useBatches } from '@/hooks/useBakery'
import { BatchStatus } from '@/types/plugins'

export function BatchTracking() {
  const [filter, setFilter] = useState<BatchStatus | 'all'>('all')
  const { data: batches, isLoading, error, refetch } = useBatches(
    filter === 'all' ? undefined : filter
  )

  if (isLoading) return <LoadingState message="Lade Chargen..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getStatusVariant = (status: BatchStatus) => {
    switch (status) {
      case 'planned':
        return 'secondary'
      case 'in_production':
        return 'default'
      case 'baking':
        return 'outline'
      case 'cooling':
        return 'outline'
      case 'completed':
        return 'outline'
      default:
        return 'outline'
    }
  }

  const getStatusLabel = (status: BatchStatus) => {
    const labels: Record<BatchStatus, string> = {
      planned: 'Geplant',
      in_production: 'In Produktion',
      baking: 'Backen',
      cooling: 'Abkühlen',
      completed: 'Fertig',
    }
    return labels[status]
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Chargenverfolgung</h1>
      </div>

      {/* Status Filter */}
      <Card className="p-4">
        <div className="flex gap-2">
          <Button variant={filter === 'all' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('all')}>
            Alle
          </Button>
          <Button variant={filter === 'planned' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('planned')}>
            Geplant
          </Button>
          <Button variant={filter === 'in_production' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('in_production')}>
            In Produktion
          </Button>
          <Button variant={filter === 'baking' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('baking')}>
            Backen
          </Button>
          <Button variant={filter === 'completed' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('completed')}>
            Fertig
          </Button>
        </div>
      </Card>

      {/* Batch Cards */}
      <div className="space-y-3">
        {batches?.map((batch) => (
          <Card key={batch.id} className="p-4">
            <div className="flex flex-col md:flex-row justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <Package className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{batch.recipe_name}</h3>
                      <Badge variant={getStatusVariant(batch.status)}>
                        {getStatusLabel(batch.status)}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground font-mono">
                      Charge #{batch.batch_number}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground mb-1">Produktionsdatum</p>
                    <p className="font-medium flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {new Date(batch.production_date).toLocaleDateString('de-DE')}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground mb-1">Uhrzeit</p>
                    <p className="font-medium">{batch.production_time}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground mb-1">Menge</p>
                    <p className="font-medium">
                      {batch.quantity_produced || batch.quantity_planned}
                    </p>
                  </div>
                  {batch.expiry_date && (
                    <div>
                      <p className="text-muted-foreground mb-1">Verfallsdatum</p>
                      <p className="font-medium">
                        {new Date(batch.expiry_date).toLocaleDateString('de-DE')}
                      </p>
                    </div>
                  )}
                </div>

                {batch.produced_by_user_name && (
                  <div className="mt-3 flex items-center gap-2 text-sm">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      Produziert von: {batch.produced_by_user_name}
                    </span>
                  </div>
                )}

                {batch.notes && (
                  <div className="mt-3 p-2 bg-yellow-50 rounded">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-yellow-600" />
                      <p className="text-sm text-yellow-900">{batch.notes}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2 min-w-[120px]">
                {batch.qr_code && (
                  <Button variant="outline" size="sm">QR-Code</Button>
                )}
                <Button variant="outline" size="sm">Details</Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {!batches || batches.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Chargen gefunden</p>
        </Card>
      )}
    </div>
  )
}
