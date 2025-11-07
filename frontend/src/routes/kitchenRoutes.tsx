import { RouteObject } from 'react-router-dom'
import { KitchenDisplay } from '@/pages/plugins/kitchen-display/KitchenDisplay'
import { StationManagement } from '@/pages/plugins/kitchen-display/StationManagement'

export const kitchenRoutes: RouteObject = {
  path: 'kitchen',
  children: [
    {
      index: true,
      element: <KitchenDisplay />,
    },
    {
      path: 'stations',
      element: <StationManagement />,
    },
  ],
}
