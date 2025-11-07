import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, ChefHat, Clock, Thermometer } from 'lucide-react'
import { useRecipes } from '@/hooks/useBakery'
import { RecipeCategory } from '@/types/plugins'

export function RecipeList() {
  const [filter, setFilter] = useState<RecipeCategory | 'all'>('all')
  const { data: recipes, isLoading, error, refetch } = useRecipes(
    filter === 'all' ? undefined : filter
  )

  if (isLoading) return <LoadingState message="Lade Rezepte..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getCategoryLabel = (category: RecipeCategory) => {
    const labels: Record<RecipeCategory, string> = {
      bread: 'Brot',
      rolls: 'Brötchen',
      cake: 'Kuchen',
      pastry: 'Gebäck',
      other: 'Sonstiges',
    }
    return labels[category]
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Rezeptverwaltung</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Neues Rezept
        </Button>
      </div>

      {/* Category Filter */}
      <Card className="p-4">
        <div className="flex gap-2">
          <Button variant={filter === 'all' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('all')}>
            Alle
          </Button>
          <Button variant={filter === 'bread' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('bread')}>
            Brot
          </Button>
          <Button variant={filter === 'rolls' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('rolls')}>
            Brötchen
          </Button>
          <Button variant={filter === 'cake' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('cake')}>
            Kuchen
          </Button>
          <Button variant={filter === 'pastry' ? 'default' : 'outline'} size="sm" onClick={() => setFilter('pastry')}>
            Gebäck
          </Button>
        </div>
      </Card>

      {/* Recipe Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recipes?.map((recipe) => (
          <Card key={recipe.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <ChefHat className="h-5 w-5 text-orange-600" />
                <h3 className="font-semibold">{recipe.recipe_name}</h3>
              </div>
              <Badge variant="outline">{getCategoryLabel(recipe.category)}</Badge>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Chargengröße</span>
                <span className="font-medium">
                  {recipe.batch_size} {recipe.unit_of_measure}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span>Backzeit: {recipe.baking_time} min</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Thermometer className="h-4 w-4 text-muted-foreground" />
                <span>Temperatur: {recipe.baking_temperature}°C</span>
              </div>
              {recipe.resting_time && (
                <div className="p-2 bg-blue-50 rounded text-sm">
                  <p className="text-muted-foreground">Ruhezeit: {recipe.resting_time} min</p>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <p className="text-xs text-muted-foreground mb-1">
                Zutaten ({recipe.ingredients.length})
              </p>
              <div className="max-h-20 overflow-y-auto text-sm">
                {recipe.ingredients.slice(0, 3).map((ing) => (
                  <div key={ing.id} className="flex justify-between">
                    <span>{ing.ingredient_name}</span>
                    <span className="text-muted-foreground">
                      {ing.quantity} {ing.unit_of_measure}
                    </span>
                  </div>
                ))}
                {recipe.ingredients.length > 3 && (
                  <p className="text-muted-foreground text-xs mt-1">
                    +{recipe.ingredients.length - 3} weitere
                  </p>
                )}
              </div>
            </div>

            <Button variant="outline" size="sm" className="w-full mt-3">
              Details
            </Button>
          </Card>
        ))}
      </div>
    </div>
  )
}
