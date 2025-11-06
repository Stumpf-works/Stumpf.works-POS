# Delivery Management Plugin - Frontend Integration

## Übersicht

Das Delivery Management Plugin benötigt eine umfassende Frontend-Integration für Lieferauftragsverwaltung, Echtzeit-Fahrer-Tracking, Routenoptimierung und GPS-basierte Verfolgung.

## Erforderliche Dependencies

```json
{
  "dependencies": {
    "leaflet": "^1.9.4",
    "react-leaflet": "^4.2.1",
    "socket.io-client": "^4.7.2",
    "@turf/turf": "^6.5.0"
  }
}
```

## Erforderliche UI-Komponenten

### 1. Delivery Dashboard (Haupt-Dashboard)

#### DeliveryDashboard
```tsx
// src/pages/plugins/delivery/DeliveryDashboard.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Package, Truck, MapPin, Clock } from 'lucide-react';

interface DashboardStats {
  pending_orders: number;
  in_transit: number;
  delivered_today: number;
  active_drivers: number;
  average_delivery_time: number;
}

export function DeliveryDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    const response = await fetch('/api/v1/delivery/dashboard/stats');
    const data = await response.json();
    setStats(data);
  };

  if (!stats) return <div>Lädt...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Lieferverwaltung</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Ausstehend</p>
              <p className="text-2xl font-bold">{stats.pending_orders}</p>
            </div>
            <Package className="h-8 w-8 text-orange-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Unterwegs</p>
              <p className="text-2xl font-bold">{stats.in_transit}</p>
            </div>
            <Truck className="h-8 w-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Heute geliefert</p>
              <p className="text-2xl font-bold">{stats.delivered_today}</p>
            </div>
            <MapPin className="h-8 w-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Aktive Fahrer</p>
              <p className="text-2xl font-bold">{stats.active_drivers}</p>
            </div>
            <Truck className="h-8 w-8 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="orders">
        <TabsList>
          <TabsTrigger value="orders">Bestellungen</TabsTrigger>
          <TabsTrigger value="drivers">Fahrer</TabsTrigger>
          <TabsTrigger value="map">Karte</TabsTrigger>
          <TabsTrigger value="routes">Routen</TabsTrigger>
        </TabsList>

        <TabsContent value="orders">
          <DeliveryOrdersList />
        </TabsContent>

        <TabsContent value="drivers">
          <DriversListView />
        </TabsContent>

        <TabsContent value="map">
          <LiveTrackingMap />
        </TabsContent>

        <TabsContent value="routes">
          <RouteManagementView />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### 2. Live Tracking Map (Echtzeit-Karte)

#### LiveTrackingMap
```tsx
// src/pages/plugins/delivery/LiveTrackingMap.tsx
import { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Icon } from 'leaflet';
import { io, Socket } from 'socket.io-client';
import 'leaflet/dist/leaflet.css';

interface Driver {
  id: number;
  driver_name: string;
  current_latitude: number;
  current_longitude: number;
  status: string;
  vehicle_type: string;
}

interface DeliveryOrder {
  id: number;
  order_number: string;
  delivery_latitude: number;
  delivery_longitude: number;
  status: string;
  driver_id: number | null;
}

export function LiveTrackingMap() {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [orders, setOrders] = useState<DeliveryOrder[]>([]);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Initial data fetch
    fetchDrivers();
    fetchOrders();

    // Setup WebSocket connection for real-time updates
    socketRef.current = io(process.env.REACT_APP_WS_URL || 'ws://localhost:8000', {
      path: '/ws/delivery',
    });

    socketRef.current.on('driver_location_update', (data) => {
      setDrivers((prev) =>
        prev.map((driver) =>
          driver.id === data.driver_id
            ? {
                ...driver,
                current_latitude: data.latitude,
                current_longitude: data.longitude,
              }
            : driver
        )
      );
    });

    socketRef.current.on('order_status_update', (data) => {
      setOrders((prev) =>
        prev.map((order) =>
          order.id === data.order_id ? { ...order, status: data.status } : order
        )
      );
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  const fetchDrivers = async () => {
    const response = await fetch('/api/v1/delivery/drivers?status=available,busy');
    const data = await response.json();
    setDrivers(data.drivers);
  };

  const fetchOrders = async () => {
    const response = await fetch('/api/v1/delivery/orders?status=assigned,in_transit');
    const data = await response.json();
    setOrders(data.orders);
  };

  // Custom icons
  const driverIcon = new Icon({
    iconUrl: '/icons/driver-marker.png',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  });

  const orderIcon = new Icon({
    iconUrl: '/icons/delivery-marker.png',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
  });

  return (
    <div className="h-[600px] rounded-lg overflow-hidden">
      <MapContainer
        center={[51.1657, 10.4515]} // Center of Germany
        zoom={6}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Driver markers */}
        {drivers.map((driver) => (
          <Marker
            key={driver.id}
            position={[driver.current_latitude, driver.current_longitude]}
            icon={driverIcon}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold">{driver.driver_name}</h3>
                <p className="text-sm">Status: {driver.status}</p>
                <p className="text-sm">Fahrzeug: {driver.vehicle_type}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Order markers */}
        {orders.map((order) => (
          <Marker
            key={order.id}
            position={[order.delivery_latitude, order.delivery_longitude]}
            icon={orderIcon}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold">{order.order_number}</h3>
                <p className="text-sm">Status: {order.status}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Route lines between drivers and their orders */}
        {orders
          .filter((order) => order.driver_id)
          .map((order) => {
            const driver = drivers.find((d) => d.id === order.driver_id);
            if (!driver) return null;

            return (
              <Polyline
                key={`route-${order.id}`}
                positions={[
                  [driver.current_latitude, driver.current_longitude],
                  [order.delivery_latitude, order.delivery_longitude],
                ]}
                color="blue"
                weight={3}
                opacity={0.7}
              />
            );
          })}
      </MapContainer>
    </div>
  );
}
```

### 3. Order Assignment (Auftragszuweisung)

#### OrderAssignmentView
```tsx
// src/pages/plugins/delivery/OrderAssignmentView.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { MapPin, Clock, Package } from 'lucide-react';

interface UnassignedOrder {
  id: number;
  order_number: string;
  customer_name: string;
  delivery_address: string;
  scheduled_delivery_time: string;
  total_amount: number;
  priority: string;
}

interface AvailableDriver {
  id: number;
  driver_name: string;
  vehicle_type: string;
  current_orders: number;
  estimated_distance: number; // km from restaurant to delivery
}

export function OrderAssignmentView() {
  const [unassignedOrders, setUnassignedOrders] = useState<UnassignedOrder[]>([]);
  const [availableDrivers, setAvailableDrivers] = useState<AvailableDriver[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<number | null>(null);
  const [selectedDriver, setSelectedDriver] = useState<number | null>(null);

  useEffect(() => {
    fetchUnassignedOrders();
    fetchAvailableDrivers();
  }, []);

  const fetchUnassignedOrders = async () => {
    const response = await fetch('/api/v1/delivery/orders?status=pending');
    const data = await response.json();
    setUnassignedOrders(data.orders);
  };

  const fetchAvailableDrivers = async () => {
    const response = await fetch('/api/v1/delivery/drivers?status=available');
    const data = await response.json();
    setAvailableDrivers(data.drivers);
  };

  const assignOrder = async () => {
    if (!selectedOrder || !selectedDriver) return;

    try {
      await fetch(`/api/v1/delivery/orders/${selectedOrder}/assign/${selectedDriver}`, {
        method: 'POST',
      });

      // Refresh lists
      fetchUnassignedOrders();
      fetchAvailableDrivers();
      setSelectedOrder(null);
      setSelectedDriver(null);
    } catch (error) {
      console.error('Failed to assign order:', error);
    }
  };

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Unassigned Orders */}
      <Card className="p-4">
        <h2 className="text-xl font-semibold mb-4">Nicht zugewiesene Bestellungen</h2>

        <div className="space-y-3">
          {unassignedOrders.map((order) => (
            <div
              key={order.id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedOrder === order.id ? 'border-blue-500 bg-blue-50' : ''
              }`}
              onClick={() => setSelectedOrder(order.id)}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-semibold">{order.order_number}</h3>
                  <p className="text-sm text-muted-foreground">{order.customer_name}</p>
                </div>
                <Badge
                  variant={
                    order.priority === 'high'
                      ? 'destructive'
                      : order.priority === 'normal'
                      ? 'default'
                      : 'secondary'
                  }
                >
                  {order.priority}
                </Badge>
              </div>

              <div className="space-y-1 text-sm">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  <span>{order.delivery_address}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  <span>
                    {new Date(order.scheduled_delivery_time).toLocaleTimeString('de-DE', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Package className="h-4 w-4" />
                  <span>{order.total_amount.toFixed(2)} €</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Available Drivers */}
      <Card className="p-4">
        <h2 className="text-xl font-semibold mb-4">Verfügbare Fahrer</h2>

        <div className="space-y-3">
          {availableDrivers.map((driver) => (
            <div
              key={driver.id}
              className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                selectedDriver === driver.id ? 'border-blue-500 bg-blue-50' : ''
              }`}
              onClick={() => setSelectedDriver(driver.id)}
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-semibold">{driver.driver_name}</h3>
                  <p className="text-sm text-muted-foreground">{driver.vehicle_type}</p>
                </div>
                <Badge variant="outline">{driver.current_orders} aktive Aufträge</Badge>
              </div>

              {selectedOrder && (
                <div className="mt-2 text-sm text-muted-foreground">
                  Geschätzte Entfernung: {driver.estimated_distance.toFixed(1)} km
                </div>
              )}
            </div>
          ))}
        </div>

        <Button
          className="w-full mt-4"
          disabled={!selectedOrder || !selectedDriver}
          onClick={assignOrder}
        >
          Auftrag zuweisen
        </Button>
      </Card>
    </div>
  );
}
```

### 4. Driver Management (Fahrerverwaltung)

#### DriverManagementView
```tsx
// src/pages/plugins/delivery/DriverManagementView.tsx
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Plus, Edit, Trash2 } from 'lucide-react';
import { useForm } from 'react-hook-form';

interface Driver {
  id: number;
  driver_name: string;
  driver_phone: string;
  driver_email: string;
  vehicle_type: string;
  vehicle_number: string;
  status: string;
  total_deliveries: number;
  average_rating: number;
  is_active: boolean;
}

export function DriverManagementView() {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingDriver, setEditingDriver] = useState<Driver | null>(null);

  const form = useForm<Driver>();

  const onSubmit = async (data: Driver) => {
    try {
      const url = editingDriver
        ? `/api/v1/delivery/drivers/${editingDriver.id}`
        : '/api/v1/delivery/drivers';

      const method = editingDriver ? 'PUT' : 'POST';

      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      setIsDialogOpen(false);
      setEditingDriver(null);
      fetchDrivers();
    } catch (error) {
      console.error('Failed to save driver:', error);
    }
  };

  const updateDriverStatus = async (driverId: number, status: string) => {
    try {
      await fetch(`/api/v1/delivery/drivers/${driverId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      fetchDrivers();
    } catch (error) {
      console.error('Failed to update driver status:', error);
    }
  };

  const fetchDrivers = async () => {
    const response = await fetch('/api/v1/delivery/drivers');
    const data = await response.json();
    setDrivers(data.drivers);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'success';
      case 'busy':
        return 'warning';
      case 'on_break':
        return 'secondary';
      case 'offline':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'available':
        return 'Verfügbar';
      case 'busy':
        return 'Beschäftigt';
      case 'on_break':
        return 'Pause';
      case 'offline':
        return 'Offline';
      default:
        return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Fahrerverwaltung</h1>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Neuer Fahrer
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {drivers.map((driver) => (
          <Card key={driver.id} className="p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-semibold text-lg">{driver.driver_name}</h3>
                <p className="text-sm text-muted-foreground">{driver.vehicle_type}</p>
              </div>
              <Badge variant={getStatusColor(driver.status)}>
                {getStatusLabel(driver.status)}
              </Badge>
            </div>

            <div className="space-y-2 text-sm mb-4">
              <div>
                <span className="text-muted-foreground">Telefon:</span> {driver.driver_phone}
              </div>
              <div>
                <span className="text-muted-foreground">Kennzeichen:</span>{' '}
                {driver.vehicle_number}
              </div>
              <div>
                <span className="text-muted-foreground">Lieferungen:</span>{' '}
                {driver.total_deliveries}
              </div>
              <div>
                <span className="text-muted-foreground">Bewertung:</span>{' '}
                {driver.average_rating ? `⭐ ${driver.average_rating.toFixed(1)}` : 'N/A'}
              </div>
            </div>

            <div className="flex gap-2">
              <Select
                value={driver.status}
                onChange={(e) => updateDriverStatus(driver.id, e.target.value)}
                className="flex-1"
              >
                <option value="available">Verfügbar</option>
                <option value="busy">Beschäftigt</option>
                <option value="on_break">Pause</option>
                <option value="offline">Offline</option>
              </Select>

              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setEditingDriver(driver);
                  form.reset(driver);
                  setIsDialogOpen(true);
                }}
              >
                <Edit className="h-4 w-4" />
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Driver Form Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingDriver ? 'Fahrer bearbeiten' : 'Neuer Fahrer'}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Name</label>
              <Input {...form.register('driver_name')} required />
            </div>

            <div>
              <label className="text-sm font-medium">Telefon</label>
              <Input {...form.register('driver_phone')} required />
            </div>

            <div>
              <label className="text-sm font-medium">E-Mail</label>
              <Input type="email" {...form.register('driver_email')} />
            </div>

            <div>
              <label className="text-sm font-medium">Fahrzeugtyp</label>
              <Select {...form.register('vehicle_type')} required>
                <option value="bike">Fahrrad</option>
                <option value="scooter">Roller</option>
                <option value="motorcycle">Motorrad</option>
                <option value="car">Auto</option>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium">Kennzeichen</label>
              <Input {...form.register('vehicle_number')} />
            </div>

            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
              >
                Abbrechen
              </Button>
              <Button type="submit">Speichern</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
```

### 5. Order Tracking Widget (für Kunden)

#### CustomerTrackingWidget
```tsx
// src/pages/plugins/delivery/CustomerTrackingWidget.tsx
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline } from 'react-leaflet';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Package, Truck, MapPin, CheckCircle } from 'lucide-react';

interface TrackingInfo {
  order_number: string;
  status: string;
  customer_name: string;
  delivery_address: string;
  driver_name: string;
  driver_phone: string;
  driver_latitude: number;
  driver_longitude: number;
  delivery_latitude: number;
  delivery_longitude: number;
  estimated_arrival: string;
  tracking_updates: Array<{
    status: string;
    timestamp: string;
    status_message: string;
  }>;
}

export function CustomerTrackingWidget({ orderId }: { orderId: number }) {
  const [tracking, setTracking] = useState<TrackingInfo | null>(null);

  useEffect(() => {
    fetchTracking();
    const interval = setInterval(fetchTracking, 10000); // Update every 10s
    return () => clearInterval(interval);
  }, [orderId]);

  const fetchTracking = async () => {
    const response = await fetch(`/api/v1/delivery/tracking/${orderId}`);
    const data = await response.json();
    setTracking(data);
  };

  if (!tracking) return <div>Lädt Tracking-Informationen...</div>;

  const statusSteps = ['pending', 'assigned', 'picked_up', 'in_transit', 'delivered'];
  const currentStep = statusSteps.indexOf(tracking.status);
  const progress = ((currentStep + 1) / statusSteps.length) * 100;

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <Card className="p-6">
        <h2 className="text-xl font-bold mb-4">
          Bestellung {tracking.order_number} wird geliefert
        </h2>

        <Progress value={progress} className="mb-6" />

        {/* Status Timeline */}
        <div className="flex justify-between mb-8">
          <div className="flex flex-col items-center">
            <div
              className={`rounded-full p-2 ${
                currentStep >= 0 ? 'bg-green-500' : 'bg-gray-300'
              }`}
            >
              <Package className="h-5 w-5 text-white" />
            </div>
            <span className="text-xs mt-2">Bestätigt</span>
          </div>

          <div className="flex flex-col items-center">
            <div
              className={`rounded-full p-2 ${
                currentStep >= 2 ? 'bg-green-500' : 'bg-gray-300'
              }`}
            >
              <Truck className="h-5 w-5 text-white" />
            </div>
            <span className="text-xs mt-2">Abgeholt</span>
          </div>

          <div className="flex flex-col items-center">
            <div
              className={`rounded-full p-2 ${
                currentStep >= 3 ? 'bg-green-500' : 'bg-gray-300'
              }`}
            >
              <MapPin className="h-5 w-5 text-white" />
            </div>
            <span className="text-xs mt-2">Unterwegs</span>
          </div>

          <div className="flex flex-col items-center">
            <div
              className={`rounded-full p-2 ${
                currentStep >= 4 ? 'bg-green-500' : 'bg-gray-300'
              }`}
            >
              <CheckCircle className="h-5 w-5 text-white" />
            </div>
            <span className="text-xs mt-2">Zugestellt</span>
          </div>
        </div>

        {/* Driver Info */}
        {tracking.driver_name && (
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 className="font-semibold mb-2">Ihr Fahrer</h3>
            <p>{tracking.driver_name}</p>
            <p className="text-sm text-muted-foreground">{tracking.driver_phone}</p>
          </div>
        )}

        {/* ETA */}
        {tracking.estimated_arrival && (
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-muted-foreground">Voraussichtliche Ankunft</p>
            <p className="text-2xl font-bold">
              {new Date(tracking.estimated_arrival).toLocaleTimeString('de-DE', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
        )}
      </Card>

      {/* Live Map */}
      {tracking.driver_latitude && tracking.driver_longitude && (
        <Card className="p-4">
          <h3 className="font-semibold mb-4">Live-Standort</h3>
          <div className="h-[300px] rounded-lg overflow-hidden">
            <MapContainer
              center={[tracking.driver_latitude, tracking.driver_longitude]}
              zoom={13}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

              <Marker position={[tracking.driver_latitude, tracking.driver_longitude]} />

              <Marker position={[tracking.delivery_latitude, tracking.delivery_longitude]} />

              <Polyline
                positions={[
                  [tracking.driver_latitude, tracking.driver_longitude],
                  [tracking.delivery_latitude, tracking.delivery_longitude],
                ]}
                color="blue"
              />
            </MapContainer>
          </div>
        </Card>
      )}

      {/* Tracking History */}
      <Card className="p-4">
        <h3 className="font-semibold mb-4">Lieferstatus-Verlauf</h3>
        <div className="space-y-3">
          {tracking.tracking_updates.map((update, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className="h-2 w-2 rounded-full bg-blue-500 mt-2" />
              <div className="flex-1">
                <p className="font-medium">{update.status_message}</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(update.timestamp).toLocaleString('de-DE')}
                </p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
```

## Routing-Konfiguration

```tsx
// src/routes/deliveryRoutes.tsx
import { Route } from 'react-router-dom';
import { DeliveryDashboard } from '@/pages/plugins/delivery/DeliveryDashboard';
import { OrderAssignmentView } from '@/pages/plugins/delivery/OrderAssignmentView';
import { DriverManagementView } from '@/pages/plugins/delivery/DriverManagementView';
import { LiveTrackingMap } from '@/pages/plugins/delivery/LiveTrackingMap';
import { CustomerTrackingWidget } from '@/pages/plugins/delivery/CustomerTrackingWidget';

export const deliveryRoutes = (
  <Route path="/delivery">
    <Route index element={<DeliveryDashboard />} />
    <Route path="assign" element={<OrderAssignmentView />} />
    <Route path="drivers" element={<DriverManagementView />} />
    <Route path="map" element={<LiveTrackingMap />} />
    <Route path="track/:orderId" element={<CustomerTrackingWidget />} />
  </Route>
);
```

## WebSocket Integration

```tsx
// src/services/deliverySocket.ts
import { io, Socket } from 'socket.io-client';

class DeliverySocketService {
  private socket: Socket | null = null;

  connect() {
    this.socket = io(process.env.REACT_APP_WS_URL || 'ws://localhost:8000', {
      path: '/ws/delivery',
      auth: {
        token: localStorage.getItem('auth_token'),
      },
    });

    this.socket.on('connect', () => {
      console.log('Connected to delivery socket');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from delivery socket');
    });
  }

  subscribeToDriverUpdates(callback: (data: any) => void) {
    this.socket?.on('driver_location_update', callback);
  }

  subscribeToOrderUpdates(callback: (data: any) => void) {
    this.socket?.on('order_status_update', callback);
  }

  updateDriverLocation(driverId: number, latitude: number, longitude: number) {
    this.socket?.emit('update_driver_location', {
      driver_id: driverId,
      latitude,
      longitude,
    });
  }

  disconnect() {
    this.socket?.disconnect();
  }
}

export const deliverySocket = new DeliverySocketService();
```

## State Management

```tsx
// src/stores/deliveryStore.ts
import { create } from 'zustand';

interface DeliveryStore {
  orders: any[];
  drivers: any[];
  selectedOrder: number | null;
  selectedDriver: number | null;

  setOrders: (orders: any[]) => void;
  setDrivers: (drivers: any[]) => void;
  setSelectedOrder: (id: number | null) => void;
  setSelectedDriver: (id: number | null) => void;
}

export const useDeliveryStore = create<DeliveryStore>((set) => ({
  orders: [],
  drivers: [],
  selectedOrder: null,
  selectedDriver: null,

  setOrders: (orders) => set({ orders }),
  setDrivers: (drivers) => set({ drivers }),
  setSelectedOrder: (selectedOrder) => set({ selectedOrder }),
  setSelectedDriver: (selectedDriver) => set({ selectedDriver }),
}));
```

## Deployment Checklist

- [ ] Leaflet und React-Leaflet installiert
- [ ] Socket.IO Client konfiguriert
- [ ] Karten-Tiles (OpenStreetMap) konfiguriert
- [ ] WebSocket-Verbindung getestet
- [ ] GPS-Tracking implementiert
- [ ] Echtzeit-Updates funktionieren
- [ ] Mobile Responsive Design
- [ ] Driver App Integration geplant
- [ ] Push-Benachrichtigungen konfiguriert
- [ ] Offline-Modus für Fahrer
