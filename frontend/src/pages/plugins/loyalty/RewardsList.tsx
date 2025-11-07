import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, Gift, Star, Percent, Package } from 'lucide-react'
import { useRewards } from '@/hooks/useLoyalty'
import { RewardType } from '@/types/plugins'

export function RewardsList() {
  const { data: rewards, isLoading, error, refetch } = useRewards()

  if (isLoading) return <LoadingState message="Lade Belohnungen..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getRewardTypeIcon = (type: RewardType) => {
    switch (type) {
      case 'discount_percentage':
        return <Percent className="h-5 w-5 text-green-600" />
      case 'discount_fixed':
        return <Star className="h-5 w-5 text-blue-600" />
      case 'free_product':
        return <Package className="h-5 w-5 text-purple-600" />
      case 'points_multiplier':
        return <Star className="h-5 w-5 text-yellow-600" />
      default:
        return <Gift className="h-5 w-5 text-gray-600" />
    }
  }

  const getRewardTypeLabel = (type: RewardType) => {
    const labels: Record<RewardType, string> = {
      discount_percentage: 'Prozentrabatt',
      discount_fixed: 'Festrabatt',
      free_product: 'Gratis Produkt',
      points_multiplier: 'Punkte-Multiplikator',
    }
    return labels[type]
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Belohnungen</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Belohnung erstellen
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {rewards?.map((reward) => (
          <Card key={reward.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-full">
                  {getRewardTypeIcon(reward.reward_type)}
                </div>
                <div>
                  <h3 className="font-semibold">{reward.reward_name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {getRewardTypeLabel(reward.reward_type)}
                  </p>
                </div>
              </div>
              <Badge variant={reward.is_active ? 'default' : 'secondary'}>
                {reward.is_active ? 'Aktiv' : 'Inaktiv'}
              </Badge>
            </div>

            {reward.description && (
              <p className="text-sm text-muted-foreground mb-4">{reward.description}</p>
            )}

            <div className="space-y-3 mb-4">
              <div className="p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Wert</p>
                <p className="text-2xl font-bold text-purple-600">
                  {reward.reward_type === 'discount_percentage'
                    ? `${reward.reward_value}%`
                    : reward.reward_type === 'discount_fixed'
                    ? `${reward.reward_value}€`
                    : reward.reward_type === 'points_multiplier'
                    ? `${reward.reward_value}x`
                    : reward.reward_value}
                </p>
              </div>

              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Benötigte Punkte</span>
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-600 fill-yellow-600" />
                    <span className="font-semibold">{reward.points_required}</span>
                  </div>
                </div>
              </div>

              {reward.tier_requirement && (
                <Badge variant="outline" className="w-full justify-center">
                  Mindestens {reward.tier_requirement}-Level
                </Badge>
              )}

              {reward.max_redemptions && (
                <p className="text-xs text-muted-foreground text-center">
                  Max. {reward.max_redemptions} Einlösungen
                </p>
              )}

              {(reward.valid_from || reward.valid_until) && (
                <div className="text-xs text-muted-foreground">
                  {reward.valid_from && (
                    <p>Von: {new Date(reward.valid_from).toLocaleDateString('de-DE')}</p>
                  )}
                  {reward.valid_until && (
                    <p>Bis: {new Date(reward.valid_until).toLocaleDateString('de-DE')}</p>
                  )}
                </div>
              )}
            </div>

            <Button variant="outline" size="sm" className="w-full">
              Bearbeiten
            </Button>
          </Card>
        ))}
      </div>
    </div>
  )
}
