import { RouteObject } from 'react-router-dom'
import { AnalyticsDashboard } from '@/pages/plugins/analytics/AnalyticsDashboard'
import { ReportBuilder } from '@/pages/plugins/analytics/ReportBuilder'

export const analyticsRoutes: RouteObject = {
  path: 'analytics',
  children: [
    {
      index: true,
      element: <AnalyticsDashboard />,
    },
    {
      path: 'reports',
      element: <ReportBuilder />,
    },
  ],
}
