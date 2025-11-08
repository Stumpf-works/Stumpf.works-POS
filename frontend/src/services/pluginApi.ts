// Plugin-specific API services
import { api } from './api'
import * as Types from '@/types/plugins'

// ===================================
// PAYMENT GATEWAY API
// ===================================

export const paymentApi = {
  // Providers
  getProviders: () => api.get<{ providers: Types.PaymentProvider[] }>('/payments/providers'),
  getProvider: (id: number) => api.get<Types.PaymentProvider>(`/payments/providers/${id}`),
  createProvider: (data: Partial<Types.PaymentProvider>) => api.post('/payments/providers', data),
  updateProvider: (id: number, data: Partial<Types.PaymentProvider>) => api.put(`/payments/providers/${id}`, data),
  deleteProvider: (id: number) => api.delete(`/payments/providers/${id}`),

  // Terminals
  getTerminals: (providerId?: number) => api.get<{ terminals: Types.PaymentTerminal[] }>('/payments/terminals', { params: { provider_id: providerId } }),
  getTerminal: (id: number) => api.get<Types.PaymentTerminal>(`/payments/terminals/${id}`),
  createTerminal: (data: Partial<Types.PaymentTerminal>) => api.post('/payments/terminals', data),
  updateTerminal: (id: number, data: Partial<Types.PaymentTerminal>) => api.put(`/payments/terminals/${id}`, data),
  deleteTerminal: (id: number) => api.delete(`/payments/terminals/${id}`),

  // Transactions
  getTransactions: (params?: Record<string, unknown>) => api.get<{ transactions: Types.PaymentTransaction[] }>('/payments/transactions', { params }),
  getTransaction: (id: number) => api.get<Types.PaymentTransaction>(`/payments/transactions/${id}`),
  createTransaction: (data: Partial<Types.PaymentTransaction>) => api.post('/payments/transactions', data),
  refundTransaction: (id: number, amount?: number) => api.post(`/payments/transactions/${id}/refund`, { amount }),
}

// ===================================
// CASH MANAGEMENT API
// ===================================

export const cashApi = {
  // Registers
  getRegisters: () => api.get<{ registers: Types.CashRegister[] }>('/cash/registers'),
  getRegister: (id: number) => api.get<Types.CashRegister>(`/cash/registers/${id}`),
  createRegister: (data: Partial<Types.CashRegister>) => api.post('/cash/registers', data),
  updateRegister: (id: number, data: Partial<Types.CashRegister>) => api.put(`/cash/registers/${id}`, data),

  // Sessions
  getSessions: (registerId?: number) => api.get<{ sessions: Types.CashSession[] }>('/cash/sessions', { params: { register_id: registerId } }),
  getSession: (id: number) => api.get<Types.CashSession>(`/cash/sessions/${id}`),
  openSession: (registerId: number, openingBalance: number) => api.post('/cash/sessions/open', { register_id: registerId, opening_balance: openingBalance }),
  closeSession: (sessionId: number, counts: Types.CashCount[], notes?: string) => api.post(`/cash/sessions/${sessionId}/close`, { counts, notes }),

  // Movements
  getMovements: (sessionId: number) => api.get<{ movements: Types.CashMovement[] }>(`/cash/sessions/${sessionId}/movements`),
  addMovement: (sessionId: number, data: Partial<Types.CashMovement>) => api.post(`/cash/sessions/${sessionId}/movements`, data),

  // Z-Report
  generateZReport: (sessionId: number) => api.post(`/cash/sessions/${sessionId}/z-report`),
  downloadZReport: (sessionId: number) => api.get(`/cash/sessions/${sessionId}/z-report/download`, { responseType: 'blob' }),
}

// ===================================
// TABLE MANAGEMENT API
// ===================================

export const tableApi = {
  // Floors
  getFloors: () => api.get<{ floors: Types.Floor[] }>('/table-management/floors'),
  getFloor: (id: number) => api.get<Types.Floor>(`/table-management/floors/${id}`),
  createFloor: (data: Partial<Types.Floor>) => api.post('/table-management/floors', data),
  updateFloor: (id: number, data: Partial<Types.Floor>) => api.put(`/table-management/floors/${id}`, data),
  deleteFloor: (id: number) => api.delete(`/table-management/floors/${id}`),

  // Tables
  getTables: (floorId?: number) => api.get<{ tables: Types.Table[] }>('/table-management/tables', { params: { floor_id: floorId } }),
  getTable: (id: number) => api.get<Types.Table>(`/table-management/tables/${id}`),
  createTable: (data: Partial<Types.Table>) => api.post('/table-management/tables', data),
  updateTable: (id: number, data: Partial<Types.Table>) => api.put(`/table-management/tables/${id}`, data),
  deleteTable: (id: number) => api.delete(`/table-management/tables/${id}`),
  updateTableStatus: (id: number, status: Types.TableStatus) => api.put(`/table-management/tables/${id}/status`, { status }),

  // Reservations
  getReservations: (params?: Record<string, unknown>) => api.get<{ reservations: Types.Reservation[] }>('/table-management/reservations', { params }),
  getReservation: (id: number) => api.get<Types.Reservation>(`/table-management/reservations/${id}`),
  createReservation: (data: Partial<Types.Reservation>) => api.post('/table-management/reservations', data),
  updateReservation: (id: number, data: Partial<Types.Reservation>) => api.put(`/table-management/reservations/${id}`, data),
  cancelReservation: (id: number) => api.put(`/table-management/reservations/${id}/cancel`),
  seatReservation: (id: number) => api.put(`/table-management/reservations/${id}/seat`),
}

// ===================================
// KITCHEN DISPLAY API
// ===================================

export const kitchenApi = {
  // Stations
  getStations: () => api.get<{ stations: Types.KitchenStation[] }>('/kitchen-display/stations'),
  getStation: (id: number) => api.get<Types.KitchenStation>(`/kitchen-display/stations/${id}`),
  createStation: (data: Partial<Types.KitchenStation>) => api.post('/kitchen-display/stations', data),
  updateStation: (id: number, data: Partial<Types.KitchenStation>) => api.put(`/kitchen-display/stations/${id}`, data),
  deleteStation: (id: number) => api.delete(`/kitchen-display/stations/${id}`),

  // Orders
  getOrders: (stationId?: number, status?: Types.OrderStatus) => api.get<{ orders: Types.KitchenOrder[] }>('/kitchen-display/orders', { params: { station_id: stationId, status } }),
  getOrder: (id: number) => api.get<Types.KitchenOrder>(`/kitchen-display/orders/${id}`),
  updateOrderStatus: (id: number, status: Types.OrderStatus) => api.put(`/kitchen-display/orders/${id}/status`, { status }),
  startOrder: (id: number) => api.put(`/kitchen-display/orders/${id}/start`),
  completeOrder: (id: number) => api.put(`/kitchen-display/orders/${id}/complete`),
}

// ===================================
// EMPLOYEE TIME TRACKING API
// ===================================

export const employeeTimeApi = {
  // Time Entries
  getTimeEntries: (employeeId?: number, date?: string) => api.get<{ entries: Types.TimeEntry[] }>('/employee-time/entries', { params: { employee_id: employeeId, date } }),
  clockIn: (employeeId: number, location?: string) => api.post('/employee-time/clock-in', { employee_id: employeeId, location }),
  clockOut: (employeeId: number) => api.post('/employee-time/clock-out', { employee_id: employeeId }),
  startBreak: (employeeId: number) => api.post('/employee-time/break-start', { employee_id: employeeId }),
  endBreak: (employeeId: number) => api.post('/employee-time/break-end', { employee_id: employeeId }),

  // Time Sheets
  getTimeSheets: (employeeId?: number, startDate?: string, endDate?: string) => api.get<{ timesheets: Types.TimeSheet[] }>('/employee-time/timesheets', { params: { employee_id: employeeId, start_date: startDate, end_date: endDate } }),
  getTimeSheet: (id: number) => api.get<Types.TimeSheet>(`/employee-time/timesheets/${id}`),

  // Shifts
  getShifts: (employeeId?: number, date?: string) => api.get<{ shifts: Types.Shift[] }>('/employee-time/shifts', { params: { employee_id: employeeId, date } }),
  getShift: (id: number) => api.get<Types.Shift>(`/employee-time/shifts/${id}`),
  createShift: (data: Partial<Types.Shift>) => api.post('/employee-time/shifts', data),
  updateShift: (id: number, data: Partial<Types.Shift>) => api.put(`/employee-time/shifts/${id}`, data),
  deleteShift: (id: number) => api.delete(`/employee-time/shifts/${id}`),
}

// ===================================
// INVENTORY MANAGEMENT API
// ===================================

export const inventoryApi = {
  // Inventory Items
  getInventoryItems: (params?: Record<string, unknown>) => api.get<{ items: Types.InventoryItem[] }>('/inventory/items', { params }),
  getInventoryItem: (id: number) => api.get<Types.InventoryItem>(`/inventory/items/${id}`),
  updateInventoryItem: (id: number, data: Partial<Types.InventoryItem>) => api.put(`/inventory/items/${id}`, data),

  // Stock Movements
  getStockMovements: (productId?: number) => api.get<{ movements: Types.StockMovement[] }>('/inventory/movements', { params: { product_id: productId } }),
  addStockMovement: (data: Partial<Types.StockMovement>) => api.post('/inventory/movements', data),

  // Suppliers
  getSuppliers: () => api.get<{ suppliers: Types.Supplier[] }>('/inventory/suppliers'),
  getSupplier: (id: number) => api.get<Types.Supplier>(`/inventory/suppliers/${id}`),
  createSupplier: (data: Partial<Types.Supplier>) => api.post('/inventory/suppliers', data),
  updateSupplier: (id: number, data: Partial<Types.Supplier>) => api.put(`/inventory/suppliers/${id}`, data),
  deleteSupplier: (id: number) => api.delete(`/inventory/suppliers/${id}`),

  // Purchase Orders
  getPurchaseOrders: (status?: Types.PurchaseOrderStatus) => api.get<{ orders: Types.PurchaseOrder[] }>('/inventory/purchase-orders', { params: { status } }),
  getPurchaseOrder: (id: number) => api.get<Types.PurchaseOrder>(`/inventory/purchase-orders/${id}`),
  createPurchaseOrder: (data: Partial<Types.PurchaseOrder>) => api.post('/inventory/purchase-orders', data),
  updatePurchaseOrder: (id: number, data: Partial<Types.PurchaseOrder>) => api.put(`/inventory/purchase-orders/${id}`, data),
  receivePurchaseOrder: (id: number, items: { product_id: number; received_quantity: number }[]) => api.post(`/inventory/purchase-orders/${id}/receive`, { items }),
}

// ===================================
// BAKERY MANAGEMENT API
// ===================================

export const bakeryApi = {
  // Recipes
  getRecipes: (category?: Types.RecipeCategory) => api.get<{ recipes: Types.Recipe[] }>('/bakery/recipes', { params: { category } }),
  getRecipe: (id: number) => api.get<Types.Recipe>(`/bakery/recipes/${id}`),
  createRecipe: (data: Partial<Types.Recipe>) => api.post('/bakery/recipes', data),
  updateRecipe: (id: number, data: Partial<Types.Recipe>) => api.put(`/bakery/recipes/${id}`, data),
  deleteRecipe: (id: number) => api.delete(`/bakery/recipes/${id}`),

  // Production Plans
  getProductionPlans: (date?: string) => api.get<{ plans: Types.ProductionPlan[] }>('/bakery/production-plans', { params: { date } }),
  getProductionPlan: (id: number) => api.get<Types.ProductionPlan>(`/bakery/production-plans/${id}`),
  createProductionPlan: (data: Partial<Types.ProductionPlan>) => api.post('/bakery/production-plans', data),
  updateProductionPlan: (id: number, data: Partial<Types.ProductionPlan>) => api.put(`/bakery/production-plans/${id}`, data),

  // Batches
  getBatches: (status?: Types.BatchStatus, date?: string) => api.get<{ batches: Types.Batch[] }>('/bakery/batches', { params: { status, date } }),
  getBatch: (id: number) => api.get<Types.Batch>(`/bakery/batches/${id}`),
  createBatch: (data: Partial<Types.Batch>) => api.post('/bakery/batches', data),
  updateBatch: (id: number, data: Partial<Types.Batch>) => api.put(`/bakery/batches/${id}`, data),
  updateBatchStatus: (id: number, status: Types.BatchStatus) => api.put(`/bakery/batches/${id}/status`, { status }),
}

// ===================================
// DELIVERY MANAGEMENT API
// ===================================

export const deliveryApi = {
  // Delivery Orders
  getDeliveryOrders: (status?: Types.DeliveryStatus, driverId?: number) => api.get<{ orders: Types.DeliveryOrder[] }>('/delivery/orders', { params: { status, driver_id: driverId } }),
  getDeliveryOrder: (id: number) => api.get<Types.DeliveryOrder>(`/delivery/orders/${id}`),
  createDeliveryOrder: (data: Partial<Types.DeliveryOrder>) => api.post('/delivery/orders', data),
  updateDeliveryOrder: (id: number, data: Partial<Types.DeliveryOrder>) => api.put(`/delivery/orders/${id}`, data),
  assignDriver: (orderId: number, driverId: number) => api.post(`/delivery/orders/${orderId}/assign`, { driver_id: driverId }),
  updateDeliveryStatus: (orderId: number, status: Types.DeliveryStatus) => api.put(`/delivery/orders/${orderId}/status`, { status }),

  // Drivers
  getDrivers: (status?: Types.DriverStatus) => api.get<{ drivers: Types.Driver[] }>('/delivery/drivers', { params: { status } }),
  getDriver: (id: number) => api.get<Types.Driver>(`/delivery/drivers/${id}`),
  createDriver: (data: Partial<Types.Driver>) => api.post('/delivery/drivers', data),
  updateDriver: (id: number, data: Partial<Types.Driver>) => api.put(`/delivery/drivers/${id}`, data),
  updateDriverStatus: (id: number, status: Types.DriverStatus) => api.put(`/delivery/drivers/${id}/status`, { status }),
}

// ===================================
// LOYALTY PROGRAM API
// ===================================

export const loyaltyApi = {
  // Customers
  getCustomers: (tier?: Types.LoyaltyTier) => api.get<{ customers: Types.LoyaltyCustomer[] }>('/loyalty/customers', { params: { tier } }),
  getCustomer: (id: number) => api.get<Types.LoyaltyCustomer>(`/loyalty/customers/${id}`),
  getCustomerByQR: (qrCode: string) => api.get<Types.LoyaltyCustomer>(`/loyalty/customers/qr/${qrCode}`),
  enrollCustomer: (customerId: number) => api.post('/loyalty/customers/enroll', { customer_id: customerId }),

  // Points
  getPointTransactions: (customerId: number) => api.get<{ transactions: Types.PointTransaction[] }>(`/loyalty/customers/${customerId}/points`),
  addPoints: (customerId: number, points: number, reason?: string) => api.post(`/loyalty/customers/${customerId}/points/add`, { points, reason }),
  redeemPoints: (customerId: number, points: number, reason?: string) => api.post(`/loyalty/customers/${customerId}/points/redeem`, { points, reason }),

  // Rewards
  getRewards: (tier?: Types.LoyaltyTier) => api.get<{ rewards: Types.Reward[] }>('/loyalty/rewards', { params: { tier } }),
  getReward: (id: number) => api.get<Types.Reward>(`/loyalty/rewards/${id}`),
  createReward: (data: Partial<Types.Reward>) => api.post('/loyalty/rewards', data),
  updateReward: (id: number, data: Partial<Types.Reward>) => api.put(`/loyalty/rewards/${id}`, data),
  deleteReward: (id: number) => api.delete(`/loyalty/rewards/${id}`),

  // Redemptions
  getRedemptions: (customerId?: number) => api.get<{ redemptions: Types.RewardRedemption[] }>('/loyalty/redemptions', { params: { customer_id: customerId } }),
  redeemReward: (customerId: number, rewardId: number) => api.post('/loyalty/redemptions', { customer_id: customerId, reward_id: rewardId }),
  useRedemption: (redemptionId: number) => api.post(`/loyalty/redemptions/${redemptionId}/use`),
}

// ===================================
// ADVANCED ANALYTICS API
// ===================================

export const analyticsApi = {
  // Dashboards
  getDashboards: () => api.get<{ dashboards: Types.Dashboard[] }>('/analytics/dashboards'),
  getDashboard: (id: number) => api.get<Types.Dashboard>(`/analytics/dashboards/${id}`),
  createDashboard: (data: Partial<Types.Dashboard>) => api.post('/analytics/dashboards', data),
  updateDashboard: (id: number, data: Partial<Types.Dashboard>) => api.put(`/analytics/dashboards/${id}`, data),
  deleteDashboard: (id: number) => api.delete(`/analytics/dashboards/${id}`),

  // Reports
  getReports: () => api.get<{ reports: Types.Report[] }>('/analytics/reports'),
  getReport: (id: number) => api.get<Types.Report>(`/analytics/reports/${id}`),
  createReport: (data: Partial<Types.Report>) => api.post('/analytics/reports', data),
  runReport: (id: number, filters?: Record<string, unknown>) => api.post(`/analytics/reports/${id}/run`, { filters }),
  exportReport: (id: number, format: 'csv' | 'xlsx' | 'pdf') => api.get(`/analytics/reports/${id}/export`, { params: { format }, responseType: 'blob' }),

  // KPIs
  getKPIs: (dateRange?: Types.DateRange) => api.get<{ kpis: Types.KPIMetric[] }>('/analytics/kpis', { params: { date_range: dateRange } }),

  // Forecasting
  getForecast: (metric: string, days: number) => api.get<{ forecast: Types.ForecastData[] }>('/analytics/forecast', { params: { metric, days } }),
}
