# Kitchen Display System Plugin - Frontend Integration

## Übersicht

Digitales Küchendisplay-System für Restaurants mit Echtzeit-Bestellanzeige, Multi-Station-Support, Timern und Priorisierung.

## Dependencies

```json
{
  "dependencies": {
    "socket.io-client": "^4.7.2",
    "howler": "^2.2.4"
  }
}
```

## Key Components

### 1. Kitchen Display Screen
```tsx
// Main display for kitchen staff
- Real-time order queue
- Color-coded priority
- Countdown timers
- Audio alerts for new orders
- Large, touch-friendly UI
```

### 2. Multi-Station View
```tsx
// Different stations (Grill, Salads, Desserts)
- Station-specific orders
- Filter by station
- Transfer orders between stations
```

### 3. Order Card
```tsx
// Individual order display
- Order number (large font)
- Items with modifications
- Special instructions
- Elapsed time
- Mark as ready button
```

## Main View

```tsx
// Kitchen Display - Full screen optimized
export function KitchenDisplayScreen({ stationId }) {
  const [orders, setOrders] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    // WebSocket connection for real-time orders
    socketRef.current = io(WS_URL);

    socketRef.current.on('new_order', (order) => {
      playAlertSound();
      setOrders(prev => [order, ...prev]);
    });

    socketRef.current.on('order_update', (update) => {
      setOrders(prev => prev.map(o =>
        o.id === update.id ? { ...o, ...update } : o
      ));
    });

    return () => socketRef.current?.disconnect();
  }, []);

  return (
    <div className="h-screen bg-gray-900 p-4">
      <StationHeader stationId={stationId} />

      <div className="grid grid-cols-3 gap-4 mt-4">
        {orders.map(order => (
          <OrderCard
            key={order.id}
            order={order}
            onComplete={() => markOrderReady(order.id)}
          />
        ))}
      </div>
    </div>
  );
}

// Order Card Component
export function OrderCard({ order, onComplete }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const diff = Date.now() - new Date(order.created_at);
      setElapsed(Math.floor(diff / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [order.created_at]);

  const isUrgent = elapsed > order.target_time * 60;
  const isWarning = elapsed > (order.target_time * 0.75) * 60;

  return (
    <Card
      className={`p-6 ${
        isUrgent ? 'bg-red-100 border-red-500' :
        isWarning ? 'bg-yellow-100 border-yellow-500' :
        'bg-white'
      }`}
    >
      {/* Order Number - Large */}
      <div className="text-6xl font-bold mb-4">
        #{order.order_number}
      </div>

      {/* Timer */}
      <div className={`text-3xl font-mono mb-4 ${
        isUrgent ? 'text-red-600' :
        isWarning ? 'text-yellow-600' :
        'text-gray-600'
      }`}>
        {formatTime(elapsed)}
      </div>

      {/* Order Items */}
      <div className="space-y-2 mb-6">
        {order.items.map(item => (
          <div key={item.id} className="text-xl">
            <span className="font-semibold">{item.quantity}x</span> {item.product_name}
            {item.modifications && (
              <div className="text-sm text-gray-600 ml-6">
                {item.modifications}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Special Instructions */}
      {order.special_instructions && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-3 mb-4">
          <p className="text-lg font-semibold text-blue-900">
            ⚠️ {order.special_instructions}
          </p>
        </div>
      )}

      {/* Actions */}
      <Button
        size="lg"
        className="w-full text-xl py-6"
        onClick={onComplete}
      >
        Fertig
      </Button>
    </Card>
  );
}
```

## WebSocket Integration

```tsx
// Kitchen socket service
export class KitchenSocketService {
  connect(stationId) {
    this.socket = io(WS_URL, {
      query: { station_id: stationId }
    });

    this.socket.on('connect', () => {
      console.log('Connected to kitchen display');
    });
  }

  subscribeToOrders(callback) {
    this.socket.on('new_order', callback);
    this.socket.on('order_update', callback);
  }

  markOrderReady(orderId) {
    this.socket.emit('order_ready', { order_id: orderId });
  }
}
```

## Audio Alerts

```tsx
import { Howl } from 'howler';

const newOrderSound = new Howl({
  src: ['/sounds/new-order.mp3'],
  volume: 0.8,
});

export function playNewOrderAlert() {
  newOrderSound.play();
}
```

## Admin Configuration

```tsx
// Station Management
export function StationManagement() {
  return (
    <div>
      <h1>Stationen verwalten</h1>

      <StationList>
        {stations.map(station => (
          <StationCard
            key={station.id}
            station={station}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}
      </StationList>

      <CreateStationButton />
    </div>
  );
}

// Settings
export function KitchenDisplaySettings() {
  return (
    <Form>
      <FormField label="Standard-Zubereitungszeit (Min)">
        <Input type="number" defaultValue={15} />
      </FormField>

      <FormField label="Warnschwelle (%)">
        <Input type="number" defaultValue={75} />
      </FormField>

      <FormField label="Alarm aktivieren">
        <Switch />
      </FormField>

      <FormField label="Alarm-Lautstärke">
        <Slider min={0} max={100} defaultValue={80} />
      </FormField>
    </Form>
  );
}
```

## Features
- **Real-time order updates via WebSocket**
- **Multi-station support**
- **Visual & audio alerts**
- **Color-coded urgency (green → yellow → red)**
- **Touch-optimized large UI**
- **Order prioritization**
- **Preparation time tracking**
- **Full-screen display mode**
- **Offline queue support**

## Display Modes

### Standard Mode
- 3-column grid layout
- Shows all pending orders
- Sorted by time

### Expo Mode
- Single column, larger cards
- For final quality check station
- Mark orders for delivery

### Tablet Mode
- Optimized for smaller screens
- 1-2 column layout

## Routing
```tsx
/kitchen-display
  /:stationId - Kitchen display screen (full screen)
  /admin/stations - Station management
  /admin/settings - Display settings
  /admin/stats - Kitchen performance stats
```

## Deployment Notes
- **Dedicated hardware**: Tablet or monitor in kitchen
- **Kiosk mode**: Prevent accidental navigation
- **Auto-reconnect**: Handle network interruptions
- **Large touch targets**: Minimum 60px
- **High contrast**: Visible in bright kitchen lighting
- **Water/heat resistant**: Consider hardware protection
