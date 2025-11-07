import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, DollarSign, Lock, Unlock } from 'lucide-react'
import { useCashRegisters } from '@/hooks/useCash'

export function CashRegisterList() {
  const { data: registers, isLoading, error, refetch } = useCashRegisters()

  if (isLoading) return <LoadingState message="Lade Kassen..." />
  if (error) return <ErrorState message="Fehler beim Laden der Kassen" onRetry={() => refetch()} />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Kassenregister</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Kasse hinzufügen
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {registers?.map((register) => (
          <Card key={register.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-100 rounded-full">
                  <DollarSign className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{register.register_name}</h3>
                  <p className="text-sm text-muted-foreground">{register.location}</p>
                </div>
              </div>
              {register.status === 'open' ? (
                <Unlock className="h-5 w-5 text-green-600" />
              ) : (
                <Lock className="h-5 w-5 text-gray-400" />
              )}
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Kassennummer</span>
                <span className="font-medium font-mono">{register.register_number}</span>
              </div>

              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Status</span>
                <Badge variant={register.status === 'open' ? 'default' : 'secondary'}>
                  {register.status === 'open' ? 'Geöffnet' : 'Geschlossen'}
                </Badge>
              </div>

              {register.current_session_id && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-xs text-muted-foreground mb-1">Aktive Sitzung</p>
                  <p className="text-sm font-medium">Sitzung #{register.current_session_id}</p>
                </div>
              )}
            </div>

            <div className="flex gap-2">
              {register.status === 'closed' ? (
                <Button variant="default" className="flex-1">
                  Sitzung öffnen
                </Button>
              ) : (
                <Button variant="outline" className="flex-1">
                  Sitzung schließen
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
