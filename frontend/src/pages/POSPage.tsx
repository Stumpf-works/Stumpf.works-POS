import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/services/api'
import { useCartStore } from '@/stores/cartStore'
import { Product, PaymentMethod } from '@/types'

export default function POSPage() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)

  const {
    items: cartItems,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    getTotalItems,
    getSubtotal,
    getTaxAmount,
    getTotal,
  } = useCartStore()

  // Fetch products
  const { data: products = [], isLoading: isLoadingProducts } = useQuery({
    queryKey: ['products', searchQuery, selectedCategory],
    queryFn: () =>
      api.products.list({
        q: searchQuery || undefined,
        category_id: selectedCategory || undefined,
        is_available: true,
        is_active: true,
        limit: 50,
      }),
    staleTime: 30000, // 30 seconds
  })

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.categories.list({ is_active: true }),
    staleTime: 60000, // 1 minute
  })

  // Create transaction mutation
  const createTransactionMutation = useMutation({
    mutationFn: (data: any) => api.transactions.create(data),
    onSuccess: (data) => {
      toast.success(`Verkauf erfolgreich! Beleg: ${data.receipt_number}`)
      clearCart()
      // TODO: Print receipt
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Fehler beim Erstellen der Transaktion')
    },
  })

  const handleAddToCart = (product: Product) => {
    // Check stock
    if (product.track_inventory) {
      const cartItem = cartItems.find((item) => item.product.id === product.id)
      const currentQty = cartItem?.quantity || 0

      if (currentQty >= product.stock_quantity) {
        toast.error('Nicht genug Lagerbestand')
        return
      }
    }

    addItem(product)
    toast.success(`${product.name} hinzugefügt`)
  }

  const handleCheckout = (paymentMethod: PaymentMethod) => {
    if (cartItems.length === 0) {
      toast.error('Warenkorb ist leer')
      return
    }

    // Prepare transaction data
    const items = cartItems.map((item) => ({
      product_id: item.product.id,
      quantity: item.quantity,
      discount_amount: 0,
    }))

    const transactionData: any = {
      items,
      payment_method: paymentMethod,
      discount_amount: 0,
    }

    // For cash, prompt for amount given
    if (paymentMethod === PaymentMethod.CASH) {
      const total = getTotal()
      const cashGiven = prompt(
        `Gesamtsumme: €${total.toFixed(2)}\n\nBargeld erhalten:`,
        total.toFixed(2)
      )

      if (!cashGiven) {
        return // User cancelled
      }

      const cashAmount = parseFloat(cashGiven)

      if (isNaN(cashAmount) || cashAmount < total) {
        toast.error('Ungültiger Betrag')
        return
      }

      transactionData.cash_given = cashAmount
    }

    createTransactionMutation.mutate(transactionData)
  }

  const filteredProducts = searchQuery
    ? products.filter(
        (p: Product) =>
          p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.barcode?.includes(searchQuery) ||
          p.sku?.includes(searchQuery)
      )
    : products

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="px-4 py-3 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/')}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Zurück
            </button>
            <h1 className="text-xl font-bold text-gray-900">Kasse</h1>
          </div>
          <div className="text-sm text-gray-600">
            {new Date().toLocaleDateString('de-DE', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Products Panel */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* Search */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Produkt suchen oder Barcode scannen..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
            />
          </div>

          {/* Categories */}
          {categories.length > 0 && (
            <div className="mb-4 flex space-x-2 overflow-x-auto pb-2">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap ${
                  selectedCategory === null
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                Alle
              </button>
              {categories.map((cat: any) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap ${
                    selectedCategory === cat.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                  style={
                    selectedCategory === cat.id && cat.color
                      ? { backgroundColor: cat.color }
                      : {}
                  }
                >
                  {cat.name}
                </button>
              ))}
            </div>
          )}

          {/* Products Grid */}
          {isLoadingProducts ? (
            <div className="text-center py-8 text-gray-500">Lädt Produkte...</div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Keine Produkte gefunden
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filteredProducts.map((product: Product) => (
                <div
                  key={product.id}
                  onClick={() => handleAddToCart(product)}
                  className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer touch-manipulation"
                >
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full aspect-square object-cover rounded-lg mb-3"
                    />
                  ) : (
                    <div className="w-full aspect-square bg-gray-200 rounded-lg mb-3 flex items-center justify-center">
                      <span className="text-4xl">📦</span>
                    </div>
                  )}

                  <h3 className="font-semibold text-gray-900 line-clamp-2">
                    {product.name}
                  </h3>
                  <p className="text-primary-600 font-bold mt-1">
                    € {product.price.toFixed(2)}
                  </p>

                  {product.track_inventory && (
                    <p
                      className={`text-xs mt-1 ${
                        product.stock_quantity <= (product.min_stock_level || 0)
                          ? 'text-red-600'
                          : 'text-gray-500'
                      }`}
                    >
                      Lager: {product.stock_quantity}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Cart Panel */}
        <div className="w-96 bg-white shadow-lg flex flex-col">
          {/* Cart Items */}
          <div className="flex-1 overflow-y-auto p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-4">
              Warenkorb ({getTotalItems()})
            </h2>

            {cartItems.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <p>Warenkorb ist leer</p>
                <p className="text-sm mt-2">Fügen Sie Produkte hinzu</p>
              </div>
            ) : (
              <div className="space-y-2">
                {cartItems.map((item) => (
                  <div
                    key={item.product.id}
                    className="bg-gray-50 p-3 rounded-lg flex items-start justify-between"
                  >
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">
                        {item.product.name}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        € {item.product.price.toFixed(2)} × {item.quantity} = €{' '}
                        {(item.product.price * item.quantity).toFixed(2)}
                      </p>

                      {/* Quantity Controls */}
                      <div className="flex items-center space-x-2 mt-2">
                        <button
                          onClick={() =>
                            updateQuantity(item.product.id, item.quantity - 1)
                          }
                          className="w-8 h-8 rounded bg-gray-200 hover:bg-gray-300 flex items-center justify-center"
                        >
                          -
                        </button>
                        <span className="w-8 text-center font-medium">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() =>
                            updateQuantity(item.product.id, item.quantity + 1)
                          }
                          className="w-8 h-8 rounded bg-gray-200 hover:bg-gray-300 flex items-center justify-center"
                        >
                          +
                        </button>
                      </div>
                    </div>

                    <button
                      onClick={() => removeItem(item.product.id)}
                      className="text-red-600 hover:text-red-700 ml-2"
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Cart Summary */}
          <div className="border-t border-gray-200 p-4 space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Zwischensumme</span>
              <span className="font-semibold">€ {getSubtotal().toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">MwSt.</span>
              <span className="font-semibold">€ {getTaxAmount().toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-lg font-bold border-t border-gray-200 pt-3">
              <span>Gesamt</span>
              <span className="text-primary-600">€ {getTotal().toFixed(2)}</span>
            </div>

            {/* Payment Buttons */}
            <div className="space-y-2 pt-2">
              <button
                disabled={cartItems.length === 0 || createTransactionMutation.isPending}
                onClick={() => handleCheckout(PaymentMethod.CARD)}
                className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {createTransactionMutation.isPending
                  ? 'Verarbeite...'
                  : 'Kartenzahlung'}
              </button>
              <button
                disabled={cartItems.length === 0 || createTransactionMutation.isPending}
                onClick={() => handleCheckout(PaymentMethod.CASH)}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Barzahlung
              </button>
              {cartItems.length > 0 && (
                <button
                  onClick={clearCart}
                  className="w-full bg-gray-200 text-gray-700 py-2 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                >
                  Warenkorb leeren
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
