import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Calendar, Users, Clock, Phone, Mail, X, Check } from 'lucide-react'
import { useReservations, useCancelReservation, useSeatReservation } from '@/hooks/useTableManagement'
import { ReservationStatus } from '@/types/plugins'

export function ReservationList() {
  const [filter, setFilter] = useState<ReservationStatus | 'all'>('all')
  const { data: reservations, isLoading, error, refetch } = useReservations(
    filter === 'all' ? undefined : { status: filter }
  )
  const cancelReservation = useCancelReservation()
  const seatReservation = useSeatReservation()

  if (isLoading) return <LoadingState message="Lade Reservierungen..." />
  if (error) return <ErrorState message="Fehler beim Laden der Reservierungen" onRetry={() => refetch()} />

  const getStatusVariant = (status: ReservationStatus) => {
    switch (status) {
      case 'confirmed':
        return 'default'
      case 'pending':
        return 'secondary'
      case 'seated':
        return 'outline'
      case 'cancelled':
        return 'destructive'
      case 'no_show':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  const getStatusLabel = (status: ReservationStatus) => {
    const labels: Record<ReservationStatus, string> = {
      pending: 'Ausstehend',
      confirmed: 'Bestätigt',
      seated: 'Platziert',
      cancelled: 'Storniert',
      no_show: 'Nicht erschienen',
    }
    return labels[status]
  }

  // Group by date
  const groupedReservations = reservations?.reduce((acc, res) => {
    const date = new Date(res.reservation_date).toLocaleDateString('de-DE')
    if (!acc[date]) acc[date] = []
    acc[date].push(res)
    return acc
  }, {} as Record<string, typeof reservations>)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reservierungen</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Neue Reservierung
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Gesamt</p>
          <p className="text-2xl font-bold">{reservations?.length || 0}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Bestätigt</p>
          <p className="text-2xl font-bold text-green-600">
            {reservations?.filter((r) => r.status === 'confirmed').length || 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Ausstehend</p>
          <p className="text-2xl font-bold text-yellow-600">
            {reservations?.filter((r) => r.status === 'pending').length || 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Platziert</p>
          <p className="text-2xl font-bold text-blue-600">
            {reservations?.filter((r) => r.status === 'seated').length || 0}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Storniert</p>
          <p className="text-2xl font-bold text-red-600">
            {reservations?.filter((r) => r.status === 'cancelled').length || 0}
          </p>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex gap-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            Alle
          </Button>
          <Button
            variant={filter === 'pending' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('pending')}
          >
            Ausstehend
          </Button>
          <Button
            variant={filter === 'confirmed' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('confirmed')}
          >
            Bestätigt
          </Button>
          <Button
            variant={filter === 'seated' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter('seated')}
          >
            Platziert
          </Button>
        </div>
      </Card>

      {/* Reservations by Date */}
      <div className="space-y-6">
        {Object.entries(groupedReservations || {}).map(([date, dateReservations]) => (
          <div key={date}>
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              {date}
            </h2>
            <div className="space-y-3">
              {dateReservations.map((reservation) => (
                <Card key={reservation.id} className="p-4">
                  <div className="flex flex-col md:flex-row justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="font-semibold text-lg">{reservation.customer_name}</h3>
                        <Badge variant={getStatusVariant(reservation.status)}>
                          {getStatusLabel(reservation.status)}
                        </Badge>
                        {reservation.table_number && (
                          <Badge variant="outline">Tisch {reservation.table_number}</Badge>
                        )}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          <span>{reservation.reservation_time}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-muted-foreground" />
                          <span>{reservation.guest_count} Gäste</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4 text-muted-foreground" />
                          <span>{reservation.customer_phone}</span>
                        </div>
                        {reservation.customer_email && (
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4 text-muted-foreground" />
                            <span className="truncate">{reservation.customer_email}</span>
                          </div>
                        )}
                      </div>

                      {reservation.notes && (
                        <div className="mt-3 p-3 bg-muted/50 rounded-lg">
                          <p className="text-sm text-muted-foreground">{reservation.notes}</p>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex md:flex-col gap-2 min-w-[120px]">
                      {reservation.status === 'confirmed' && (
                        <Button
                          variant="default"
                          size="sm"
                          className="flex-1"
                          onClick={() => seatReservation.mutate(reservation.id)}
                        >
                          <Check className="mr-2 h-4 w-4" />
                          Platzieren
                        </Button>
                      )}
                      {(reservation.status === 'pending' || reservation.status === 'confirmed') && (
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1"
                          onClick={() => cancelReservation.mutate(reservation.id)}
                        >
                          <X className="mr-2 h-4 w-4" />
                          Stornieren
                        </Button>
                      )}
                      <Button variant="ghost" size="sm" className="flex-1">
                        Details
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>

      {!reservations || reservations.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Reservierungen gefunden</p>
        </Card>
      )}
    </div>
  )
}
