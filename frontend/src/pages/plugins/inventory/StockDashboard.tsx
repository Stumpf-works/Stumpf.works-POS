import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Package, AlertTriangle, TrendingDown, RefreshCcw } from 'lucide-react'
import { useInventoryItems } from '@/hooks/useInventory'

export function StockDashboard() {
  const { data: items, isLoading, error, refetch } = useInventoryItems()

  if (isLoading) return <LoadingState message="Lade Bestand..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const lowStockItems = items?.filter((item) => item.current_stock <= item.reorder_level) || []
  const outOfStockItems = items?.filter((item) => item.current_stock === 0) || []
  const totalValue = items?.reduce((sum, item) => sum + item.current_stock * item.unit_cost, 0) || 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Bestandsübersicht</h1>
        <Button variant="outline" onClick={() => refetch()}>
          <RefreshCcw className="mr-2 h-4 w-4" />
          Aktualisieren
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Gesamt Artikel</p>
          <p className="text-3xl font-bold">{items?.length || 0}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Gesamtwert</p>
          <p className="text-3xl font-bold text-green-600">{totalValue.toFixed(2)} €</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Niedriger Bestand</p>
          <p className="text-3xl font-bold text-yellow-600">{lowStockItems.length}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Nicht vorrätig</p>
          <p className="text-3xl font-bold text-red-600">{outOfStockItems.length}</p>
        </Card>
      </div>

      {/* Low Stock Alert */}
      {lowStockItems.length > 0 && (
        <Card className="p-4 bg-yellow-50 border-yellow-200">
          <div className="flex items-center gap-3 mb-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
            <h3 className="font-semibold text-yellow-900">Niedriger Bestand</h3>
          </div>
          <div className="space-y-2">
            {lowStockItems.slice(0, 5).map((item) => (
              <div key={item.id} className="flex justify-between text-sm">
                <span>{item.product_name}</span>
                <Badge variant="outline" className="bg-white">
                  {item.current_stock} {item.unit_of_measure}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Inventory List */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Bestandsliste</h2>
        <div className="space-y-3">
          {items?.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-3">
                <Package className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="font-medium">{item.product_name}</p>
                  <p className="text-sm text-muted-foreground">SKU: {item.sku}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Bestand</p>
                  <p className="font-semibold">
                    {item.current_stock} {item.unit_of_measure}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Wert</p>
                  <p className="font-semibold">
                    {(item.current_stock * item.unit_cost).toFixed(2)} €
                  </p>
                </div>
                {item.current_stock <= item.reorder_level && (
                  <TrendingDown className="h-5 w-5 text-yellow-600" />
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
