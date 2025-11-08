import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Clock, AlertCircle, ChefHat, Play, Check } from 'lucide-react'
import { useKitchenOrders, useStartOrder, useCompleteOrder } from '@/hooks/useKitchenDisplay'
import { OrderPriority } from '@/types/plugins'

export function KitchenDisplay() {
  const [selectedStation] = useState<number>()
  const { data: orders, isLoading, error, refetch } = useKitchenOrders(selectedStation, undefined)
  const startOrder = useStartOrder()
  const completeOrder = useCompleteOrder()

  if (isLoading) return <LoadingState message="Lade Bestellungen..." />
  if (error) return <ErrorState message="Fehler beim Laden der Bestellungen" onRetry={() => refetch()} />

  const getPriorityColor = (priority: OrderPriority) => {
    switch (priority) {
      case 'urgent':
        return 'border-red-500 bg-red-50'
      case 'high':
        return 'border-orange-500 bg-orange-50'
      default:
        return 'border-gray-300 bg-white'
    }
  }

  // Unused function - kept for future use
  // const getStatusColor = (status: OrderStatus) => {
  //   switch (status) {
  //     case 'new':
  //       return 'bg-blue-600'
  //     case 'preparing':
  //       return 'bg-yellow-600'
  //     case 'ready':
  //       return 'bg-green-600'
  //     case 'served':
  //       return 'bg-gray-600'
  //     default:
  //       return 'bg-gray-400'
  //   }
  // }

  const getElapsedTime = (createdAt: string) => {
    const elapsed = Math.floor((Date.now() - new Date(createdAt).getTime()) / 1000 / 60)
    return elapsed
  }

  // Group orders by status
  const newOrders = orders?.filter((o) => o.status === 'new') || []
  const preparingOrders = orders?.filter((o) => o.status === 'preparing') || []
  const readyOrders = orders?.filter((o) => o.status === 'ready') || []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <ChefHat className="h-8 w-8" />
          <div>
            <h1 className="text-2xl font-bold">Küchen-Display</h1>
            <p className="text-sm text-muted-foreground">
              {orders?.length || 0} aktive Bestellungen
            </p>
          </div>
        </div>
        <div className="text-2xl font-mono font-bold">
          {new Date().toLocaleTimeString('de-DE')}
        </div>
      </div>

      {/* Columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* New Orders */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 rounded-full bg-blue-600"></div>
            <h2 className="text-lg font-semibold">Neu ({newOrders.length})</h2>
          </div>
          <div className="space-y-3">
            {newOrders.map((order) => (
              <Card
                key={order.id}
                className={`p-4 border-2 ${getPriorityColor(order.priority)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-xl">#{order.order_number}</span>
                      {order.priority !== 'normal' && (
                        <Badge variant="destructive" className="uppercase text-xs">
                          {order.priority}
                        </Badge>
                      )}
                    </div>
                    {order.table_number && (
                      <p className="text-sm text-muted-foreground">Tisch {order.table_number}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-sm font-semibold">
                      <Clock className="h-4 w-4" />
                      {getElapsedTime(order.created_at)} min
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {order.estimated_time_minutes} min geschätzt
                    </p>
                  </div>
                </div>

                <div className="space-y-2 mb-3">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span className="font-medium">
                        {item.quantity}x {item.product_name}
                      </span>
                      {item.notes && (
                        <span className="text-muted-foreground italic">{item.notes}</span>
                      )}
                    </div>
                  ))}
                </div>

                {order.notes && (
                  <div className="p-2 bg-yellow-100 rounded text-sm mb-3">
                    <AlertCircle className="h-4 w-4 inline mr-1" />
                    {order.notes}
                  </div>
                )}

                <Button
                  variant="default"
                  className="w-full"
                  onClick={() => startOrder.mutate(order.id)}
                >
                  <Play className="mr-2 h-4 w-4" />
                  Starten
                </Button>
              </Card>
            ))}
          </div>
        </div>

        {/* Preparing Orders */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 rounded-full bg-yellow-600"></div>
            <h2 className="text-lg font-semibold">In Zubereitung ({preparingOrders.length})</h2>
          </div>
          <div className="space-y-3">
            {preparingOrders.map((order) => (
              <Card
                key={order.id}
                className={`p-4 border-2 ${getPriorityColor(order.priority)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-xl">#{order.order_number}</span>
                      {order.priority !== 'normal' && (
                        <Badge variant="destructive" className="uppercase text-xs">
                          {order.priority}
                        </Badge>
                      )}
                    </div>
                    {order.table_number && (
                      <p className="text-sm text-muted-foreground">Tisch {order.table_number}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div
                      className={`flex items-center gap-1 text-sm font-semibold ${
                        getElapsedTime(order.created_at) > order.estimated_time_minutes
                          ? 'text-red-600'
                          : ''
                      }`}
                    >
                      <Clock className="h-4 w-4" />
                      {getElapsedTime(order.created_at)} min
                    </div>
                    {order.started_at && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Gestartet: {new Date(order.started_at).toLocaleTimeString('de-DE')}
                      </p>
                    )}
                  </div>
                </div>

                <div className="space-y-2 mb-3">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span className="font-medium">
                        {item.quantity}x {item.product_name}
                      </span>
                    </div>
                  ))}
                </div>

                <Button
                  variant="default"
                  className="w-full bg-green-600 hover:bg-green-700"
                  onClick={() => completeOrder.mutate(order.id)}
                >
                  <Check className="mr-2 h-4 w-4" />
                  Fertig
                </Button>
              </Card>
            ))}
          </div>
        </div>

        {/* Ready Orders */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-3 h-3 rounded-full bg-green-600"></div>
            <h2 className="text-lg font-semibold">Fertig ({readyOrders.length})</h2>
          </div>
          <div className="space-y-3">
            {readyOrders.map((order) => (
              <Card key={order.id} className="p-4 border-2 border-green-500 bg-green-50">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="font-bold text-xl">#{order.order_number}</span>
                    {order.table_number && (
                      <p className="text-sm text-muted-foreground">Tisch {order.table_number}</p>
                    )}
                  </div>
                  <Badge variant="outline" className="bg-green-600 text-white">
                    Bereit
                  </Badge>
                </div>

                <div className="space-y-2">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex justify-between text-sm">
                      <span className="font-medium">
                        {item.quantity}x {item.product_name}
                      </span>
                    </div>
                  ))}
                </div>

                {order.completed_at && (
                  <p className="text-xs text-muted-foreground mt-3">
                    Fertig: {new Date(order.completed_at).toLocaleTimeString('de-DE')}
                  </p>
                )}
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
