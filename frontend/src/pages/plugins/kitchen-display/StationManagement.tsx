import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Settings, ChefHat } from 'lucide-react'
import { useKitchenStations } from '@/hooks/useKitchenDisplay'

export function StationManagement() {
  const { data: stations, isLoading, error, refetch } = useKitchenStations()

  if (isLoading) return <LoadingState message="Lade Stationen..." />
  if (error) return <ErrorState message="Fehler beim Laden der Stationen" onRetry={() => refetch()} />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Küchenstationen</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Station hinzufügen
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stations?.map((station) => (
          <Card key={station.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-orange-100 rounded-full">
                  <ChefHat className="h-6 w-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{station.station_name}</h3>
                  <p className="text-sm text-muted-foreground font-mono">{station.station_code}</p>
                </div>
              </div>
              <Badge variant={station.is_active ? 'default' : 'secondary'}>
                {station.is_active ? 'Aktiv' : 'Inaktiv'}
              </Badge>
            </div>

            {station.description && (
              <p className="text-sm text-muted-foreground mb-4">{station.description}</p>
            )}

            <div className="flex justify-between items-center mb-4">
              <span className="text-sm text-muted-foreground">Anzeigereihenfolge</span>
              <span className="font-medium">{station.display_order}</span>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="flex-1">
                <Settings className="mr-2 h-4 w-4" />
                Einstellungen
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {!stations || stations.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <ChefHat className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Stationen konfiguriert</p>
          <Button variant="link" className="mt-2">
            Erste Station erstellen
          </Button>
        </Card>
      )}
    </div>
  )
}
