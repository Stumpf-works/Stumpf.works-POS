import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Edit, Maximize2 } from 'lucide-react'
import { useFloors, useTables, useUpdateTableStatus } from '@/hooks/useTableManagement'
import { TableStatus } from '@/types/plugins'

export function FloorPlanView() {
  const [selectedFloorId, setSelectedFloorId] = useState<number>()
  const { data: floors, isLoading: floorsLoading, error: floorsError } = useFloors()
  const { data: tables, isLoading: tablesLoading, error: tablesError } = useTables(selectedFloorId)
  const updateStatus = useUpdateTableStatus()

  const isLoading = floorsLoading || tablesLoading
  const error = floorsError || tablesError

  if (isLoading) return <LoadingState message="Lade Raumplan..." />
  if (error) return <ErrorState message="Fehler beim Laden des Raumplans" />

  const getStatusColor = (status: TableStatus) => {
    switch (status) {
      case 'available':
        return 'bg-green-500'
      case 'occupied':
        return 'bg-red-500'
      case 'reserved':
        return 'bg-blue-500'
      case 'dirty':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
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

  const getShapeClass = (shape: string) => {
    switch (shape) {
      case 'circle':
        return 'rounded-full'
      case 'rectangle':
        return 'rounded-lg'
      default:
        return 'rounded-lg'
    }
  }

  // Set default floor if none selected
  if (!selectedFloorId && floors && floors.length > 0) {
    setSelectedFloorId(floors[0].id)
  }

  // const currentFloor = floors?.find((f) => f.id === selectedFloorId)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Raumplan</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Edit className="mr-2 h-4 w-4" />
            Bearbeiten
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Tisch hinzufügen
          </Button>
        </div>
      </div>

      {/* Floor Selection */}
      <div className="flex gap-2">
        {floors?.map((floor) => (
          <Button
            key={floor.id}
            variant={selectedFloorId === floor.id ? 'default' : 'outline'}
            onClick={() => setSelectedFloorId(floor.id)}
          >
            {floor.floor_name}
          </Button>
        ))}
      </div>

      {/* Legend */}
      <Card className="p-4">
        <div className="flex items-center gap-6">
          <span className="text-sm font-medium">Legende:</span>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span className="text-sm">Verfügbar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span className="text-sm">Besetzt</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-blue-500 rounded"></div>
            <span className="text-sm">Reserviert</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-500 rounded"></div>
            <span className="text-sm">Reinigung</span>
          </div>
        </div>
      </Card>

      {/* Floor Plan */}
      <Card className="p-6">
        <div className="relative bg-muted/20 rounded-lg" style={{ minHeight: '600px' }}>
          {tables?.map((table) => (
            <div
              key={table.id}
              className={`absolute cursor-pointer transition-all hover:scale-105 ${getShapeClass(
                table.shape
              )} ${getStatusColor(table.status)} shadow-lg`}
              style={{
                left: `${table.x_position}px`,
                top: `${table.y_position}px`,
                width: `${table.width}px`,
                height: `${table.height}px`,
              }}
              onClick={() => {
                // Cycle through statuses for demo
                const statuses: TableStatus[] = ['available', 'occupied', 'reserved', 'dirty']
                const currentIndex = statuses.indexOf(table.status)
                const nextStatus = statuses[(currentIndex + 1) % statuses.length]
                updateStatus.mutate({ id: table.id, status: nextStatus })
              }}
            >
              <div className="h-full flex flex-col items-center justify-center text-white font-semibold p-2">
                <div className="text-lg">{table.table_number}</div>
                <div className="text-xs opacity-90">{table.capacity} Pers.</div>
              </div>
            </div>
          ))}

          {(!tables || tables.length === 0) && (
            <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Maximize2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Keine Tische auf dieser Etage</p>
                <Button variant="link" className="mt-2">
                  Tische hinzufügen
                </Button>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Table List */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Tischübersicht</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {tables?.map((table) => (
            <div key={table.id} className="p-4 border rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold">{table.table_number}</p>
                  <p className="text-sm text-muted-foreground">{table.capacity} Personen</p>
                </div>
                <Badge variant="outline">{getStatusLabel(table.status)}</Badge>
              </div>
              <div className={`w-full h-2 rounded-full ${getStatusColor(table.status)}`}></div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
