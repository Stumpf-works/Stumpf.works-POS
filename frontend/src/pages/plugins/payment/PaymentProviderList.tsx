import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Settings } from 'lucide-react'
import { usePaymentProviders, useUpdatePaymentProvider } from '@/hooks/usePayment'

export function PaymentProviderList() {
  const { data: providers, isLoading, error, refetch } = usePaymentProviders()
  const updateProvider = useUpdatePaymentProvider()

  const getProviderIcon = (name: string) => {
    const icons: Record<string, string> = {
      stripe: '💳',
      paypal: '🅿️',
      square: '⬛',
      sumup: '🔷',
    }
    return icons[name.toLowerCase()] || '💰'
  }

  const getHealthStatusVariant = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'default'
      case 'degraded':
        return 'secondary'
      case 'unhealthy':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  if (isLoading) return <LoadingState message="Lade Zahlungsanbieter..." />
  if (error) return <ErrorState message="Fehler beim Laden der Anbieter" onRetry={() => refetch()} />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Zahlungsanbieter</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Anbieter hinzufügen
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {providers?.map((provider) => (
          <Card key={provider.id} className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="text-3xl">{getProviderIcon(provider.provider_name)}</div>
                <div>
                  <h3 className="font-semibold text-lg">{provider.provider_name}</h3>
                  <p className="text-sm text-muted-foreground capitalize">
                    {provider.provider_type.replace('_', ' ')}
                  </p>
                </div>
              </div>

              <Badge variant={getHealthStatusVariant(provider.health_status)}>
                {provider.health_status}
              </Badge>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Gebühren</span>
                <span className="font-medium">
                  {provider.transaction_fee_percentage}% + {provider.transaction_fee_fixed}€
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Modus</span>
                <Badge variant={provider.is_test_mode ? 'secondary' : 'default'}>
                  {provider.is_test_mode ? 'Test' : 'Live'}
                </Badge>
              </div>

              {provider.is_default && (
                <Badge variant="outline" className="w-full justify-center">
                  Standard-Anbieter
                </Badge>
              )}

              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Status</span>
                <Badge variant={provider.is_active ? 'default' : 'secondary'}>
                  {provider.is_active ? 'Aktiv' : 'Inaktiv'}
                </Badge>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() =>
                  updateProvider.mutate({
                    id: provider.id,
                    data: { is_active: !provider.is_active },
                  })
                }
              >
                {provider.is_active ? 'Deaktivieren' : 'Aktivieren'}
              </Button>

              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
