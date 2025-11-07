import { Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { LoadingState } from '@/components/shared/LoadingState'

// Lazy load all plugin routes
const PaymentRoutes = lazy(() => import('./paymentRoutes'))
const CashRoutes = lazy(() => import('./cashRoutes'))
const TableRoutes = lazy(() => import('./tableRoutes'))
const KitchenRoutes = lazy(() => import('./kitchenRoutes'))
const EmployeeTimeRoutes = lazy(() => import('./employeeTimeRoutes'))
const InventoryRoutes = lazy(() => import('./inventoryRoutes'))
const BakeryRoutes = lazy(() => import('./bakeryRoutes'))
const DeliveryRoutes = lazy(() => import('./deliveryRoutes'))
const LoyaltyRoutes = lazy(() => import('./loyaltyRoutes'))
const AnalyticsRoutes = lazy(() => import('./analyticsRoutes'))

export function PluginRoutes() {
  return (
    <Suspense fallback={<LoadingState message="Plugin wird geladen..." />}>
      <Routes>
        <Route path="payment/*" element={<PaymentRoutes />} />
        <Route path="cash/*" element={<CashRoutes />} />
        <Route path="tables/*" element={<TableRoutes />} />
        <Route path="kitchen/*" element={<KitchenRoutes />} />
        <Route path="employee-time/*" element={<EmployeeTimeRoutes />} />
        <Route path="inventory/*" element={<InventoryRoutes />} />
        <Route path="bakery/*" element={<BakeryRoutes />} />
        <Route path="delivery/*" element={<DeliveryRoutes />} />
        <Route path="loyalty/*" element={<LoyaltyRoutes />} />
        <Route path="analytics/*" element={<AnalyticsRoutes />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </Suspense>
  )
}
