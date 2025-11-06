import { openDB, DBSchema, IDBPDatabase } from 'idb'
import { Transaction, Product } from '@/types'

interface POSDatabase extends DBSchema {
  products: {
    key: number
    value: Product
    indexes: { 'by-barcode': string; 'by-sku': string }
  }
  pendingTransactions: {
    key: string // UUID
    value: {
      id: string
      transactionData: any
      createdAt: string
      synced: boolean
    }
  }
  offlineQueue: {
    key: string // UUID
    value: {
      id: string
      type: 'product_update' | 'stock_adjustment' | 'other'
      action: string
      data: any
      createdAt: string
      synced: boolean
    }
  }
}

class OfflineStorageService {
  private dbName = 'stumpfworks-pos-db'
  private dbVersion = 1
  private db: IDBPDatabase<POSDatabase> | null = null

  async init(): Promise<void> {
    if (this.db) return

    this.db = await openDB<POSDatabase>(this.dbName, this.dbVersion, {
      upgrade(db) {
        // Products store
        if (!db.objectStoreNames.contains('products')) {
          const productStore = db.createObjectStore('products', { keyPath: 'id' })
          productStore.createIndex('by-barcode', 'barcode')
          productStore.createIndex('by-sku', 'sku')
        }

        // Pending transactions store
        if (!db.objectStoreNames.contains('pendingTransactions')) {
          db.createObjectStore('pendingTransactions', { keyPath: 'id' })
        }

        // Offline queue store
        if (!db.objectStoreNames.contains('offlineQueue')) {
          db.createObjectStore('offlineQueue', { keyPath: 'id' })
        }
      },
    })
  }

  // Product methods
  async saveProducts(products: Product[]): Promise<void> {
    await this.init()
    if (!this.db) return

    const tx = this.db.transaction('products', 'readwrite')
    const store = tx.objectStore('products')

    await Promise.all(products.map((product) => store.put(product)))
    await tx.done
  }

  async getProducts(): Promise<Product[]> {
    await this.init()
    if (!this.db) return []

    return await this.db.getAll('products')
  }

  async getProductByBarcode(barcode: string): Promise<Product | undefined> {
    await this.init()
    if (!this.db) return undefined

    return await this.db.getFromIndex('products', 'by-barcode', barcode)
  }

  async getProductBySKU(sku: string): Promise<Product | undefined> {
    await this.init()
    if (!this.db) return undefined

    return await this.db.getFromIndex('products', 'by-sku', sku)
  }

  async updateProductStock(productId: number, newStock: number): Promise<void> {
    await this.init()
    if (!this.db) return

    const product = await this.db.get('products', productId)
    if (product) {
      product.stock_quantity = newStock
      await this.db.put('products', product)
    }
  }

  // Pending transactions methods
  async savePendingTransaction(transactionData: any): Promise<string> {
    await this.init()
    if (!this.db) throw new Error('Database not initialized')

    const id = crypto.randomUUID()
    const pendingTx = {
      id,
      transactionData,
      createdAt: new Date().toISOString(),
      synced: false,
    }

    await this.db.put('pendingTransactions', pendingTx)
    return id
  }

  async getPendingTransactions(): Promise<any[]> {
    await this.init()
    if (!this.db) return []

    const all = await this.db.getAll('pendingTransactions')
    return all.filter((tx) => !tx.synced)
  }

  async markTransactionSynced(id: string): Promise<void> {
    await this.init()
    if (!this.db) return

    const tx = await this.db.get('pendingTransactions', id)
    if (tx) {
      tx.synced = true
      await this.db.put('pendingTransactions', tx)
    }
  }

  async deletePendingTransaction(id: string): Promise<void> {
    await this.init()
    if (!this.db) return

    await this.db.delete('pendingTransactions', id)
  }

  // Offline queue methods
  async addToOfflineQueue(
    type: 'product_update' | 'stock_adjustment' | 'other',
    action: string,
    data: any
  ): Promise<string> {
    await this.init()
    if (!this.db) throw new Error('Database not initialized')

    const id = crypto.randomUUID()
    const queueItem = {
      id,
      type,
      action,
      data,
      createdAt: new Date().toISOString(),
      synced: false,
    }

    await this.db.put('offlineQueue', queueItem)
    return id
  }

  async getOfflineQueue(): Promise<any[]> {
    await this.init()
    if (!this.db) return []

    const all = await this.db.getAll('offlineQueue')
    return all.filter((item) => !item.synced)
  }

  async markQueueItemSynced(id: string): Promise<void> {
    await this.init()
    if (!this.db) return

    const item = await this.db.get('offlineQueue', id)
    if (item) {
      item.synced = true
      await this.db.put('offlineQueue', item)
    }
  }

  async deleteQueueItem(id: string): Promise<void> {
    await this.init()
    if (!this.db) return

    await this.db.delete('offlineQueue', id)
  }

  // Utility methods
  async clearAllData(): Promise<void> {
    await this.init()
    if (!this.db) return

    await this.db.clear('products')
    await this.db.clear('pendingTransactions')
    await this.db.clear('offlineQueue')
  }

  async getStats(): Promise<{
    productsCount: number
    pendingTransactionsCount: number
    queueItemsCount: number
  }> {
    await this.init()
    if (!this.db) {
      return {
        productsCount: 0,
        pendingTransactionsCount: 0,
        queueItemsCount: 0,
      }
    }

    const products = await this.db.count('products')
    const pendingTransactions = await this.db.count('pendingTransactions')
    const queueItems = await this.db.count('offlineQueue')

    return {
      productsCount: products,
      pendingTransactionsCount: pendingTransactions,
      queueItemsCount: queueItems,
    }
  }
}

// Singleton instance
export const offlineStorage = new OfflineStorageService()
