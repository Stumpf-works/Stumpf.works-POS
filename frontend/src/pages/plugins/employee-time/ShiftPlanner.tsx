import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Calendar, Clock, User } from 'lucide-react'
import { useShifts } from '@/hooks/useEmployeeTime'

export function ShiftPlanner() {
  const { data: shifts, isLoading, error, refetch } = useShifts()

  if (isLoading) return <LoadingState message="Lade Schichtplan..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  // Group shifts by date
  const groupedShifts = shifts?.reduce((acc, shift) => {
    const date = shift.shift_date
    if (!acc[date]) acc[date] = []
    acc[date].push(shift)
    return acc
  }, {} as Record<string, typeof shifts>)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Schichtplanung</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Schicht hinzufügen
        </Button>
      </div>

      {/* Calendar View */}
      <div className="space-y-6">
        {Object.entries(groupedShifts || {}).map(([date, dateShifts]) => (
          <div key={date}>
            <div className="flex items-center gap-2 mb-3">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <h2 className="text-lg font-semibold">
                {new Date(date).toLocaleDateString('de-DE', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </h2>
              <Badge variant="outline">{dateShifts.length} Schichten</Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dateShifts.map((shift) => (
                <Card key={shift.id} className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <User className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <h3 className="font-semibold">{shift.employee_name}</h3>
                        {shift.position && (
                          <p className="text-sm text-muted-foreground">{shift.position}</p>
                        )}
                      </div>
                    </div>
                    <Badge variant={shift.is_confirmed ? 'default' : 'secondary'}>
                      {shift.is_confirmed ? 'Bestätigt' : 'Offen'}
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">
                        {shift.start_time} - {shift.end_time}
                      </span>
                    </div>

                    {shift.notes && (
                      <div className="p-2 bg-muted/50 rounded text-sm">
                        <p className="text-muted-foreground">{shift.notes}</p>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2 mt-3">
                    {!shift.is_confirmed && (
                      <Button variant="default" size="sm" className="flex-1">
                        Bestätigen
                      </Button>
                    )}
                    <Button variant="outline" size="sm" className="flex-1">
                      Bearbeiten
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>

      {!shifts || shifts.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Schichten geplant</p>
          <Button variant="link" className="mt-2">
            Erste Schicht erstellen
          </Button>
        </Card>
      )}
    </div>
  )
}
