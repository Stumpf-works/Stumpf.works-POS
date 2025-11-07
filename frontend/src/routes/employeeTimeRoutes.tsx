import { RouteObject } from 'react-router-dom'
import { ClockTerminal } from '@/pages/plugins/employee-time/ClockTerminal'
import { TimeSheetView } from '@/pages/plugins/employee-time/TimeSheetView'
import { ShiftPlanner } from '@/pages/plugins/employee-time/ShiftPlanner'

export const employeeTimeRoutes: RouteObject = {
  path: 'employee-time',
  children: [
    {
      index: true,
      element: <ClockTerminal />,
    },
    {
      path: 'timesheets',
      element: <TimeSheetView />,
    },
    {
      path: 'shifts',
      element: <ShiftPlanner />,
    },
  ],
}
