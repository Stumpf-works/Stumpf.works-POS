import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { analyticsApi } from '@/services/pluginApi'
import { Dashboard, Report, KPIMetric, DateRange } from '@/types/plugins'
import toast from 'react-hot-toast'

// Dashboards
export function useDashboards() {
  return useQuery({
    queryKey: ['analytics', 'dashboards'],
    queryFn: async () => {
      const data = await analyticsApi.getDashboards()
      return data.dashboards
    },
  })
}

export function useDashboard(id: number) {
  return useQuery({
    queryKey: ['analytics', 'dashboards', id],
    queryFn: () => analyticsApi.getDashboard(id),
    enabled: !!id,
  })
}

export function useCreateDashboard() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Dashboard>) => analyticsApi.createDashboard(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analytics', 'dashboards'] })
      toast.success('Dashboard erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}

// Reports
export function useReports() {
  return useQuery({
    queryKey: ['analytics', 'reports'],
    queryFn: async () => {
      const data = await analyticsApi.getReports()
      return data.reports
    },
  })
}

export function useReport(id: number) {
  return useQuery({
    queryKey: ['analytics', 'reports', id],
    queryFn: () => analyticsApi.getReport(id),
    enabled: !!id,
  })
}

export function useRunReport() {
  return useMutation({
    mutationFn: ({ id, filters }: { id: number; filters?: any }) =>
      analyticsApi.runReport(id, filters),
    onSuccess: () => {
      toast.success('Bericht generiert')
    },
    onError: () => {
      toast.error('Fehler beim Generieren')
    },
  })
}

// KPIs
export function useKPIs(dateRange?: DateRange) {
  return useQuery({
    queryKey: ['analytics', 'kpis', dateRange],
    queryFn: async () => {
      const data = await analyticsApi.getKPIs(dateRange)
      return data.kpis
    },
  })
}

// Forecasting
export function useForecast(metric: string, days: number) {
  return useQuery({
    queryKey: ['analytics', 'forecast', metric, days],
    queryFn: async () => {
      const data = await analyticsApi.getForecast(metric, days)
      return data.forecast
    },
    enabled: !!metric && !!days,
  })
}
