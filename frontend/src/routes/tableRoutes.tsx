import { RouteObject } from 'react-router-dom'
import { FloorPlanView } from '@/pages/plugins/table-management/FloorPlanView'
import { TableList } from '@/pages/plugins/table-management/TableList'
import { ReservationList } from '@/pages/plugins/table-management/ReservationList'

export const tableRoutes: RouteObject = {
  path: 'tables',
  children: [
    {
      index: true,
      element: <FloorPlanView />,
    },
    {
      path: 'list',
      element: <TableList />,
    },
    {
      path: 'reservations',
      element: <ReservationList />,
    },
  ],
}
