import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Calendar, Clock, Download, User } from 'lucide-react'
import { useTimeSheets } from '@/hooks/useEmployeeTime'

export function TimeSheetView() {
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0])
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])

  const { data: timesheets, isLoading, error, refetch } = useTimeSheets(undefined, startDate, endDate)

  if (isLoading) return <LoadingState message="Lade Zeiterfassung..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  // Calculate totals
  const totalHours = timesheets?.reduce((sum, ts) => sum + ts.total_hours, 0) || 0
  const totalRegular = timesheets?.reduce((sum, ts) => sum + ts.regular_hours, 0) || 0
  const totalOvertime = timesheets?.reduce((sum, ts) => sum + ts.overtime_hours, 0) || 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Zeiterfassungsübersicht</h1>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Exportieren
        </Button>
      </div>

      {/* Date Filter */}
      <Card className="p-4">
        <div className="flex gap-4 items-center">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <label className="text-sm font-medium">Von:</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="border rounded px-3 py-2 bg-background"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Bis:</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="border rounded px-3 py-2 bg-background"
            />
          </div>
        </div>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Gesamtstunden</p>
          <p className="text-3xl font-bold">{totalHours.toFixed(2)}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Reguläre Stunden</p>
          <p className="text-3xl font-bold text-blue-600">{totalRegular.toFixed(2)}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Überstunden</p>
          <p className="text-3xl font-bold text-orange-600">{totalOvertime.toFixed(2)}</p>
        </Card>
      </div>

      {/* Timesheets */}
      <div className="space-y-3">
        {timesheets?.map((timesheet) => (
          <Card key={timesheet.id} className="p-4">
            <div className="flex flex-col md:flex-row justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <User className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <h3 className="font-semibold">{timesheet.employee_name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {new Date(timesheet.date).toLocaleDateString('de-DE', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                  <Badge variant={timesheet.status === 'active' ? 'default' : 'secondary'}>
                    {timesheet.status === 'active' ? 'Aktiv' : 'Abgeschlossen'}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {timesheet.clock_in && (
                    <div>
                      <p className="text-muted-foreground mb-1">Einchecken</p>
                      <p className="font-medium">
                        {new Date(timesheet.clock_in).toLocaleTimeString('de-DE')}
                      </p>
                    </div>
                  )}
                  {timesheet.clock_out && (
                    <div>
                      <p className="text-muted-foreground mb-1">Auschecken</p>
                      <p className="font-medium">
                        {new Date(timesheet.clock_out).toLocaleTimeString('de-DE')}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-muted-foreground mb-1">Gesamtstunden</p>
                    <p className="font-medium">{timesheet.total_hours.toFixed(2)}h</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground mb-1">Pause</p>
                    <p className="font-medium">{timesheet.break_hours.toFixed(2)}h</p>
                  </div>
                </div>

                {timesheet.overtime_hours > 0 && (
                  <div className="mt-3 p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-orange-600" />
                      <p className="text-sm font-medium text-orange-900">
                        Überstunden: {timesheet.overtime_hours.toFixed(2)}h
                      </p>
                    </div>
                  </div>
                )}

                {timesheet.notes && (
                  <div className="mt-3 p-3 bg-muted/50 rounded-lg">
                    <p className="text-sm text-muted-foreground">{timesheet.notes}</p>
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-2 min-w-[120px]">
                <Button variant="outline" size="sm">
                  Details
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {!timesheets || timesheets.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Zeiterfassungsdaten gefunden</p>
        </Card>
      )}
    </div>
  )
}
