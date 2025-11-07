import { RouteObject } from 'react-router-dom'
import { CustomerPortal } from '@/pages/plugins/loyalty/CustomerPortal'
import { RewardsList } from '@/pages/plugins/loyalty/RewardsList'

export const loyaltyRoutes: RouteObject = {
  path: 'loyalty',
  children: [
    {
      index: true,
      element: <CustomerPortal />,
    },
    {
      path: 'rewards',
      element: <RewardsList />,
    },
  ],
}
