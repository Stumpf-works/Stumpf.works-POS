import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { cashApi } from '@/services/pluginApi'
import { CashRegister, CashMovement, CashCount } from '@/types/plugins'
import toast from 'react-hot-toast'

// Registers
export function useCashRegisters() {
  return useQuery({
    queryKey: ['cash', 'registers'],
    queryFn: async () => {
      const data = await cashApi.getRegisters()
      return data.registers
    },
  })
}

export function useCashRegister(id: number) {
  return useQuery({
    queryKey: ['cash', 'registers', id],
    queryFn: () => cashApi.getRegister(id),
    enabled: !!id,
  })
}

export function useCreateCashRegister() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<CashRegister>) => cashApi.createRegister(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cash', 'registers'] })
      toast.success('Kasse erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Sessions
export function useCashSessions(registerId?: number) {
  return useQuery({
    queryKey: ['cash', 'sessions', registerId],
    queryFn: async () => {
      const data = await cashApi.getSessions(registerId)
      return data.sessions
    },
  })
}

export function useCashSession(id: number) {
  return useQuery({
    queryKey: ['cash', 'sessions', id],
    queryFn: () => cashApi.getSession(id),
    enabled: !!id,
  })
}

export function useOpenCashSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ registerId, openingBalance }: { registerId: number; openingBalance: number }) =>
      cashApi.openSession(registerId, openingBalance),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cash', 'sessions'] })
      queryClient.invalidateQueries({ queryKey: ['cash', 'registers'] })
      toast.success('Kassensitzung geöffnet')
    },
    onError: () => {
      toast.error('Fehler beim Öffnen')
    },
  })
}

export function useCloseCashSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      sessionId,
      counts,
      notes,
    }: {
      sessionId: number
      counts: CashCount[]
      notes?: string
    }) => cashApi.closeSession(sessionId, counts, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cash', 'sessions'] })
      queryClient.invalidateQueries({ queryKey: ['cash', 'registers'] })
      toast.success('Kassensitzung geschlossen')
    },
    onError: () => {
      toast.error('Fehler beim Schließen')
    },
  })
}

// Movements
export function useCashMovements(sessionId: number) {
  return useQuery({
    queryKey: ['cash', 'movements', sessionId],
    queryFn: async () => {
      const data = await cashApi.getMovements(sessionId)
      return data.movements
    },
    enabled: !!sessionId,
  })
}

export function useAddCashMovement() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ sessionId, data }: { sessionId: number; data: Partial<CashMovement> }) =>
      cashApi.addMovement(sessionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cash', 'movements'] })
      toast.success('Bewegung hinzugefügt')
    },
    onError: () => {
      toast.error('Fehler beim Hinzufügen')
    },
  })
}

// Z-Report
export function useGenerateZReport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (sessionId: number) => cashApi.generateZReport(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cash', 'sessions'] })
      toast.success('Z-Bericht generiert')
    },
    onError: () => {
      toast.error('Fehler beim Generieren')
    },
  })
}
