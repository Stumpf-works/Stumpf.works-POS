import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Building, Phone, Mail, MapPin } from 'lucide-react'
import { useSuppliers } from '@/hooks/useInventory'

export function SupplierList() {
  const { data: suppliers, isLoading, error, refetch } = useSuppliers()

  if (isLoading) return <LoadingState message="Lade Lieferanten..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Lieferanten</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Lieferant hinzufügen
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {suppliers?.map((supplier) => (
          <Card key={supplier.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-full">
                  <Building className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold">{supplier.supplier_name}</h3>
                  {supplier.contact_person && (
                    <p className="text-sm text-muted-foreground">{supplier.contact_person}</p>
                  )}
                </div>
              </div>
              <Badge variant={supplier.is_active ? 'default' : 'secondary'}>
                {supplier.is_active ? 'Aktiv' : 'Inaktiv'}
              </Badge>
            </div>

            <div className="space-y-2 text-sm">
              {supplier.phone && (
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{supplier.phone}</span>
                </div>
              )}
              {supplier.email && (
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span>{supplier.email}</span>
                </div>
              )}
              {supplier.address && (
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="line-clamp-1">{supplier.address}</span>
                </div>
              )}
              {supplier.payment_terms && (
                <div className="mt-2 p-2 bg-muted/50 rounded">
                  <p className="text-xs text-muted-foreground">Zahlungsbedingungen</p>
                  <p className="font-medium">{supplier.payment_terms}</p>
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
