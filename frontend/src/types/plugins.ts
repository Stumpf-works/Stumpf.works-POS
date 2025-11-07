// ===================================
// PLUGIN TYPES & INTERFACES
// ===================================

// Base Plugin Interface
export interface Plugin {
  id: number
  plugin_name: string
  display_name: string
  description: string
  version: string
  is_active: boolean
  category: string
  icon?: string
}

// ===================================
// PAYMENT GATEWAY PLUGIN
// ===================================

export type PaymentProviderType = 'stripe' | 'paypal' | 'square' | 'sumup'
export type PaymentStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'refunded' | 'partially_refunded'
export type TerminalConnectionStatus = 'connected' | 'disconnected' | 'error'

export interface PaymentProvider {
  id: number
  provider_name: string
  provider_type: PaymentProviderType
  is_active: boolean
  is_test_mode: boolean
  is_default: boolean
  health_status: 'healthy' | 'degraded' | 'unhealthy'
  transaction_fee_percentage: number
  transaction_fee_fixed: number
  created_at: string
  updated_at: string
}

export interface PaymentTerminal {
  id: number
  terminal_id: string
  provider_id: number
  location_name: string
  is_online: boolean
  connection_status: TerminalConnectionStatus
  last_seen_at?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface PaymentTransaction {
  id: number
  transaction_id: string
  provider_id: number
  provider_name: string
  terminal_id?: number
  amount: number
  currency: string
  status: PaymentStatus
  payment_method: string
  customer_email?: string
  metadata?: Record<string, any>
  error_message?: string
  created_at: string
  updated_at: string
}

// ===================================
// CASH MANAGEMENT PLUGIN
// ===================================

export type CashRegisterStatus = 'open' | 'closed'
export type CashDenomination = 'bills' | 'coins'

export interface CashRegister {
  id: number
  register_name: string
  register_number: string
  location: string
  status: CashRegisterStatus
  current_session_id?: number
  created_at: string
  updated_at: string
}

export interface CashSession {
  id: number
  register_id: number
  opened_by_user_id: number
  opened_by_user_name: string
  opened_at: string
  closed_at?: string
  closed_by_user_id?: number
  closed_by_user_name?: string
  opening_balance: number
  closing_balance?: number
  expected_balance?: number
  variance?: number
  notes?: string
  z_report_generated: boolean
}

export interface CashCount {
  denomination_type: CashDenomination
  denomination_value: number
  count: number
  total: number
}

export interface CashMovement {
  id: number
  session_id: number
  movement_type: 'in' | 'out' | 'correction'
  amount: number
  reason: string
  performed_by_user_id: number
  performed_by_user_name: string
  created_at: string
}

// ===================================
// TABLE MANAGEMENT PLUGIN
// ===================================

export type TableStatus = 'available' | 'occupied' | 'reserved' | 'dirty'
export type TableShape = 'square' | 'circle' | 'rectangle'
export type ReservationStatus = 'pending' | 'confirmed' | 'seated' | 'cancelled' | 'no_show'

export interface Floor {
  id: number
  floor_name: string
  floor_number: number
  width: number
  height: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Table {
  id: number
  table_number: string
  capacity: number
  shape: TableShape
  x_position: number
  y_position: number
  width: number
  height: number
  status: TableStatus
  floor_id: number
  floor_name?: string
  current_reservation_id?: number
  created_at: string
  updated_at: string
}

export interface Reservation {
  id: number
  customer_name: string
  customer_phone: string
  customer_email?: string
  guest_count: number
  reservation_date: string
  reservation_time: string
  duration_minutes: number
  table_id?: number
  table_number?: string
  status: ReservationStatus
  notes?: string
  created_at: string
  updated_at: string
}

// ===================================
// KITCHEN DISPLAY PLUGIN
// ===================================

export type OrderStatus = 'new' | 'preparing' | 'ready' | 'served'
export type OrderPriority = 'normal' | 'high' | 'urgent'

export interface KitchenStation {
  id: number
  station_name: string
  station_code: string
  description?: string
  display_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface KitchenOrder {
  id: number
  order_id: number
  order_number: string
  table_number?: string
  customer_name?: string
  station_id: number
  station_name: string
  items: KitchenOrderItem[]
  status: OrderStatus
  priority: OrderPriority
  estimated_time_minutes: number
  started_at?: string
  completed_at?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface KitchenOrderItem {
  id: number
  product_name: string
  quantity: number
  notes?: string
  modifiers?: string[]
}

// ===================================
// EMPLOYEE TIME TRACKING PLUGIN
// ===================================

export type TimeEntryType = 'clock_in' | 'clock_out' | 'break_start' | 'break_end'

export interface TimeEntry {
  id: number
  employee_id: number
  employee_name: string
  entry_type: TimeEntryType
  timestamp: string
  location?: string
  notes?: string
  created_at: string
}

export interface TimeSheet {
  id: number
  employee_id: number
  employee_name: string
  date: string
  clock_in?: string
  clock_out?: string
  total_hours: number
  break_hours: number
  regular_hours: number
  overtime_hours: number
  status: 'active' | 'completed'
  notes?: string
}

export interface Shift {
  id: number
  employee_id: number
  employee_name: string
  shift_date: string
  start_time: string
  end_time: string
  position?: string
  notes?: string
  is_confirmed: boolean
  created_at: string
  updated_at: string
}

// ===================================
// INVENTORY MANAGEMENT PLUGIN
// ===================================

export type StockMovementType = 'purchase' | 'sale' | 'adjustment' | 'transfer' | 'waste'
export type PurchaseOrderStatus = 'draft' | 'sent' | 'partial' | 'received' | 'cancelled'

export interface InventoryItem {
  id: number
  product_id: number
  product_name: string
  sku: string
  current_stock: number
  unit_of_measure: string
  reorder_level: number
  reorder_quantity: number
  unit_cost: number
  last_ordered_at?: string
  supplier_id?: number
  supplier_name?: string
  location?: string
  created_at: string
  updated_at: string
}

export interface StockMovement {
  id: number
  product_id: number
  product_name: string
  movement_type: StockMovementType
  quantity: number
  from_location?: string
  to_location?: string
  reference_id?: string
  notes?: string
  performed_by_user_id: number
  performed_by_user_name: string
  created_at: string
}

export interface Supplier {
  id: number
  supplier_name: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
  payment_terms?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PurchaseOrder {
  id: number
  po_number: string
  supplier_id: number
  supplier_name: string
  order_date: string
  expected_delivery_date?: string
  status: PurchaseOrderStatus
  total_amount: number
  items: PurchaseOrderItem[]
  notes?: string
  created_at: string
  updated_at: string
}

export interface PurchaseOrderItem {
  id: number
  product_id: number
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
  received_quantity?: number
}

// ===================================
// BAKERY MANAGEMENT PLUGIN
// ===================================

export type RecipeCategory = 'bread' | 'rolls' | 'cake' | 'pastry' | 'other'
export type BatchStatus = 'planned' | 'in_production' | 'baking' | 'cooling' | 'completed'

export interface Recipe {
  id: number
  recipe_name: string
  category: RecipeCategory
  batch_size: number
  unit_of_measure: string
  baking_time: number
  baking_temperature: number
  resting_time?: number
  shelf_life_hours: number
  ingredients: RecipeIngredient[]
  instructions?: string
  created_at: string
  updated_at: string
}

export interface RecipeIngredient {
  id: number
  ingredient_name: string
  quantity: number
  unit_of_measure: string
}

export interface ProductionPlan {
  id: number
  plan_date: string
  shift: 'morning' | 'afternoon' | 'night'
  items: ProductionPlanItem[]
  notes?: string
  created_at: string
  updated_at: string
}

export interface ProductionPlanItem {
  id: number
  recipe_id: number
  recipe_name: string
  quantity: number
  batch_number?: string
}

export interface Batch {
  id: number
  batch_number: string
  recipe_id: number
  recipe_name: string
  production_date: string
  production_time: string
  quantity_planned: number
  quantity_produced?: number
  status: BatchStatus
  produced_by_user_id?: number
  produced_by_user_name?: string
  expiry_date?: string
  qr_code?: string
  notes?: string
  created_at: string
  updated_at: string
}

// ===================================
// DELIVERY MANAGEMENT PLUGIN
// ===================================

export type DeliveryStatus = 'pending' | 'assigned' | 'picked_up' | 'in_transit' | 'delivered' | 'cancelled'
export type DriverStatus = 'available' | 'busy' | 'offline'

export interface DeliveryOrder {
  id: number
  order_id: number
  order_number: string
  customer_name: string
  customer_phone: string
  delivery_address: string
  delivery_latitude?: number
  delivery_longitude?: number
  driver_id?: number
  driver_name?: string
  status: DeliveryStatus
  assigned_at?: string
  picked_up_at?: string
  delivered_at?: string
  estimated_delivery_time?: string
  actual_delivery_time?: string
  delivery_fee: number
  distance_km?: number
  notes?: string
  created_at: string
  updated_at: string
}

export interface Driver {
  id: number
  user_id: number
  driver_name: string
  phone: string
  vehicle_type: string
  vehicle_number?: string
  status: DriverStatus
  current_latitude?: number
  current_longitude?: number
  last_location_update?: string
  active_delivery_id?: number
  total_deliveries: number
  rating?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// ===================================
// LOYALTY PROGRAM PLUGIN
// ===================================

export type LoyaltyTier = 'bronze' | 'silver' | 'gold' | 'platinum'
export type RewardType = 'discount_percentage' | 'discount_fixed' | 'free_product' | 'points_multiplier'
export type RedemptionStatus = 'pending' | 'approved' | 'rejected' | 'used'

export interface LoyaltyCustomer {
  id: number
  customer_id: number
  customer_name: string
  customer_email?: string
  customer_phone?: string
  member_number: string
  qr_code: string
  tier: LoyaltyTier
  total_points: number
  points_earned: number
  points_redeemed: number
  tier_progress_percentage: number
  next_tier?: LoyaltyTier
  points_to_next_tier?: number
  joined_at: string
  last_transaction_at?: string
}

export interface PointTransaction {
  id: number
  customer_id: number
  transaction_id?: number
  points: number
  transaction_type: 'earned' | 'redeemed' | 'expired' | 'adjusted'
  reason?: string
  created_at: string
}

export interface Reward {
  id: number
  reward_name: string
  description?: string
  reward_type: RewardType
  reward_value: number
  points_required: number
  tier_requirement?: LoyaltyTier
  is_active: boolean
  valid_from?: string
  valid_until?: string
  max_redemptions?: number
  created_at: string
  updated_at: string
}

export interface RewardRedemption {
  id: number
  customer_id: number
  customer_name: string
  reward_id: number
  reward_name: string
  points_used: number
  status: RedemptionStatus
  redeemed_at: string
  used_at?: string
  transaction_id?: number
}

// ===================================
// ADVANCED ANALYTICS PLUGIN
// ===================================

export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'scatter'
export type DateRange = 'today' | 'yesterday' | 'last_7_days' | 'last_30_days' | 'this_month' | 'last_month' | 'custom'

export interface Dashboard {
  id: number
  dashboard_name: string
  description?: string
  widgets: DashboardWidget[]
  is_default: boolean
  created_by_user_id: number
  created_at: string
  updated_at: string
}

export interface DashboardWidget {
  id: number
  widget_type: 'kpi' | 'chart' | 'table' | 'text'
  widget_title: string
  chart_type?: ChartType
  data_source: string
  config: Record<string, any>
  position_x: number
  position_y: number
  width: number
  height: number
}

export interface Report {
  id: number
  report_name: string
  report_type: 'sales' | 'inventory' | 'employee' | 'customer' | 'financial' | 'custom'
  description?: string
  filters: Record<string, any>
  columns: ReportColumn[]
  created_by_user_id: number
  created_at: string
  updated_at: string
}

export interface ReportColumn {
  field: string
  label: string
  type: 'string' | 'number' | 'date' | 'currency'
  aggregation?: 'sum' | 'avg' | 'count' | 'min' | 'max'
}

export interface KPIMetric {
  metric_name: string
  metric_value: number
  metric_unit?: string
  previous_value?: number
  change_percentage?: number
  trend: 'up' | 'down' | 'neutral'
}

export interface ForecastData {
  date: string
  predicted_value: number
  confidence_lower: number
  confidence_upper: number
  actual_value?: number
}
