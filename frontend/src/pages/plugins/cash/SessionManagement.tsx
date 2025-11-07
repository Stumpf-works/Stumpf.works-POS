import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Clock, Calendar, User, DollarSign, AlertCircle } from 'lucide-react'
import { useCashSessions } from '@/hooks/useCash'

export function SessionManagement() {
  const [selectedRegisterId, setSelectedRegisterId] = useState<number>()
  const { data: sessions, isLoading, error, refetch } = useCashSessions(selectedRegisterId)

  if (isLoading) return <LoadingState message="Lade Sitzungen..." />
  if (error) return <ErrorState message="Fehler beim Laden der Sitzungen" onRetry={() => refetch()} />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Kassensitzungen</h1>
        <div className="flex gap-2">
          <select
            className="border rounded px-3 py-2 bg-background"
            value={selectedRegisterId || ''}
            onChange={(e) => setSelectedRegisterId(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">Alle Kassen</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        {sessions?.map((session) => (
          <Card key={session.id} className="p-6">
            <div className="flex flex-col md:flex-row justify-between gap-4">
              {/* Session Info */}
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-4">
                  <Badge variant={session.closed_at ? 'secondary' : 'default'}>
                    {session.closed_at ? 'Geschlossen' : 'Aktiv'}
                  </Badge>
                  <span className="text-sm text-muted-foreground">Sitzung #{session.id}</span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-muted-foreground">Geöffnet von</p>
                        <p className="font-medium">{session.opened_by_user_name}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <p className="text-muted-foreground">Geöffnet am</p>
                        <p className="font-medium">
                          {new Date(session.opened_at).toLocaleString('de-DE')}
                        </p>
                      </div>
                    </div>

                    {session.closed_at && (
                      <>
                        <div className="flex items-center gap-2 text-sm">
                          <User className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <p className="text-muted-foreground">Geschlossen von</p>
                            <p className="font-medium">{session.closed_by_user_name}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <p className="text-muted-foreground">Geschlossen am</p>
                            <p className="font-medium">
                              {new Date(session.closed_at).toLocaleString('de-DE')}
                            </p>
                          </div>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Financial Info */}
                  <div className="space-y-3">
                    <div className="p-3 bg-green-50 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Anfangsbestand</p>
                      <p className="text-xl font-bold text-green-600">
                        {session.opening_balance.toFixed(2)} €
                      </p>
                    </div>

                    {session.closing_balance !== null && session.closing_balance !== undefined && (
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-muted-foreground mb-1">Endbestand</p>
                        <p className="text-xl font-bold text-blue-600">
                          {session.closing_balance.toFixed(2)} €
                        </p>
                      </div>
                    )}

                    {session.variance !== null && session.variance !== undefined && session.variance !== 0 && (
                      <div className={`p-3 rounded-lg ${session.variance > 0 ? 'bg-yellow-50' : 'bg-red-50'}`}>
                        <div className="flex items-center gap-2">
                          <AlertCircle className={`h-4 w-4 ${session.variance > 0 ? 'text-yellow-600' : 'text-red-600'}`} />
                          <div>
                            <p className="text-xs text-muted-foreground">Abweichung</p>
                            <p className={`text-lg font-bold ${session.variance > 0 ? 'text-yellow-600' : 'text-red-600'}`}>
                              {session.variance > 0 ? '+' : ''}{session.variance.toFixed(2)} €
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {session.notes && (
                  <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                    <p className="text-sm font-medium mb-1">Notizen</p>
                    <p className="text-sm text-muted-foreground">{session.notes}</p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2 min-w-[150px]">
                {session.z_report_generated ? (
                  <Badge variant="outline" className="justify-center">
                    Z-Bericht erstellt
                  </Badge>
                ) : (
                  session.closed_at && (
                    <Button variant="outline" size="sm">
                      Z-Bericht erstellen
                    </Button>
                  )
                )}
                <Button variant="ghost" size="sm">
                  Details ansehen
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {sessions?.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <DollarSign className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Kassensitzungen gefunden</p>
        </Card>
      )}
    </div>
  )
}
