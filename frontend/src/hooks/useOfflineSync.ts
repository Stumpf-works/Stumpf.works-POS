import { useEffect, useState, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/services/api'
import { offlineStorage } from '@/services/offlineStorage'

export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [isSyncing, setIsSyncing] = useState(false)
  const [syncStatus, setSyncStatus] = useState<{
    pendingTransactions: number
    queueItems: number
  }>({
    pendingTransactions: 0,
    queueItems: 0,
  })

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      toast.success('Verbindung wiederhergestellt')
      // Trigger sync when coming online
      syncOfflineData()
    }

    const handleOffline = () => {
      setIsOnline(false)
      toast.error('Keine Verbindung - Offline-Modus aktiviert', {
        duration: 5000,
      })
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Update sync status
  const updateSyncStatus = useCallback(async () => {
    const stats = await offlineStorage.getStats()
    setSyncStatus({
      pendingTransactions: stats.pendingTransactionsCount,
      queueItems: stats.queueItemsCount,
    })
  }, [])

  // Sync offline data to server
  const syncOfflineData = useCallback(async () => {
    if (!isOnline || isSyncing) return

    setIsSyncing(true)

    try {
      // Sync pending transactions
      const pendingTransactions = await offlineStorage.getPendingTransactions()

      for (const pending of pendingTransactions) {
        try {
          await api.transactions.create(pending.transactionData)
          await offlineStorage.markTransactionSynced(pending.id)
          toast.success(`Transaktion ${pending.id.slice(0, 8)}... synchronisiert`)
        } catch (error) {
          console.error('Failed to sync transaction:', error)
          // Keep in queue for next sync attempt
        }
      }

      // Sync offline queue items
      const queueItems = await offlineStorage.getOfflineQueue()

      for (const item of queueItems) {
        try {
          // Handle different queue item types
          switch (item.type) {
            case 'stock_adjustment':
              await api.products.adjustStock(
                item.data.productId,
                item.data.quantity,
                item.data.reason
              )
              break
            case 'product_update':
              await api.products.update(item.data.id, item.data)
              break
            // Add more cases as needed
          }

          await offlineStorage.markQueueItemSynced(item.id)
        } catch (error) {
          console.error('Failed to sync queue item:', error)
        }
      }

      // Update status
      await updateSyncStatus()

      const totalSynced = pendingTransactions.length + queueItems.length
      if (totalSynced > 0) {
        toast.success(`${totalSynced} Elemente synchronisiert`)
      }
    } catch (error) {
      console.error('Sync failed:', error)
      toast.error('Synchronisierung fehlgeschlagen')
    } finally {
      setIsSyncing(false)
    }
  }, [isOnline, isSyncing, updateSyncStatus])

  // Periodic sync (every 5 minutes when online)
  useEffect(() => {
    if (!isOnline) return

    const interval = setInterval(() => {
      syncOfflineData()
    }, 5 * 60 * 1000) // 5 minutes

    return () => clearInterval(interval)
  }, [isOnline, syncOfflineData])

  // Initial sync status
  useEffect(() => {
    updateSyncStatus()
  }, [updateSyncStatus])

  return {
    isOnline,
    isSyncing,
    syncStatus,
    syncOfflineData,
    updateSyncStatus,
  }
}
