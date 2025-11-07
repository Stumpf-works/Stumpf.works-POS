import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, User, Phone, Car, MapPin, Star } from 'lucide-react'
import { useDrivers } from '@/hooks/useDelivery'
import { DriverStatus } from '@/types/plugins'

export function DriverManagement() {
  const { data: drivers, isLoading, error, refetch } = useDrivers()

  if (isLoading) return <LoadingState message="Lade Fahrer..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getStatusVariant = (status: DriverStatus) => {
    switch (status) {
      case 'available':
        return 'default'
      case 'busy':
        return 'secondary'
      case 'offline':
        return 'outline'
      default:
        return 'outline'
    }
  }

  const getStatusLabel = (status: DriverStatus) => {
    const labels: Record<DriverStatus, string> = {
      available: 'Verfügbar',
      busy: 'Beschäftigt',
      offline: 'Offline',
    }
    return labels[status]
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Fahrerverwaltung</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Fahrer hinzufügen
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Verfügbar</p>
          <p className="text-3xl font-bold text-green-600">
            {drivers?.filter((d) => d.status === 'available').length || 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Beschäftigt</p>
          <p className="text-3xl font-bold text-yellow-600">
            {drivers?.filter((d) => d.status === 'busy').length || 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Offline</p>
          <p className="text-3xl font-bold text-gray-600">
            {drivers?.filter((d) => d.status === 'offline').length || 0}
          </p>
        </Card>
      </div>

      {/* Driver Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {drivers?.map((driver) => (
          <Card key={driver.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  <User className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold">{driver.driver_name}</h3>
                  {driver.rating && (
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3 text-yellow-600 fill-yellow-600" />
                      <span className="text-sm">{driver.rating.toFixed(1)}</span>
                    </div>
                  )}
                </div>
              </div>
              <Badge variant={getStatusVariant(driver.status)}>
                {getStatusLabel(driver.status)}
              </Badge>
            </div>

            <div className="space-y-2 text-sm mb-4">
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <span>{driver.phone}</span>
              </div>
              <div className="flex items-center gap-2">
                <Car className="h-4 w-4 text-muted-foreground" />
                <span>
                  {driver.vehicle_type}
                  {driver.vehicle_number && ` - ${driver.vehicle_number}`}
                </span>
              </div>
              {driver.last_location_update && (
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">
                    Zuletzt: {new Date(driver.last_location_update).toLocaleTimeString('de-DE')}
                  </span>
                </div>
              )}
            </div>

            <div className="p-3 bg-muted/50 rounded-lg">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Lieferungen</span>
                <span className="font-semibold">{driver.total_deliveries}</span>
              </div>
              {driver.active_delivery_id && (
                <p className="text-xs text-muted-foreground mt-1">
                  Aktive Lieferung: #{driver.active_delivery_id}
                </p>
              )}
            </div>

            <Button variant="outline" size="sm" className="w-full mt-3">
              Details
            </Button>
          </Card>
        ))}
      </div>
    </div>
  )
}
