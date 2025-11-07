import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Users, Square, Circle } from 'lucide-react'
import { useTables, useUpdateTableStatus } from '@/hooks/useTableManagement'
import { TableStatus } from '@/types/plugins'

export function TableList() {
  const { data: tables, isLoading, error, refetch } = useTables()
  const updateStatus = useUpdateTableStatus()

  if (isLoading) return <LoadingState message="Lade Tische..." />
  if (error) return <ErrorState message="Fehler beim Laden der Tische" onRetry={() => refetch()} />

  const getStatusVariant = (status: TableStatus) => {
    switch (status) {
      case 'available':
        return 'default'
      case 'occupied':
        return 'destructive'
      case 'reserved':
        return 'secondary'
      case 'dirty':
        return 'outline'
      default:
        return 'outline'
    }
  }

  const getStatusLabel = (status: TableStatus) => {
    const labels: Record<TableStatus, string> = {
      available: 'Verfügbar',
      occupied: 'Besetzt',
      reserved: 'Reserviert',
      dirty: 'Reinigung',
    }
    return labels[status]
  }

  const getShapeIcon = (shape: string) => {
    switch (shape) {
      case 'circle':
        return <Circle className="h-5 w-5" />
      case 'rectangle':
        return <Square className="h-5 w-5" />
      default:
        return <Square className="h-5 w-5" />
    }
  }

  // Group by floor
  const groupedTables = tables?.reduce((acc, table) => {
    const floor = table.floor_name || 'Ohne Etage'
    if (!acc[floor]) acc[floor] = []
    acc[floor].push(table)
    return acc
  }, {} as Record<string, typeof tables>)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tischverwaltung</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Tisch hinzufügen
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Gesamt</p>
          <p className="text-2xl font-bold">{tables?.length || 0}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Verfügbar</p>
          <p className="text-2xl font-bold text-green-600">
            {tables?.filter((t) => t.status === 'available').length || 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Besetzt</p>
          <p className="text-2xl font-bold text-red-600">
            {tables?.filter((t) => t.status === 'occupied').length || 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Kapazität</p>
          <p className="text-2xl font-bold">
            {tables?.reduce((sum, t) => sum + t.capacity, 0) || 0}
          </p>
        </Card>
      </div>

      {/* Tables by Floor */}
      <div className="space-y-6">
        {Object.entries(groupedTables || {}).map(([floor, floorTables]) => (
          <div key={floor}>
            <h2 className="text-lg font-semibold mb-3">{floor}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {floorTables.map((table) => (
                <Card key={table.id} className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getShapeIcon(table.shape)}
                      <div>
                        <h3 className="font-semibold">{table.table_number}</h3>
                        <p className="text-sm text-muted-foreground flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {table.capacity}
                        </p>
                      </div>
                    </div>
                  </div>

                  <Badge variant={getStatusVariant(table.status)} className="w-full justify-center mb-3">
                    {getStatusLabel(table.status)}
                  </Badge>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => {
                        const newStatus: TableStatus =
                          table.status === 'available' ? 'occupied' : 'available'
                        updateStatus.mutate({ id: table.id, status: newStatus })
                      }}
                    >
                      {table.status === 'available' ? 'Besetzen' : 'Freigeben'}
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
