import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { loyaltyApi } from '@/services/pluginApi'
import { Reward, LoyaltyTier } from '@/types/plugins'
import toast from 'react-hot-toast'

// Customers
export function useLoyaltyCustomers(tier?: LoyaltyTier) {
  return useQuery({
    queryKey: ['loyalty', 'customers', tier],
    queryFn: async () => {
      const data = await loyaltyApi.getCustomers(tier)
      return data.customers
    },
  })
}

export function useLoyaltyCustomer(id: number) {
  return useQuery({
    queryKey: ['loyalty', 'customers', id],
    queryFn: () => loyaltyApi.getCustomer(id),
    enabled: !!id,
  })
}

export function useLoyaltyCustomerByQR(qrCode: string) {
  return useQuery({
    queryKey: ['loyalty', 'customers', 'qr', qrCode],
    queryFn: () => loyaltyApi.getCustomerByQR(qrCode),
    enabled: !!qrCode,
  })
}

export function useEnrollCustomer() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (customerId: number) => loyaltyApi.enrollCustomer(customerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loyalty', 'customers'] })
      toast.success('Kunde eingeschrieben')
    },
    onError: () => {
      toast.error('Fehler beim Einschreiben')
    },
  })
}

// Points
export function usePointTransactions(customerId: number) {
  return useQuery({
    queryKey: ['loyalty', 'points', customerId],
    queryFn: async () => {
      const data = await loyaltyApi.getPointTransactions(customerId)
      return data.transactions
    },
    enabled: !!customerId,
  })
}

export function useAddPoints() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ customerId, points, reason }: { customerId: number; points: number; reason?: string }) =>
      loyaltyApi.addPoints(customerId, points, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loyalty'] })
      toast.success('Punkte gutgeschrieben')
    },
    onError: () => {
      toast.error('Fehler beim Gutschreiben')
    },
  })
}

// Rewards
export function useRewards(tier?: LoyaltyTier) {
  return useQuery({
    queryKey: ['loyalty', 'rewards', tier],
    queryFn: async () => {
      const data = await loyaltyApi.getRewards(tier)
      return data.rewards
    },
  })
}

export function useCreateReward() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Reward>) => loyaltyApi.createReward(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loyalty', 'rewards'] })
      toast.success('Belohnung erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Redemptions
export function useRedemptions(customerId?: number) {
  return useQuery({
    queryKey: ['loyalty', 'redemptions', customerId],
    queryFn: async () => {
      const data = await loyaltyApi.getRedemptions(customerId)
      return data.redemptions
    },
  })
}

export function useRedeemReward() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ customerId, rewardId }: { customerId: number; rewardId: number }) =>
      loyaltyApi.redeemReward(customerId, rewardId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['loyalty'] })
      toast.success('Belohnung eingelöst')
    },
    onError: () => {
      toast.error('Fehler beim Einlösen')
    },
  })
}
