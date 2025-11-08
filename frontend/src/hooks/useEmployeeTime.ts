import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { employeeTimeApi } from '@/services/pluginApi'
import { Shift } from '@/types/plugins'
import toast from 'react-hot-toast'

// Time Entries
export function useTimeEntries(employeeId?: number, date?: string) {
  return useQuery({
    queryKey: ['employee-time', 'entries', employeeId, date],
    queryFn: async () => {
      const data = await employeeTimeApi.getTimeEntries(employeeId, date)
      return data.entries
    },
  })
}

export function useClockIn() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ employeeId, location }: { employeeId: number; location?: string }) =>
      employeeTimeApi.clockIn(employeeId, location),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-time', 'entries'] })
      toast.success('Eingecheckt')
    },
    onError: () => {
      toast.error('Fehler beim Einchecken')
    },
  })
}

export function useClockOut() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (employeeId: number) => employeeTimeApi.clockOut(employeeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-time', 'entries'] })
      toast.success('Ausgecheckt')
    },
    onError: () => {
      toast.error('Fehler beim Auschecken')
    },
  })
}

export function useStartBreak() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (employeeId: number) => employeeTimeApi.startBreak(employeeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-time', 'entries'] })
      toast.success('Pause gestartet')
    },
    onError: () => {
      toast.error('Fehler beim Starten der Pause')
    },
  })
}

export function useEndBreak() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (employeeId: number) => employeeTimeApi.endBreak(employeeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-time', 'entries'] })
      toast.success('Pause beendet')
    },
    onError: () => {
      toast.error('Fehler beim Beenden der Pause')
    },
  })
}

// Time Sheets
export function useTimeSheets(employeeId?: number, startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ['employee-time', 'timesheets', employeeId, startDate, endDate],
    queryFn: async () => {
      const data = await employeeTimeApi.getTimeSheets(employeeId, startDate, endDate)
      return data.timesheets
    },
  })
}

export function useTimeSheet(id: number) {
  return useQuery({
    queryKey: ['employee-time', 'timesheets', id],
    queryFn: () => employeeTimeApi.getTimeSheet(id),
    enabled: !!id,
  })
}

// Shifts
export function useShifts(employeeId?: number, date?: string) {
  return useQuery({
    queryKey: ['employee-time', 'shifts', employeeId, date],
    queryFn: async () => {
      const data = await employeeTimeApi.getShifts(employeeId, date)
      return data.shifts
    },
  })
}

export function useCreateShift() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Shift>) => employeeTimeApi.createShift(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-time', 'shifts'] })
      toast.success('Schicht erstellt')
    },
    onError: () => {
      toast.error('Fehler beim Erstellen')
    },
  })
}
