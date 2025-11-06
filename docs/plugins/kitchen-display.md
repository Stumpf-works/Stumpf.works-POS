# Kitchen Display System Plugin

**Kategorie:** `restaurant`
**Version:** 1.0.0
**Autor:** Stumpf.works

## Übersicht

Digitales Küchen-Display für professionelles Bestellmanagement. Ersetzt Papier-Bons durch Echtzeit-Displays mit Timern und Priorisierung.

---

## Features

✅ **Real-time Orders** - Bestellungen sofort in Küche
✅ **Multi-Station** - Grill, Kalt, Dessert, Bar
✅ **Status Tracking** - new → in_progress → completed
✅ **Auto-Timers** - Countdown pro Gericht
✅ **Priority System** - Normal, High, Urgent
✅ **Color Coding** - Rot bei Verzögerung
✅ **Performance Stats** - Durchlaufzeit, Peak Hours
✅ **Acoustic Alerts** - Sound bei neuer Bestellung

---

## Konfiguration

```json
{
  "enable_timers": true,
  "default_prep_time_minutes": 15,
  "alert_after_minutes": 20,
  "stations": ["Grill", "Kalt", "Dessert", "Bar"],
  "auto_print_receipt": true
}
```

---

## API Endpoints

### Stations

#### `GET /api/v1/kitchen/stations`
Liste alle Küchenstationen.

**Response:**
```json
[
  {
    "id": 1,
    "station_name": "Grill",
    "station_type": "grill",
    "display_order": 1,
    "is_active": true,
    "color": "#ff5722"
  },
  {
    "id": 2,
    "station_name": "Kalt",
    "station_type": "cold",
    "display_order": 2,
    "is_active": true,
    "color": "#2196f3"
  }
]
```

#### `POST /api/v1/kitchen/stations`
Neue Station erstellen.

**Request:**
```json
{
  "station_name": "Pizza-Ofen",
  "station_type": "pizza",
  "display_order": 3,
  "color": "#ff9800"
}
```

---

### Orders

#### `GET /api/v1/kitchen/orders/active`
Aktive Bestellungen.

**Query Parameters:**
- `station_id` (optional): Filter nach Station

**Response:**
```json
[
  {
    "id": 1,
    "order_number": "T5-001",
    "table_number": 5,
    "order_type": "dine_in",
    "status": "in_progress",
    "priority": 0,
    "received_at": "2025-11-06T18:30:00Z",
    "started_at": "2025-11-06T18:32:00Z",
    "completed_at": null,
    "prep_time_minutes": 15,
    "actual_time_minutes": null,
    "notes": "Ohne Zwiebeln",
    "items": [
      {
        "id": 1,
        "item_name": "Rumpsteak medium",
        "quantity": 1,
        "status": "cooking",
        "station_id": 1,
        "station_name": "Grill",
        "started_at": "2025-11-06T18:32:00Z",
        "completed_at": null,
        "prep_time_minutes": 15,
        "special_instructions": "Medium-rare"
      }
    ],
    "elapsed_minutes": 8,
    "is_urgent": false
  }
]
```

**Status-Codes:**
- `new` - Neu eingegangen
- `in_progress` - In Zubereitung
- `completed` - Fertig
- `cancelled` - Storniert

#### `POST /api/v1/kitchen/orders`
Neue Bestellung erstellen.

**Request:**
```json
{
  "order_number": "T5-001",
  "table_number": 5,
  "order_type": "dine_in",
  "priority": 0,
  "items": [
    {
      "item_name": "Rumpsteak medium",
      "quantity": 1,
      "station_id": 1,
      "prep_time_minutes": 15,
      "special_instructions": "Medium-rare"
    },
    {
      "item_name": "Pommes Frites",
      "quantity": 1,
      "station_id": 1,
      "prep_time_minutes": 8
    }
  ],
  "notes": "Ohne Zwiebeln"
}
```

#### `POST /api/v1/kitchen/orders/{order_id}/start`
Bestellung starten (Timer aktivieren).

**Response:**
```json
{
  "order_id": 1,
  "started_at": "2025-11-06T18:32:00Z",
  "message": "Order started"
}
```

**Auto-Features:**
- Status → `in_progress`
- Timer startet
- Alle Items → `cooking`

#### `POST /api/v1/kitchen/orders/{order_id}/complete`
Bestellung abschließen.

**Response:**
```json
{
  "order_id": 1,
  "completed_at": "2025-11-06T18:47:00Z",
  "actual_time_minutes": 15,
  "message": "Order completed"
}
```

**Auto-Features:**
- Status → `completed`
- Timer stoppt
- Alle Items → `ready`
- Waiter-Notification (optional)

#### `PATCH /api/v1/kitchen/orders/{order_id}/status`
Status manuell ändern.

**Request:**
```json
{
  "status": "completed"
}
```

---

### Statistics

#### `GET /api/v1/kitchen/stats`
Performance-Statistiken.

**Query Parameters:**
- `date` (optional): Datum (default: heute)

**Response:**
```json
{
  "date": "2025-11-06",
  "total_orders": 45,
  "completed_orders": 42,
  "cancelled_orders": 2,
  "in_progress": 1,
  "average_prep_time_minutes": 14,
  "peak_hour": 19
}
```

---

## Anwendungsbeispiele

### Beispiel 1: Standard-Workflow

```bash
# 1. Kellner nimmt Bestellung auf (POS)
# 2. POS sendet an Kitchen Display
POST /api/v1/kitchen/orders
{
  "order_number": "T3-005",
  "table_number": 3,
  "items": [
    {"item_name": "Schnitzel", "station_id": 1, "quantity": 2}
  ]
}

# 3. Küche sieht neue Bestellung auf Display (Status: NEW)
# 4. Koch startet Zubereitung
POST /api/v1/kitchen/orders/5/start
# -> Timer läuft (15 Min)

# 5. Gericht fertig
POST /api/v1/kitchen/orders/5/complete
# -> Waiter wird benachrichtigt
```

### Beispiel 2: Multi-Station Order

```bash
# Bestellung mit mehreren Stationen
POST /api/v1/kitchen/orders
{
  "order_number": "T8-012",
  "table_number": 8,
  "items": [
    {"item_name": "Steak", "station_id": 1, "quantity": 1},      # Grill
    {"item_name": "Salat", "station_id": 2, "quantity": 1},      # Kalt
    {"item_name": "Tiramisu", "station_id": 3, "quantity": 1}    # Dessert
  ]
}

# Jede Station sieht nur ihre Gerichte
GET /api/v1/kitchen/orders/active?station_id=1  # Grill: Steak
GET /api/v1/kitchen/orders/active?station_id=2  # Kalt: Salat
GET /api/v1/kitchen/orders/active?station_id=3  # Dessert: Tiramisu
```

### Beispiel 3: Rush Hour Management

```bash
# Viele Bestellungen gleichzeitig
# System sortiert automatisch nach:
# 1. Priority (urgent > high > normal)
# 2. Elapsed Time (älteste zuerst)
# 3. Order Number

# Farb-Kodierung:
# Grün: < 15 Min
# Gelb: 15-20 Min
# Rot: > 20 Min (Alert!)
```

---

## Display-Layout

### Kachel-Ansicht (empfohlen)

```
┌─────────────────────────────────────────┐
│  [T5] Order #001        ⏱️ 08:32        │
│  ────────────────────────────────────── │
│  🍖 1x Rumpsteak medium                 │
│  🍟 1x Pommes Frites                    │
│                                          │
│  💬 Ohne Zwiebeln                        │
│  ────────────────────────────────────── │
│  Status: IN PROGRESS    Priority: 🟢    │
└─────────────────────────────────────────┘
```

### Listen-Ansicht

```
Table | Order  | Items | Status      | Time   | Action
──────┼────────┼───────┼─────────────┼────────┼────────
  5   | #001   |   2   | IN PROGRESS | 08:32  | [✓ Done]
  3   | #002   |   1   | NEW         | 00:15  | [▶ Start]
  8   | #003   |   4   | IN PROGRESS | 15:44  | [✓ Done]
```

---

## Hardware-Empfehlungen

### Küchen-Display
- **Größe:** min. 24" (besser 32")
- **Touchscreen:** Ja (für Status-Updates)
- **Schutz:** IP65 (spritzwassergeschützt)
- **Helligkeit:** min. 300 cd/m² (Küchen-Licht)
- **Montage:** Wandmontage oder VESA-Arm

### Beispiel-Setup (3 Stationen)
```
Station 1: Grill      → 24" Touchscreen
Station 2: Kalt       → 24" Touchscreen
Station 3: Dessert    → 21" Display (nur Anzeige)
Pass (Service)        → 32" Übersicht aller Stationen
```

---

## Best Practices

✅ **Prep-Times realistisch** - Basierend auf echten Messungen
✅ **Alert-Schwelle anpassen** - Rush Hour vs. ruhige Zeit
✅ **Stationen logisch aufteilen** - Nach Workflow
✅ **Farbcodes konsistent** - Grün/Gelb/Rot
✅ **Sound-Alerts dosiert** - Nur bei NEUEN Bestellungen

---

## Integration

### Mit POS-System
```python
# Wenn Kellner Bestellung abschickt
@router.post("/orders/submit")
async def submit_order(order_data: OrderCreate):
    # 1. Order in Datenbank speichern
    order = create_order(order_data)

    # 2. An Kitchen Display senden
    await kitchen_display.create_order({
        "order_number": order.number,
        "table_number": order.table_number,
        "items": order.items
    })

    # 3. Bon drucken (falls aktiviert)
    if config.auto_print_receipt:
        print_kitchen_receipt(order)

    return order
```

### Mit Table Management
```python
# Tisch-Nr. aus Reservierung übernehmen
reservation = get_reservation(reservation_id)
kitchen_order = create_kitchen_order(
    table_number=reservation.table_number
)
```

---

## WebSocket-Support (zukünftig)

```javascript
// Real-time Updates ohne Polling
const ws = new WebSocket('wss://api/kitchen/live');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);

    if (update.type === 'new_order') {
        playSound('ding.mp3');
        addOrderToDisplay(update.order);
    }

    if (update.type === 'order_updated') {
        updateOrderInDisplay(update.order);
    }
};
```

---

## Lizenzierung

**Standard:** 59€/Monat pro Location
**Enterprise:** Custom mit Multi-Location Support

---

## Support

📧 dev@stumpf.works
📖 https://docs.stumpf.works/plugins/kitchen-display
