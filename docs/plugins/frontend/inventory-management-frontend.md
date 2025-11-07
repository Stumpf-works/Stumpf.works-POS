# Inventory Management Plugin - Frontend Integration

## Übersicht

Bestandsverwaltung mit Lieferanten, Einkaufsbestellungen, Bestandsbewegungen und automatischen Nachbestellvorschlägen.

## Key Components

### 1. Stock Overview Dashboard
```tsx
// Stock levels with low stock alerts
- Real-time stock levels with color-coded status
- Quick action buttons for stock adjustments
- Low stock warnings with reorder suggestions
```

### 2. Supplier Management
```tsx
// Supplier CRUD operations
- Supplier list with contact information
- Order history per supplier
- Performance metrics
```

### 3. Purchase Orders
```tsx
// PO creation and management
- Multi-item purchase order form
- Approval workflow
- Receive goods functionality
- Cost tracking
```

### 4. Stock Movements
```tsx
// Movement tracking
- Movement history log
- Filter by type (in/out/adjustment/waste)
- Export functionality
```

### 5. Inventory Count
```tsx
// Physical inventory
- Count sheet generation
- Variance reporting
- Adjustment processing
```

## Main Views

```tsx
// src/pages/plugins/inventory/InventoryDashboard.tsx
export function InventoryDashboard() {
  return (
    <div>
      <StockLevelCards />
      <LowStockAlerts />
      <RecentMovements />
      <QuickActions />
    </div>
  );
}

// src/pages/plugins/inventory/PurchaseOrderForm.tsx
export function PurchaseOrderForm() {
  // Multi-step form:
  // 1. Select supplier
  // 2. Add items
  // 3. Review & submit
}
```

## API Hooks

```tsx
export function useStockLevels() {
  return useQuery({
    queryKey: ['inventory', 'stock'],
    queryFn: () => api.get('/inventory/stock-levels'),
  });
}

export function useCreatePurchaseOrder() {
  return useMutation({
    mutationFn: (data) => api.post('/inventory/purchase-orders', data),
  });
}
```

## Features
- **Real-time stock tracking**
- **Automated reorder points**
- **Supplier comparison**
- **Barcode scanning support**
- **Export to Excel**
- **Cost analysis**

## Routing
```tsx
/inventory
  /stock - Stock overview
  /suppliers - Supplier management
  /purchase-orders - PO management
  /movements - Movement history
  /counts - Physical inventory
```
