import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tableApi } from '@/services/pluginApi'
import { Floor, Reservation, TableStatus } from '@/types/plugins'
import toast from 'react-hot-toast'

// Floors
export function useFloors() {
  return useQuery({
    queryKey: ['table-management', 'floors'],
    queryFn: async () => {
      const data = await tableApi.getFloors()
      return data.floors
    },
  })
}

export function useFloor(id: number) {
  return useQuery({
    queryKey: ['table-management', 'floors', id],
    queryFn: () => tableApi.getFloor(id),
    enabled: !!id,
  })
}

export function useCreateFloor() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Floor>) => tableApi.createFloor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['table-management', 'floors'] })
      toast.success('Etage erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Tables
export function useTables(floorId?: number) {
  return useQuery({
    queryKey: ['table-management', 'tables', floorId],
    queryFn: async () => {
      const data = await tableApi.getTables(floorId)
      return data.tables
    },
  })
}

export function useTable(id: number) {
  return useQuery({
    queryKey: ['table-management', 'tables', id],
    queryFn: () => tableApi.getTable(id),
    enabled: !!id,
  })
}

export function useUpdateTableStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: TableStatus }) =>
      tableApi.updateTableStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['table-management', 'tables'] })
      toast.success('Tischstatus aktualisiert')
    },
    onError: () => {
      toast.error('Fehler beim Aktualisieren')
    },
  })
}

// Reservations
export function useReservations(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['table-management', 'reservations', params],
    queryFn: async () => {
      const data = await tableApi.getReservations(params)
      return data.reservations
    },
  })
}

export function useReservation(id: number) {
  return useQuery({
    queryKey: ['table-management', 'reservations', id],
    queryFn: () => tableApi.getReservation(id),
    enabled: !!id,
  })
}

export function useCreateReservation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Reservation>) => tableApi.createReservation(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['table-management', 'reservations'] })
      toast.success('Reservierung erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

export function useCancelReservation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => tableApi.cancelReservation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['table-management', 'reservations'] })
      toast.success('Reservierung storniert')
    },
    onError: () => {
      toast.error('Fehler beim Stornieren')
    },
  })
}

export function useSeatReservation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => tableApi.seatReservation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['table-management', 'reservations'] })
      queryClient.invalidateQueries({ queryKey: ['table-management', 'tables'] })
      toast.success('Gäste platziert')
    },
    onError: () => {
      toast.error('Fehler beim Platzieren')
    },
  })
}
