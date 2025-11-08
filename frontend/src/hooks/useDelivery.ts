import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { deliveryApi } from '@/services/pluginApi'
import { DeliveryStatus, DriverStatus } from '@/types/plugins'
import toast from 'react-hot-toast'

// Delivery Orders
export function useDeliveryOrders(status?: DeliveryStatus, driverId?: number) {
  return useQuery({
    queryKey: ['delivery', 'orders', status, driverId],
    queryFn: async () => {
      const data = await deliveryApi.getDeliveryOrders(status, driverId)
      return data.orders
    },
    refetchInterval: 10000, // Auto-refresh every 10 seconds
  })
}

export function useDeliveryOrder(id: number) {
  return useQuery({
    queryKey: ['delivery', 'orders', id],
    queryFn: () => deliveryApi.getDeliveryOrder(id),
    enabled: !!id,
  })
}

export function useAssignDriver() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ orderId, driverId }: { orderId: number; driverId: number }) =>
      deliveryApi.assignDriver(orderId, driverId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['delivery'] })
      toast.success('Fahrer zugewiesen')
    },
    onError: () => {
      toast.error('Fehler beim Zuweisen')
    },
  })
}

export function useUpdateDeliveryStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ orderId, status }: { orderId: number; status: DeliveryStatus }) =>
      deliveryApi.updateDeliveryStatus(orderId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['delivery', 'orders'] })
      toast.success('Status aktualisiert')
    },
    onError: () => {
      toast.error('Fehler beim Aktualisieren')
    },
  })
}

// Drivers
export function useDrivers(status?: DriverStatus) {
  return useQuery({
    queryKey: ['delivery', 'drivers', status],
    queryFn: async () => {
      const data = await deliveryApi.getDrivers(status)
      return data.drivers
    },
  })
}

export function useDriver(id: number) {
  return useQuery({
    queryKey: ['delivery', 'drivers', id],
    queryFn: () => deliveryApi.getDriver(id),
    enabled: !!id,
  })
}

export function useUpdateDriverStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: DriverStatus }) =>
      deliveryApi.updateDriverStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['delivery', 'drivers'] })
      toast.success('Fahrerstatus aktualisiert')
    },
    onError: () => {
      toast.error('Fehler beim Aktualisieren')
    },
  })
}
