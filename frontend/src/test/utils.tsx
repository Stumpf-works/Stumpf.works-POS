/**
 * Test Utilities
 * Helper functions for testing React components
 */
/* eslint-disable react-refresh/only-export-components */

import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create a test query client
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

// Custom render function with providers
interface AllTheProvidersProps {
  children: React.ReactNode
}

function AllTheProviders({ children }: AllTheProvidersProps) {
  const queryClient = createTestQueryClient()

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  )
}

export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllTheProviders, ...options })
}

// Mock data generators
export const mockProduct = {
  id: 1,
  name: 'Test Product',
  description: 'A test product',
  sku: 'TEST-001',
  barcode: '1234567890123',
  price: 9.99,
  vat_rate: 19.0,
  category_id: 1,
  category_name: 'Test Category',
  stock_quantity: 100,
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

export const mockCategory = {
  id: 1,
  name: 'Test Category',
  description: 'A test category',
  color: '#FF5733',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

export const mockTransaction = {
  id: 1,
  receipt_number: 'R-2024-001',
  subtotal: 8.40,
  vat_amount: 1.60,
  total: 10.00,
  payment_method: 'cash',
  amount_paid: 10.00,
  change_amount: 0.00,
  status: 'completed',
  is_tse_signed: true,
  tse_transaction_id: '123',
  tse_signature: 'test_signature',
  completed_at: '2024-01-01T12:00:00Z',
  items: [
    {
      id: 1,
      product_id: 1,
      product_name: 'Test Product',
      product_sku: 'TEST-001',
      quantity: 1,
      unit_price: 9.99,
      vat_rate: 19.0,
      vat_amount: 1.60,
      total: 10.00,
    },
  ],
}

export const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  role: 'cashier',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
}

export const mockAdminUser = {
  ...mockUser,
  role: 'admin',
  username: 'admin',
  email: 'admin@example.com',
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { renderWithProviders as render }
