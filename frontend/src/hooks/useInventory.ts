import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { inventoryApi } from '@/services/pluginApi'
import { InventoryItem, Supplier, PurchaseOrder, StockMovement } from '@/types/plugins'
import toast from 'react-hot-toast'

// Inventory Items
export function useInventoryItems(params?: any) {
  return useQuery({
    queryKey: ['inventory', 'items', params],
    queryFn: async () => {
      const data = await inventoryApi.getInventoryItems(params)
      return data.items
    },
  })
}

export function useInventoryItem(id: number) {
  return useQuery({
    queryKey: ['inventory', 'items', id],
    queryFn: () => inventoryApi.getInventoryItem(id),
    enabled: !!id,
  })
}

export function useUpdateInventoryItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<InventoryItem> }) =>
      inventoryApi.updateInventoryItem(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'items'] })
      toast.success('Bestand aktualisiert')
    },
    onError: () => {
      toast.error('Fehler beim Aktualisieren')
    },
  })
}

// Stock Movements
export function useStockMovements(productId?: number) {
  return useQuery({
    queryKey: ['inventory', 'movements', productId],
    queryFn: async () => {
      const data = await inventoryApi.getStockMovements(productId)
      return data.movements
    },
  })
}

export function useAddStockMovement() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<StockMovement>) => inventoryApi.addStockMovement(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      toast.success('Bewegung hinzugefügt')
    },
    onError: () => {
      toast.error('Fehler beim Hinzufügen')
    },
  })
}

// Suppliers
export function useSuppliers() {
  return useQuery({
    queryKey: ['inventory', 'suppliers'],
    queryFn: async () => {
      const data = await inventoryApi.getSuppliers()
      return data.suppliers
    },
  })
}

export function useCreateSupplier() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Supplier>) => inventoryApi.createSupplier(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'suppliers'] })
      toast.success('Lieferant erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Purchase Orders
export function usePurchaseOrders(status?: any) {
  return useQuery({
    queryKey: ['inventory', 'purchase-orders', status],
    queryFn: async () => {
      const data = await inventoryApi.getPurchaseOrders(status)
      return data.orders
    },
  })
}

export function useCreatePurchaseOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) => inventoryApi.createPurchaseOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'purchase-orders'] })
      toast.success('Bestellung erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}
