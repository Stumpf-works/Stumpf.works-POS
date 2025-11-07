import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, User, Star, TrendingUp } from 'lucide-react'
import { useLoyaltyCustomers } from '@/hooks/useLoyalty'
import { LoyaltyTier } from '@/types/plugins'

export function CustomerPortal() {
  const { data: customers, isLoading, error, refetch } = useLoyaltyCustomers()

  if (isLoading) return <LoadingState message="Lade Kunden..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getTierColor = (tier: LoyaltyTier) => {
    switch (tier) {
      case 'bronze':
        return 'bg-orange-700'
      case 'silver':
        return 'bg-gray-400'
      case 'gold':
        return 'bg-yellow-500'
      case 'platinum':
        return 'bg-purple-600'
      default:
        return 'bg-gray-500'
    }
  }

  const getTierLabel = (tier: LoyaltyTier) => {
    const labels: Record<LoyaltyTier, string> = {
      bronze: 'Bronze',
      silver: 'Silber',
      gold: 'Gold',
      platinum: 'Platin',
    }
    return labels[tier]
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Treueprogramm Kunden</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Kunde einschreiben
        </Button>
      </div>

      {/* Tier Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {(['bronze', 'silver', 'gold', 'platinum'] as LoyaltyTier[]).map((tier) => {
          const count = customers?.filter((c) => c.tier === tier).length || 0
          return (
            <Card key={tier} className="p-4">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${getTierColor(tier)}`}></div>
                <div>
                  <p className="text-sm text-muted-foreground">{getTierLabel(tier)}</p>
                  <p className="text-2xl font-bold">{count}</p>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Customer Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {customers?.map((customer) => (
          <Card key={customer.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-full">
                  <User className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold">{customer.customer_name}</h3>
                  <p className="text-sm text-muted-foreground font-mono">
                    {customer.member_number}
                  </p>
                </div>
              </div>
              <Badge className={getTierColor(customer.tier)}>
                {getTierLabel(customer.tier)}
              </Badge>
            </div>

            <div className="space-y-3 mb-4">
              <div className="p-3 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Punkte</p>
                    <p className="text-3xl font-bold text-purple-600">
                      {customer.total_points}
                    </p>
                  </div>
                  <Star className="h-8 w-8 text-yellow-500 fill-yellow-500" />
                </div>
              </div>

              {customer.next_tier && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    <p className="text-sm font-medium text-blue-900">
                      Nächstes Level: {getTierLabel(customer.next_tier)}
                    </p>
                  </div>
                  <div className="w-full bg-white rounded-full h-2 mb-1">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${customer.tier_progress_percentage}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Noch {customer.points_to_next_tier} Punkte
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="p-2 bg-muted/50 rounded">
                  <p className="text-muted-foreground">Verdient</p>
                  <p className="font-semibold">{customer.points_earned}</p>
                </div>
                <div className="p-2 bg-muted/50 rounded">
                  <p className="text-muted-foreground">Eingelöst</p>
                  <p className="font-semibold">{customer.points_redeemed}</p>
                </div>
              </div>
            </div>

            <Button variant="outline" size="sm" className="w-full">
              Details
            </Button>
          </Card>
        ))}
      </div>
    </div>
  )
}
