import { RouteObject } from 'react-router-dom'
import { RecipeList } from '@/pages/plugins/bakery/RecipeList'
import { ProductionPlan } from '@/pages/plugins/bakery/ProductionPlan'
import { BatchTracking } from '@/pages/plugins/bakery/BatchTracking'

export const bakeryRoutes: RouteObject = {
  path: 'bakery',
  children: [
    {
      index: true,
      element: <RecipeList />,
    },
    {
      path: 'production',
      element: <ProductionPlan />,
    },
    {
      path: 'batches',
      element: <BatchTracking />,
    },
  ],
}
