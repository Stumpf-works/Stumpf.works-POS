import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Calendar, Sun, Sunset, Moon } from 'lucide-react'
import { useProductionPlans } from '@/hooks/useBakery'

export function ProductionPlan() {
  const { data: plans, isLoading, error, refetch } = useProductionPlans()

  if (isLoading) return <LoadingState message="Lade Produktionsplan..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getShiftIcon = (shift: string) => {
    switch (shift) {
      case 'morning':
        return <Sun className="h-5 w-5 text-yellow-600" />
      case 'afternoon':
        return <Sunset className="h-5 w-5 text-orange-600" />
      case 'night':
        return <Moon className="h-5 w-5 text-blue-600" />
      default:
        return null
    }
  }

  const getShiftLabel = (shift: string) => {
    const labels: Record<string, string> = {
      morning: 'Morgen',
      afternoon: 'Nachmittag',
      night: 'Nacht',
    }
    return labels[shift] || shift
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Produktionsplanung</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Neuer Plan
        </Button>
      </div>

      <div className="space-y-4">
        {plans?.map((plan) => (
          <Card key={plan.id} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <Calendar className="h-6 w-6 text-muted-foreground" />
                <div>
                  <h3 className="font-semibold text-lg">
                    {new Date(plan.plan_date).toLocaleDateString('de-DE', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    {getShiftIcon(plan.shift)}
                    <span className="text-sm text-muted-foreground">
                      {getShiftLabel(plan.shift)}-Schicht
                    </span>
                  </div>
                </div>
              </div>
              <Badge variant="outline">{plan.items.length} Artikel</Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {plan.items.map((item) => (
                <div key={item.id} className="p-3 bg-muted/50 rounded-lg">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-medium text-sm">{item.recipe_name}</h4>
                    <Badge variant="secondary" className="text-xs">
                      {item.quantity}x
                    </Badge>
                  </div>
                  {item.batch_number && (
                    <p className="text-xs text-muted-foreground">
                      Charge: {item.batch_number}
                    </p>
                  )}
                </div>
              ))}
            </div>

            {plan.notes && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm text-muted-foreground">{plan.notes}</p>
              </div>
            )}
          </Card>
        ))}
      </div>

      {!plans || plans.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Produktionspläne vorhanden</p>
        </Card>
      )}
    </div>
  )
}
