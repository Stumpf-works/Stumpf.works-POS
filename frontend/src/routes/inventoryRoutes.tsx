import { RouteObject } from 'react-router-dom'
import { StockDashboard } from '@/pages/plugins/inventory/StockDashboard'
import { SupplierList } from '@/pages/plugins/inventory/SupplierList'
import { PurchaseOrders } from '@/pages/plugins/inventory/PurchaseOrders'

export const inventoryRoutes: RouteObject = {
  path: 'inventory',
  children: [
    {
      index: true,
      element: <StockDashboard />,
    },
    {
      path: 'suppliers',
      element: <SupplierList />,
    },
    {
      path: 'purchase-orders',
      element: <PurchaseOrders />,
    },
  ],
}
