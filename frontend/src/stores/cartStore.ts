import { create } from 'zustand'
import { Product, CartItem } from '@/types'

interface CartState {
  items: CartItem[]

  // Actions
  addItem: (product: Product, quantity?: number) => void
  removeItem: (productId: number) => void
  updateQuantity: (productId: number, quantity: number) => void
  clearCart: () => void

  // Computed values
  getTotalItems: () => number
  getSubtotal: () => number
  getTaxAmount: () => number
  getTotal: () => number
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],

  addItem: (product, quantity = 1) => {
    const { items } = get()
    const existingItem = items.find((item) => item.product.id === product.id)

    if (existingItem) {
      // Update quantity
      set({
        items: items.map((item) =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        ),
      })
    } else {
      // Add new item
      set({
        items: [...items, { product, quantity }],
      })
    }
  },

  removeItem: (productId) => {
    set({
      items: get().items.filter((item) => item.product.id !== productId),
    })
  },

  updateQuantity: (productId, quantity) => {
    if (quantity <= 0) {
      get().removeItem(productId)
      return
    }

    set({
      items: get().items.map((item) =>
        item.product.id === productId ? { ...item, quantity } : item
      ),
    })
  },

  clearCart: () => {
    set({ items: [] })
  },

  getTotalItems: () => {
    return get().items.reduce((total, item) => total + item.quantity, 0)
  },

  getSubtotal: () => {
    return get().items.reduce(
      (total, item) => total + item.product.price * item.quantity,
      0
    )
  },

  getTaxAmount: () => {
    return get().items.reduce((total, item) => {
      const vatRate = parseFloat(item.product.vat_rate)
      const itemTotal = item.product.price * item.quantity
      const netAmount = itemTotal / (1 + vatRate)
      const taxAmount = itemTotal - netAmount
      return total + taxAmount
    }, 0)
  },

  getTotal: () => {
    return get().getSubtotal()
  },
}))
