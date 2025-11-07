import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { paymentApi } from '@/services/pluginApi'
import { PaymentProvider, PaymentTerminal, PaymentTransaction } from '@/types/plugins'
import toast from 'react-hot-toast'

// Providers
export function usePaymentProviders() {
  return useQuery({
    queryKey: ['payment', 'providers'],
    queryFn: async () => {
      const data = await paymentApi.getProviders()
      return data.providers
    },
  })
}

export function usePaymentProvider(id: number) {
  return useQuery({
    queryKey: ['payment', 'providers', id],
    queryFn: () => paymentApi.getProvider(id),
    enabled: !!id,
  })
}

export function useUpdatePaymentProvider() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<PaymentProvider> }) =>
      paymentApi.updateProvider(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'providers'] })
      toast.success('Anbieter aktualisiert')
    },
    onError: () => {
      toast.error('Fehler beim Aktualisieren')
    },
  })
}

// Terminals
export function usePaymentTerminals(providerId?: number) {
  return useQuery({
    queryKey: ['payment', 'terminals', providerId],
    queryFn: async () => {
      const data = await paymentApi.getTerminals(providerId)
      return data.terminals
    },
  })
}

export function useCreatePaymentTerminal() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<PaymentTerminal>) => paymentApi.createTerminal(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'terminals'] })
      toast.success('Terminal hinzugefügt')
    },
    onError: () => {
      toast.error('Fehler beim Hinzufügen')
    },
  })
}

// Transactions
export function usePaymentTransactions(params?: any) {
  return useQuery({
    queryKey: ['payment', 'transactions', params],
    queryFn: async () => {
      const data = await paymentApi.getTransactions(params)
      return data.transactions
    },
  })
}

export function usePaymentTransaction(id: number) {
  return useQuery({
    queryKey: ['payment', 'transactions', id],
    queryFn: () => paymentApi.getTransaction(id),
    enabled: !!id,
  })
}

export function useCreatePaymentTransaction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<PaymentTransaction>) => paymentApi.createTransaction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'transactions'] })
      toast.success('Zahlung verarbeitet')
    },
    onError: () => {
      toast.error('Zahlungsfehler')
    },
  })
}

export function useRefundTransaction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, amount }: { id: number; amount?: number }) =>
      paymentApi.refundTransaction(id, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment', 'transactions'] })
      toast.success('Rückerstattung erfolgreich')
    },
    onError: () => {
      toast.error('Rückerstattungsfehler')
    },
  })
}
