import { RouteObject } from 'react-router-dom'
import { CashRegisterList } from '@/pages/plugins/cash/CashRegisterList'
import { SessionManagement } from '@/pages/plugins/cash/SessionManagement'
import { ZReportView } from '@/pages/plugins/cash/ZReportView'

export const cashRoutes: RouteObject = {
  path: 'cash',
  children: [
    {
      index: true,
      element: <CashRegisterList />,
    },
    {
      path: 'sessions',
      element: <SessionManagement />,
    },
    {
      path: 'z-report/:sessionId?',
      element: <ZReportView />,
    },
  ],
}
