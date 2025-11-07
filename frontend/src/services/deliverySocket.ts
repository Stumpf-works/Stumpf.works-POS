import { io, Socket } from 'socket.io-client'
import { DeliveryOrder, DeliveryStatus, Driver } from '@/types/plugins'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

interface DriverLocation {
  driver_id: number
  latitude: number
  longitude: number
  timestamp: string
}

class DeliverySocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 2000

  connect(driverId?: number) {
    if (this.socket?.connected) {
      console.log('Delivery socket already connected')
      return
    }

    this.socket = io(`${WS_URL}/delivery`, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: this.reconnectDelay,
      reconnectionAttempts: this.maxReconnectAttempts,
      query: driverId ? { driver_id: driverId } : undefined,
    })

    this.socket.on('connect', () => {
      console.log('Delivery socket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', (reason) => {
      console.log('Delivery socket disconnected:', reason)
    })

    this.socket.on('connect_error', (error) => {
      console.error('Delivery socket connection error:', error)
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

  // Listen for new delivery orders
  onNewDelivery(callback: (order: DeliveryOrder) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('new_delivery', callback)
  }

  // Listen for delivery updates
  onDeliveryUpdate(callback: (order: DeliveryOrder) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('delivery_update', callback)
  }

  // Listen for delivery status changes
  onDeliveryStatusChange(callback: (data: { order_id: number; status: DeliveryStatus }) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('delivery_status_change', callback)
  }

  // Listen for driver location updates
  onDriverLocationUpdate(callback: (location: DriverLocation) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('driver_location_update', callback)
  }

  // Listen for driver status changes
  onDriverStatusChange(callback: (driver: Driver) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('driver_status_change', callback)
  }

  // Emit delivery assignment
  assignDelivery(deliveryId: number, driverId: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('assign_delivery', { delivery_id: deliveryId, driver_id: driverId })
  }

  // Emit delivery status update
  updateDeliveryStatus(deliveryId: number, status: DeliveryStatus) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('update_delivery_status', { delivery_id: deliveryId, status })
  }

  // Emit driver location update
  updateDriverLocation(driverId: number, latitude: number, longitude: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('update_driver_location', {
      driver_id: driverId,
      latitude,
      longitude,
      timestamp: new Date().toISOString(),
    })
  }

  // Emit driver status update
  updateDriverStatus(driverId: number, status: 'available' | 'busy' | 'offline') {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('update_driver_status', { driver_id: driverId, status })
  }

  // Join driver room (for driver-specific notifications)
  joinDriverRoom(driverId: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('join_driver_room', { driver_id: driverId })
  }

  // Leave driver room
  leaveDriverRoom(driverId: number) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('leave_driver_room', { driver_id: driverId })
  }

  // Request all active drivers locations
  requestAllDriversLocations() {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.emit('request_all_drivers_locations')
  }

  // Listen for all drivers locations response
  onAllDriversLocations(callback: (locations: DriverLocation[]) => void) {
    if (!this.socket) {
      console.error('Socket not connected')
      return
    }
    this.socket.on('all_drivers_locations', callback)
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

export const deliverySocket = new DeliverySocketService()
