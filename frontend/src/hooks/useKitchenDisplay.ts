import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { kitchenApi } from '@/services/pluginApi'
import { KitchenStation, KitchenOrder, OrderStatus } from '@/types/plugins'
import toast from 'react-hot-toast'

// Stations
export function useKitchenStations() {
  return useQuery({
    queryKey: ['kitchen', 'stations'],
    queryFn: async () => {
      const data = await kitchenApi.getStations()
      return data.stations
    },
  })
}

export function useKitchenStation(id: number) {
  return useQuery({
    queryKey: ['kitchen', 'stations', id],
    queryFn: () => kitchenApi.getStation(id),
    enabled: !!id,
  })
}

export function useCreateKitchenStation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<KitchenStation>) => kitchenApi.createStation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kitchen', 'stations'] })
      toast.success('Station erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Orders
export function useKitchenOrders(stationId?: number, status?: OrderStatus) {
  return useQuery({
    queryKey: ['kitchen', 'orders', stationId, status],
    queryFn: async () => {
      const data = await kitchenApi.getOrders(stationId, status)
      return data.orders
    },
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  })
}

export function useKitchenOrder(id: number) {
  return useQuery({
    queryKey: ['kitchen', 'orders', id],
    queryFn: () => kitchenApi.getOrder(id),
    enabled: !!id,
  })
}

export function useUpdateOrderStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: OrderStatus }) =>
      kitchenApi.updateOrderStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kitchen', 'orders'] })
      toast.success('Status aktualisiert')
    },
    onError: () => {
      toast.error('Fehler beim Aktualisieren')
    },
  })
}

export function useStartOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => kitchenApi.startOrder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kitchen', 'orders'] })
      toast.success('Bestellung gestartet')
    },
    onError: () => {
      toast.error('Fehler beim Starten')
    },
  })
}

export function useCompleteOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => kitchenApi.completeOrder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kitchen', 'orders'] })
      toast.success('Bestellung fertig')
    },
    onError: () => {
      toast.error('Fehler beim Abschließen')
    },
  })
}
