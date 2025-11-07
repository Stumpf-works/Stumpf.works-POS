import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Truck, MapPin, Clock, TrendingUp } from 'lucide-react'
import { useDeliveryOrders, useDrivers } from '@/hooks/useDelivery'

export function DeliveryDashboard() {
  const { data: orders, isLoading: ordersLoading, error: ordersError } = useDeliveryOrders()
  const { data: drivers, isLoading: driversLoading, error: driversError } = useDrivers()

  const isLoading = ordersLoading || driversLoading
  const error = ordersError || driversError

  if (isLoading) return <LoadingState message="Lade Dashboard..." />
  if (error) return <ErrorState message="Fehler beim Laden" />

  const activeOrders = orders?.filter((o) => ['assigned', 'picked_up', 'in_transit'].includes(o.status)) || []
  const availableDrivers = drivers?.filter((d) => d.status === 'available') || []
  const avgDeliveryTime = 35 // Mock - calculate from completed orders

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Lieferübersicht</h1>
          <p className="text-muted-foreground">{activeOrders.length} aktive Lieferungen</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Aktive Lieferungen</p>
              <p className="text-3xl font-bold">{activeOrders.length}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <Truck className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Verfügbare Fahrer</p>
              <p className="text-3xl font-bold">{availableDrivers.length}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <MapPin className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Ø Lieferzeit</p>
              <p className="text-3xl font-bold">{avgDeliveryTime} min</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Clock className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Heute gesamt</p>
              <p className="text-3xl font-bold">{orders?.length || 0}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Deliveries */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Aktive Lieferungen</h2>
          <div className="space-y-3">
            {activeOrders.slice(0, 5).map((order) => (
              <div key={order.id} className="p-3 bg-muted/50 rounded-lg">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-semibold">#{order.order_number}</p>
                    <p className="text-sm text-muted-foreground">{order.customer_name}</p>
                  </div>
                  <Badge variant={
                    order.status === 'in_transit' ? 'default' :
                    order.status === 'picked_up' ? 'secondary' : 'outline'
                  }>
                    {order.status === 'in_transit' ? 'Unterwegs' :
                     order.status === 'picked_up' ? 'Abgeholt' : 'Zugewiesen'}
                  </Badge>
                </div>
                {order.driver_name && (
                  <p className="text-sm text-muted-foreground">
                    Fahrer: {order.driver_name}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Available Drivers */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Verfügbare Fahrer</h2>
          <div className="space-y-3">
            {availableDrivers.slice(0, 5).map((driver) => (
              <div key={driver.id} className="p-3 bg-muted/50 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{driver.driver_name}</p>
                    <p className="text-sm text-muted-foreground">{driver.vehicle_type}</p>
                  </div>
                  <Badge variant="default">Verfügbar</Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {driver.total_deliveries} Lieferungen
                </p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
