import { RouteObject } from 'react-router-dom'
import { PaymentDashboard } from '@/pages/plugins/payment/PaymentDashboard'
import { PaymentProviderList } from '@/pages/plugins/payment/PaymentProviderList'
import { TransactionHistory } from '@/pages/plugins/payment/TransactionHistory'

export const paymentRoutes: RouteObject = {
  path: 'payment',
  children: [
    {
      index: true,
      element: <PaymentDashboard />,
    },
    {
      path: 'providers',
      element: <PaymentProviderList />,
    },
    {
      path: 'transactions',
      element: <TransactionHistory />,
    },
  ],
}
