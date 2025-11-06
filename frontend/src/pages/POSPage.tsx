import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function POSPage() {
  const navigate = useNavigate()
  const [cart, setCart] = useState<any[]>([])

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
          <div className="mb-4">
            <input
              type="text"
              placeholder="Produkt suchen oder Barcode scannen..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {/* Placeholder products */}
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div
                key={i}
                className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer touch-manipulation"
              >
                <div className="aspect-square bg-gray-200 rounded-lg mb-3"></div>
                <h3 className="font-semibold text-gray-900">Produkt {i}</h3>
                <p className="text-primary-600 font-bold mt-1">€ 9,99</p>
              </div>
            ))}
          </div>
        </div>

        {/* Cart Panel */}
        <div className="w-96 bg-white shadow-lg flex flex-col">
          {/* Cart Items */}
          <div className="flex-1 overflow-y-auto p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Warenkorb</h2>

            {cart.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <p>Warenkorb ist leer</p>
                <p className="text-sm mt-2">Fügen Sie Produkte hinzu</p>
              </div>
            ) : (
              <div className="space-y-2">
                {/* Cart items will go here */}
              </div>
            )}
          </div>

          {/* Cart Summary */}
          <div className="border-t border-gray-200 p-4 space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Zwischensumme</span>
              <span className="font-semibold">€ 0,00</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">MwSt. (19%)</span>
              <span className="font-semibold">€ 0,00</span>
            </div>
            <div className="flex justify-between text-lg font-bold border-t border-gray-200 pt-3">
              <span>Gesamt</span>
              <span className="text-primary-600">€ 0,00</span>
            </div>

            {/* Payment Buttons */}
            <div className="space-y-2 pt-2">
              <button
                disabled={cart.length === 0}
                className="w-full bg-primary-600 text-white py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Kartenzahlung
              </button>
              <button
                disabled={cart.length === 0}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Barzahlung
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
