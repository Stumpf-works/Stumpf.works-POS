/**
 * Tests for Cart Store
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useCartStore } from '../cartStore'

describe('CartStore', () => {
  beforeEach(() => {
    // Reset cart before each test
    useCartStore.getState().clearCart()
  })

  const mockProduct = {
    id: 1,
    name: 'Test Product',
    price: 10.00,
    vat_rate: 19.0,
    stock_quantity: 100,
  }

  it('should initialize with empty cart', () => {
    const { items } = useCartStore.getState()
    expect(items).toEqual([])
  })

  it('should add item to cart', () => {
    useCartStore.getState().addItem(mockProduct)

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(1)
    expect(items[0].product.id).toBe(mockProduct.id)
    expect(items[0].quantity).toBe(1)
  })

  it('should increase quantity when adding existing item', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().addItem(mockProduct)

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(1)
    expect(items[0].quantity).toBe(2)
  })

  it('should remove item from cart', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().removeItem(mockProduct.id)

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(0)
  })

  it('should update item quantity', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().updateQuantity(mockProduct.id, 5)

    const { items } = useCartStore.getState()
    expect(items[0].quantity).toBe(5)
  })

  it('should remove item when quantity is set to 0', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().updateQuantity(mockProduct.id, 0)

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(0)
  })

  it('should calculate subtotal correctly', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().updateQuantity(mockProduct.id, 2)

    const { getSubtotal } = useCartStore.getState()
    expect(getSubtotal()).toBe(20.00)
  })

  it('should calculate VAT correctly', () => {
    const { addItem, updateQuantity, getTaxAmount } = useCartStore.getState()

    addItem(mockProduct)
    updateQuantity(mockProduct.id, 1)

    // VAT = 10.00 * 0.19 = 1.90
    const expectedVat = 10.00 * (19.0 / 100)
    expect(Math.abs(getTaxAmount() - expectedVat)).toBeLessThan(0.01)
  })

  it('should calculate total correctly', () => {
    const { addItem, updateQuantity, getTotal } = useCartStore.getState()

    addItem(mockProduct)
    updateQuantity(mockProduct.id, 1)

    // Total = price (already includes VAT in our model)
    expect(getTotal()).toBe(10.00)
  })

  it('should clear cart', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().addItem({ ...mockProduct, id: 2 })
    useCartStore.getState().clearCart()

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(0)
  })

  it('should handle multiple different products', () => {
    const product1 = mockProduct
    const product2 = { ...mockProduct, id: 2, name: 'Product 2', price: 15.00 }

    useCartStore.getState().addItem(product1)
    useCartStore.getState().addItem(product2)

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(2)
  })

  it('should calculate total item count correctly', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().updateQuantity(mockProduct.id, 3)
    useCartStore.getState().addItem({ ...mockProduct, id: 2 })
    useCartStore.getState().updateQuantity(2, 2)

    const { items } = useCartStore.getState()
    const totalCount = items.reduce((sum, item) => sum + item.quantity, 0)
    expect(totalCount).toBe(5)
  })

  it('should not add item with negative quantity', () => {
    useCartStore.getState().addItem(mockProduct)
    useCartStore.getState().updateQuantity(mockProduct.id, -1)

    const { items } = useCartStore.getState()
    // Should either remove or set to 0
    expect(items.length === 0 || items[0].quantity === 0).toBe(true)
  })

  it('should handle items with different VAT rates', () => {
    const product1 = { ...mockProduct, vat_rate: 19.0 }
    const product2 = { ...mockProduct, id: 2, vat_rate: 7.0, price: 20.00 }

    useCartStore.getState().addItem(product1)
    useCartStore.getState().addItem(product2)

    const { items } = useCartStore.getState()
    expect(items).toHaveLength(2)
    expect(items[0].product.vat_rate).toBe(19.0)
    expect(items[1].product.vat_rate).toBe(7.0)
  })
})
