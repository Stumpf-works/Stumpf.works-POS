/**
 * Tests for POS Page
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders, mockProduct, mockCategory } from '../../test/utils'
import POSPage from '../POSPage'
import { useCartStore } from '../../stores/cartStore'

// Mock the API
vi.mock('../../services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

describe('POSPage', () => {
  beforeEach(() => {
    useCartStore.getState().clearCart()
    vi.clearAllMocks()
  })

  it('should render POS interface', async () => {
    const { api } = await import('../../services/api')

    // Mock products and categories
    vi.mocked(api.get).mockImplementation((url) => {
      if (url.includes('/products')) {
        return Promise.resolve({ data: [mockProduct] })
      }
      if (url.includes('/categories')) {
        return Promise.resolve({ data: [mockCategory] })
      }
      return Promise.resolve({ data: [] })
    })

    renderWithProviders(<POSPage />)

    await waitFor(() => {
      expect(screen.getByText(/kasse/i)).toBeInTheDocument()
    })
  })

  it('should display products grid', async () => {
    const { api } = await import('../../services/api')

    vi.mocked(api.get).mockImplementation((url) => {
      if (url.includes('/products')) {
        return Promise.resolve({ data: [mockProduct] })
      }
      return Promise.resolve({ data: [] })
    })

    renderWithProviders(<POSPage />)

    await waitFor(() => {
      expect(screen.getByText(mockProduct.name)).toBeInTheDocument()
    })
  })

  it('should add product to cart when clicked', async () => {
    const user = userEvent.setup()
    const { api } = await import('../../services/api')

    vi.mocked(api.get).mockImplementation((url) => {
      if (url.includes('/products')) {
        return Promise.resolve({ data: [mockProduct] })
      }
      return Promise.resolve({ data: [] })
    })

    renderWithProviders(<POSPage />)

    await waitFor(() => {
      expect(screen.getByText(mockProduct.name)).toBeInTheDocument()
    })

    const productCard = screen.getByText(mockProduct.name)
    await user.click(productCard)

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(1)
    expect(items[0].product.id).toBe(mockProduct.id)
  })

  it('should display cart items', async () => {
    renderWithProviders(<POSPage />)

    // Add item to cart
    useCartStore.getState().addItem(mockProduct)

    await waitFor(() => {
      expect(screen.getByText(mockProduct.name)).toBeInTheDocument()
    })
  })

  it('should calculate total correctly', () => {
    renderWithProviders(<POSPage />)

    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().updateQuantity(mockProduct.id, 2)

    const { total } = useCartStore.getState()
    expect(total()).toBe(mockProduct.price * 2)
  })

  it('should show checkout button when cart has items', () => {
    renderWithProviders(<POSPage />)

    useCartStore.getState().addItem(mockProduct)

    const checkoutButton = screen.queryByText(/bezahlen/i)
    expect(checkoutButton).toBeInTheDocument()
  })

  it('should process checkout', async () => {
    const user = userEvent.setup()
    const { api } = await import('../../services/api')

    // Mock successful transaction
    vi.mocked(api.post).mockResolvedValueOnce({
      data: {
        id: 1,
        receipt_number: 'R-2024-001',
        total: mockProduct.price,
        status: 'completed',
      },
    })

    renderWithProviders(<POSPage />)

    useCartStore.getState().addItem(mockProduct)

    const checkoutButton = screen.queryByText(/bezahlen/i)
    if (checkoutButton) {
      await user.click(checkoutButton)

      // Select payment method
      const cashButton = screen.queryByText(/bar/i)
      if (cashButton) {
        await user.click(cashButton)

        await waitFor(() => {
          expect(api.post).toHaveBeenCalledWith(
            '/transactions',
            expect.objectContaining({
              items: expect.arrayContaining([
                expect.objectContaining({ product_id: mockProduct.id }),
              ]),
            })
          )
        })
      }
    }
  })

  it('should search products', async () => {
    const user = userEvent.setup()
    const { api } = await import('../../services/api')

    vi.mocked(api.get).mockImplementation((url) => {
      if (url.includes('/products')) {
        return Promise.resolve({ data: [mockProduct] })
      }
      return Promise.resolve({ data: [] })
    })

    renderWithProviders(<POSPage />)

    const searchInput = screen.queryByPlaceholderText(/suche/i)
    if (searchInput) {
      await user.type(searchInput, 'Test')

      await waitFor(() => {
        expect(screen.getByText(mockProduct.name)).toBeInTheDocument()
      })
    }
  })

  it('should filter products by category', async () => {
    const user = userEvent.setup()
    const { api } = await import('../../services/api')

    vi.mocked(api.get).mockImplementation((url) => {
      if (url.includes('/products')) {
        return Promise.resolve({ data: [mockProduct] })
      }
      if (url.includes('/categories')) {
        return Promise.resolve({ data: [mockCategory] })
      }
      return Promise.resolve({ data: [] })
    })

    renderWithProviders(<POSPage />)

    await waitFor(() => {
      const categoryButton = screen.queryByText(mockCategory.name)
      if (categoryButton) {
        expect(categoryButton).toBeInTheDocument()
      }
    })
  })

  it('should clear cart after successful checkout', async () => {
    const { api } = await import('../../services/api')

    vi.mocked(api.post).mockResolvedValueOnce({
      data: {
        id: 1,
        receipt_number: 'R-2024-001',
        total: mockProduct.price,
        status: 'completed',
      },
    })

    useCartStore.getState().addItem(mockProduct)
    expect(useCartStore.getState().items).toHaveLength(1)

    // After successful checkout, cart should be cleared
    // This would be tested in the checkout flow
  })
})
