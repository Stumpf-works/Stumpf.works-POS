// User types
export interface User {
  id: number
  email: string
  username: string
  first_name?: string
  last_name?: string
  role: UserRole
  tenant_id: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
}

export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  TENANT_ADMIN = 'tenant_admin',
  MANAGER = 'manager',
  CASHIER = 'cashier',
  VIEWER = 'viewer',
}

// Auth types
export interface LoginCredentials {
  username_or_email: string
  password: string
}

export interface PINLoginCredentials {
  pin_code: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// Product types
export interface Product {
  id: number
  name: string
  sku?: string
  barcode?: string
  description?: string
  category_id?: number
  price: number
  cost?: number
  vat_rate: VATRate
  track_inventory: boolean
  stock_quantity: number
  min_stock_level?: number
  is_active: boolean
  is_available: boolean
  image_url?: string
  tenant_id: string
  created_at: string
  updated_at: string
}

export interface ProductCategory {
  id: number
  name: string
  slug: string
  description?: string
  parent_id?: number
  color?: string
  sort_order: number
  is_active: boolean
  tenant_id: string
}

export enum VATRate {
  STANDARD = '0.19',
  REDUCED = '0.07',
  ZERO = '0.00',
}

// Transaction types
export interface Transaction {
  id: number
  receipt_number: string
  user_id: number
  status: TransactionStatus
  subtotal: number
  tax_amount: number
  total: number
  discount_amount: number
  payment_method: PaymentMethod
  payment_reference?: string
  cash_given?: number
  cash_change?: number
  tse_transaction_id?: string
  tse_signature?: string
  is_tse_signed: boolean
  notes?: string
  customer_name?: string
  customer_email?: string
  completed_at?: string
  items: TransactionItem[]
  tenant_id: string
  created_at: string
  updated_at: string
}

export interface TransactionItem {
  id: number
  transaction_id: number
  product_id: number
  product_name: string
  product_sku?: string
  quantity: number
  unit_price: number
  vat_rate: number
  subtotal: number
  tax_amount: number
  total: number
  discount_amount: number
}

export enum TransactionStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded',
}

export enum PaymentMethod {
  CASH = 'cash',
  CARD = 'card',
  SUMUP = 'sumup',
  BANK_TRANSFER = 'bank_transfer',
  OTHER = 'other',
}

// Cart types (for POS)
export interface CartItem {
  product: Product
  quantity: number
}

// API Response types
export interface ApiError {
  detail: string
  code?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
