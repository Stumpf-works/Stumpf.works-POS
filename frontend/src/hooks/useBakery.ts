import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { bakeryApi } from '@/services/pluginApi'
import { Recipe, ProductionPlan, Batch, RecipeCategory, BatchStatus } from '@/types/plugins'
import toast from 'react-hot-toast'

// Recipes
export function useRecipes(category?: RecipeCategory) {
  return useQuery({
    queryKey: ['bakery', 'recipes', category],
    queryFn: async () => {
      const data = await bakeryApi.getRecipes(category)
      return data.recipes
    },
  })
}

export function useRecipe(id: number) {
  return useQuery({
    queryKey: ['bakery', 'recipes', id],
    queryFn: () => bakeryApi.getRecipe(id),
    enabled: !!id,
  })
}

export function useCreateRecipe() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Recipe>) => bakeryApi.createRecipe(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bakery', 'recipes'] })
      toast.success('Rezept erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Production Plans
export function useProductionPlans(date?: string) {
  return useQuery({
    queryKey: ['bakery', 'production-plans', date],
    queryFn: async () => {
      const data = await bakeryApi.getProductionPlans(date)
      return data.plans
    },
  })
}

export function useCreateProductionPlan() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<ProductionPlan>) => bakeryApi.createProductionPlan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bakery', 'production-plans'] })
      toast.success('Produktionsplan erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Batches
export function useBatches(status?: BatchStatus, date?: string) {
  return useQuery({
    queryKey: ['bakery', 'batches', status, date],
    queryFn: async () => {
      const data = await bakeryApi.getBatches(status, date)
      return data.batches
    },
  })
}

export function useUpdateBatchStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: BatchStatus }) =>
      bakeryApi.updateBatchStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bakery', 'batches'] })
      toast.success('Status aktualisiert')
    },
    onError: () => {
      toast.error('Fehler beim Aktualisieren')
    },
  })
}
