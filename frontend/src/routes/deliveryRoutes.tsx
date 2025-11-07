import { RouteObject } from 'react-router-dom'
import { DeliveryDashboard } from '@/pages/plugins/delivery/DeliveryDashboard'
import { DriverManagement } from '@/pages/plugins/delivery/DriverManagement'

export const deliveryRoutes: RouteObject = {
  path: 'delivery',
  children: [
    {
      index: true,
      element: <DeliveryDashboard />,
    },
    {
      path: 'drivers',
      element: <DriverManagement />,
    },
  ],
}
