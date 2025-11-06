# ADR 0006: Offline-First Architecture mit IndexedDB

## Status
Accepted

## Kontext
Ein POS-System muss auch bei Internetausfall funktionsfähig bleiben. Geschäfte können nicht auf stabile Internetverbindung verlassen:
- Verkäufe dürfen nicht unterbrochen werden
- Produktinformationen müssen lokal verfügbar sein
- Transaktionen müssen später synchronisiert werden
- User Experience soll sich nicht unterscheiden (online/offline)

Anforderungen:
- Verkäufe ohne Internet
- Automatische Synchronisation bei Wiederverbindung
- Konfliktauflösung bei parallelen Änderungen
- Minimale Latenz

## Entscheidung
Wir haben uns für eine **Offline-First Architecture mit IndexedDB** entschieden:

- **IndexedDB:** Browser-native NoSQL-Datenbank
- **Sync Service:** Automatische Synchronisation im Hintergrund
- **Conflict Resolution:** Last-Write-Wins mit Logging
- **Progressive Web App (PWA):** Service Worker für Offline-Unterstützung

## Alternativen

### 1. Rein Server-basiert (kein Offline)
**Pro:**
- Einfachste Implementierung
- Keine Sync-Probleme
- Single Source of Truth

**Contra:**
- System ist offline nicht nutzbar
- Geschäftskritischer Ausfall bei Netzproblemen
- Dealbreaker für viele Kunden

### 2. LocalStorage
**Pro:**
- Einfache API
- Synchron

**Contra:**
- Nur 5-10MB Speicher
- Kein Query-Support
- Blocking API
- Zu limitiert für Use Case

### 3. SQLite (via sql.js)
**Pro:**
- Vollständige SQL-Datenbank
- Relational Model

**Contra:**
- WASM-Overhead (mehrere MB)
- Komplexer als benötigt
- Performance-Probleme bei großen Datensets

### 4. IndexedDB mit Sync (Gewählt)
**Pro:**
- Native Browser-API
- Async/Non-blocking
- Großer Speicher (>100MB)
- Gute Performance
- Index-Support

**Contra:**
- Komplexere API als LocalStorage
- Erfordert Wrapper-Library (z.B. idb)
- Sync-Logic muss implementiert werden

## Konsequenzen

### Positiv
- **Resilience:** System funktioniert offline
- **Performance:** Lokale Daten sind sofort verfügbar
- **User Experience:** Keine Wartezeiten bei schlechter Verbindung
- **Business Continuity:** Verkäufe können immer getätigt werden

### Negativ
- **Komplexität:** Sync-Logic ist komplex
- **Conflicts:** Mögliche Datenkonflikte müssen behandelt werden
- **Storage Management:** Browser-Speicher kann voll laufen
- **Testing:** Offline-Szenarien sind schwierig zu testen

### Neutral
- **Data Consistency:** Eventual Consistency statt Strong Consistency
- **Network Usage:** Mehr Datenübertragung für Sync

## Architektur

### Offline Storage Service
```typescript
class OfflineStorageService {
  private db: IDBPDatabase

  async initialize() {
    this.db = await openDB('pos-offline', 1, {
      upgrade(db) {
        // Products Store
        db.createObjectStore('products', { keyPath: 'id' })

        // Pending Transactions Store
        const txnStore = db.createObjectStore('pendingTransactions', {
          keyPath: 'id',
          autoIncrement: true
        })
        txnStore.createIndex('timestamp', 'timestamp')

        // Offline Queue Store
        db.createObjectStore('offlineQueue', {
          keyPath: 'id',
          autoIncrement: true
        })
      }
    })
  }

  async saveProduct(product: Product) {
    await this.db.put('products', product)
  }

  async getProduct(id: number): Promise<Product | undefined> {
    return this.db.get('products', id)
  }

  async savePendingTransaction(transaction: Transaction) {
    await this.db.add('pendingTransactions', {
      ...transaction,
      timestamp: Date.now()
    })
  }

  async getPendingTransactions(): Promise<Transaction[]> {
    return this.db.getAll('pendingTransactions')
  }
}
```

### Sync Strategy
```typescript
class SyncService {
  private isOnline = navigator.onLine
  private syncInterval: number

  constructor() {
    window.addEventListener('online', () => this.handleOnline())
    window.addEventListener('offline', () => this.handleOffline())

    // Periodic sync every 5 minutes when online
    this.syncInterval = setInterval(() => {
      if (this.isOnline) this.sync()
    }, 5 * 60 * 1000)
  }

  async handleOnline() {
    this.isOnline = true
    await this.sync()
  }

  handleOffline() {
    this.isOnline = false
  }

  async sync() {
    // 1. Upload pending transactions
    const pending = await offlineStorage.getPendingTransactions()
    for (const txn of pending) {
      try {
        await api.post('/transactions', txn)
        await offlineStorage.markSynced(txn.id)
      } catch (error) {
        console.error('Sync failed for transaction', txn.id, error)
      }
    }

    // 2. Download updated products
    const products = await api.get('/products')
    for (const product of products) {
      await offlineStorage.saveProduct(product)
    }

    // 3. Process offline queue
    const queue = await offlineStorage.getOfflineQueue()
    for (const item of queue) {
      await this.processQueueItem(item)
    }
  }
}
```

### React Hook for Offline Support
```typescript
export function useOfflineSync() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingCount, setPendingCount] = useState(0)

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      syncOfflineData()
    }

    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const syncOfflineData = async () => {
    const pending = await offlineStorage.getPendingTransactions()
    setPendingCount(pending.length)

    for (const txn of pending) {
      await syncTransaction(txn)
    }

    setPendingCount(0)
  }

  return { isOnline, pendingCount, syncOfflineData }
}
```

## Conflict Resolution

### Strategy: Last-Write-Wins mit Audit Log
```typescript
async function resolveConflict(local: any, remote: any) {
  // Compare timestamps
  if (local.updated_at > remote.updated_at) {
    // Local version is newer - keep it
    return local
  } else {
    // Remote version is newer - use it
    // Log conflict for audit
    await logConflict({
      entity: local.id,
      localVersion: local,
      remoteVersion: remote,
      resolution: 'remote',
      timestamp: Date.now()
    })
    return remote
  }
}
```

## Data Flow

### Offline Transaction Creation
```
1. User creates transaction in POS
2. Transaction saved to IndexedDB
3. UI shows "Offline - Will sync when online"
4. Transaction added to sync queue
```

### Online Sync
```
1. Network comes back online
2. Sync service detects connectivity
3. Pending transactions uploaded to server
4. Server processes and signs with TSE
5. Updated data synced back to IndexedDB
6. UI updated with success status
```

## Storage Management

### Quota Management
```typescript
async function checkStorageQuota() {
  const estimate = await navigator.storage.estimate()
  const usagePercent = (estimate.usage / estimate.quota) * 100

  if (usagePercent > 80) {
    // Clean up old data
    await cleanupOldTransactions()
    await cleanupOldProducts()
  }
}
```

### Data Cleanup Policy
- Synced transactions: Keep for 30 days
- Unsynced transactions: Never delete
- Product data: Keep latest version only
- Old logs: Delete after 90 days

## Testing Offline Scenarios

```typescript
describe('Offline Functionality', () => {
  it('should create transaction offline', async () => {
    // Simulate offline
    vi.stubGlobal('navigator', { onLine: false })

    await createTransaction(mockData)

    const pending = await offlineStorage.getPendingTransactions()
    expect(pending).toHaveLength(1)
  })

  it('should sync when online', async () => {
    // Add pending transaction
    await offlineStorage.savePendingTransaction(mockTransaction)

    // Simulate online
    vi.stubGlobal('navigator', { onLine: true })
    await syncService.sync()

    const pending = await offlineStorage.getPendingTransactions()
    expect(pending).toHaveLength(0)
  })
})
```

## Monitoring & Alerts

- **Pending Transaction Count:** Alert wenn >100 unsynced
- **Sync Failures:** Log alle fehlgeschlagenen Syncs
- **Storage Usage:** Warn bei >80% Quota
- **Offline Duration:** Track wie lange offline

## Validierung
- [x] Offline-Modus mit 50 Transaktionen getestet
- [x] Sync nach 24h Offline erfolgreich
- [x] Konfliktauflösung funktioniert
- [x] Storage Management verhindert Quota-Errors
- [x] Performance ist akzeptabel (<100ms für lokale Ops)

## Einschränkungen
- Nur Lese-Zugriff auf Produktdaten offline
- Admin-Funktionen erfordern Online-Verbindung
- Berichte werden nur online generiert
- User-Management ist nur online möglich

## Referenzen
- [IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [idb Library](https://github.com/jakearchibald/idb)
- [Offline-First Patterns](https://offlinefirst.org/)
- [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

## Datum
2024-01-15

## Autoren
- Stumpf.works Entwicklungsteam
