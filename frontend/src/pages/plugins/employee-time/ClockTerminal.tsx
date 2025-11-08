import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Clock, LogIn, LogOut, Coffee, User } from 'lucide-react'
import { useClockIn, useClockOut, useStartBreak, useEndBreak } from '@/hooks/useEmployeeTime'

export function ClockTerminal() {
  const [employeeId, setEmployeeId] = useState('')
  const [currentEmployee, setCurrentEmployee] = useState<{ id: number; name: string; status: string } | null>(null)

  const clockIn = useClockIn()
  const clockOut = useClockOut()
  const startBreak = useStartBreak()
  const endBreak = useEndBreak()

  const handleClockIn = () => {
    if (!employeeId) return
    clockIn.mutate(
      { employeeId: parseInt(employeeId) },
      {
        onSuccess: () => {
          setCurrentEmployee({ id: employeeId, status: 'working' })
        },
      }
    )
  }

  const handleClockOut = () => {
    if (!employeeId) return
    clockOut.mutate(parseInt(employeeId), {
      onSuccess: () => {
        setCurrentEmployee(null)
        setEmployeeId('')
      },
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-6">
      <Card className="w-full max-w-2xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Clock className="h-12 w-12 text-blue-600" />
            <h1 className="text-3xl font-bold">Zeiterfassung</h1>
          </div>
          <div className="text-5xl font-mono font-bold text-blue-600">
            {new Date().toLocaleTimeString('de-DE')}
          </div>
          <div className="text-lg text-muted-foreground mt-2">
            {new Date().toLocaleDateString('de-DE', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </div>
        </div>

        {/* Employee Input */}
        {!currentEmployee && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Mitarbeiter-ID eingeben</label>
              <Input
                type="text"
                placeholder="ID oder Kartennummer"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                className="text-center text-2xl h-16"
                autoFocus
                onKeyPress={(e) => {
                  if (e.key === 'Enter') handleClockIn()
                }}
              />
            </div>

            <Button onClick={handleClockIn} className="w-full h-16 text-xl" size="lg">
              <LogIn className="mr-3 h-6 w-6" />
              Einchecken
            </Button>
          </div>
        )}

        {/* Active Session */}
        {currentEmployee && (
          <div className="space-y-6">
            <div className="p-6 bg-green-50 border-2 border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <User className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="text-sm text-muted-foreground">Angemeldet als</p>
                    <p className="text-xl font-semibold">Mitarbeiter #{currentEmployee.id}</p>
                  </div>
                </div>
                <Badge variant="default" className="text-lg px-4 py-2">
                  {currentEmployee.status === 'working' ? 'Arbeitet' : 'Pause'}
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {currentEmployee.status === 'working' ? (
                <>
                  <Button
                    variant="outline"
                    className="h-24 text-lg"
                    onClick={() => {
                      startBreak.mutate(parseInt(employeeId), {
                        onSuccess: () => {
                          setCurrentEmployee({ ...currentEmployee, status: 'break' })
                        },
                      })
                    }}
                  >
                    <Coffee className="mr-2 h-6 w-6" />
                    Pause starten
                  </Button>
                  <Button
                    variant="destructive"
                    className="h-24 text-lg"
                    onClick={handleClockOut}
                  >
                    <LogOut className="mr-2 h-6 w-6" />
                    Auschecken
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="default"
                    className="h-24 text-lg"
                    onClick={() => {
                      endBreak.mutate(parseInt(employeeId), {
                        onSuccess: () => {
                          setCurrentEmployee({ ...currentEmployee, status: 'working' })
                        },
                      })
                    }}
                  >
                    <LogIn className="mr-2 h-6 w-6" />
                    Pause beenden
                  </Button>
                  <Button
                    variant="destructive"
                    className="h-24 text-lg"
                    onClick={handleClockOut}
                  >
                    <LogOut className="mr-2 h-6 w-6" />
                    Auschecken
                  </Button>
                </>
              )}
            </div>

            <div className="text-center text-sm text-muted-foreground">
              Eingecheckt seit: {new Date().toLocaleTimeString('de-DE')}
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
