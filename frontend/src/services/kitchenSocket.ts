import { io, Socket } from 'socket.io-client'
import { KitchenOrder, OrderStatus } from '@/types/plugins'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

class KitchenSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 2000

  connect(stationId?: number) {
    if (this.socket?.connected) {
      console.log('Kitchen socket already connected')
      return
    }

    this.socket = io(`${WS_URL}/kitchen`, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: this.reconnectDelay,
      reconnectionAttempts: this.maxReconnectAttempts,
      query: stationId ? { station_id: stationId } : undefined,
    })

    this.socket.on('connect', () => {
      console.log('Kitchen socket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', (reason) => {
      console.log('Kitchen socket disconnected:', reason)
    })

    this.socket.on('connect_error', (error) => {
      console.error('Kitchen socket connection error:', error)
      this.reconnectAttempts++
    })

    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  // Listen for new orders
  onNewOrder(callback: (order: KitchenOrder) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('new_order', callback)
  }

  // Listen for order updates
  onOrderUpdate(callback: (order: KitchenOrder) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('order_update', callback)
  }

  // Listen for order status changes
  onOrderStatusChange(callback: (data: { order_id: number; status: OrderStatus }) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('order_status_change', callback)
  }

  // Emit order status update
  updateOrderStatus(orderId: number, status: OrderStatus) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('update_order_status', { order_id: orderId, status })
  }

  // Emit order start
  startOrder(orderId: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('start_order', { order_id: orderId })
  }

  // Emit order complete
  completeOrder(orderId: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('complete_order', { order_id: orderId })
  }

  // Join station room
  joinStation(stationId: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('join_station', { station_id: stationId })
  }

  // Leave station room
  leaveStation(stationId: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('leave_station', { station_id: stationId })
  }

  // Remove all listeners
  removeAllListeners() {
    if (this.socket) {
      this.socket.removeAllListeners()
    }
  }

  // Check if connected
  isConnected(): boolean {
    return this.socket?.connected || false
  }
}

export const kitchenSocket = new KitchenSocketService()
