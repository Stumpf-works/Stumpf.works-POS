# Inventory Management Pro Plugin

**Kategorie:** `retail`
**Version:** 1.0.0
**Autor:** Stumpf.works

## Übersicht

Erweiterte Bestandsverwaltung mit automatischen Bestellvorschlägen, Lieferantenverwaltung und Inventur-Funktionen. Ideal für Einzelhandel, Supermärkte und Warenlager.

---

## Features

✅ **Stock Level Tracking** - Min/Max-Levels und Reorder Points
✅ **Supplier Management** - Lieferanten mit Kontaktdaten
✅ **Purchase Orders** - Bestellungen an Lieferanten
✅ **Stock Movements** - Historie (Eingang, Ausgang, Anpassung)
✅ **Inventory Counts** - Inventur mit Differenz-Tracking
✅ **Low Stock Alerts** - Automatische Warnungen
✅ **Barcode Support** - Barcode-Tracking pro Produkt
✅ **Location Tracking** - Lagerort-Verwaltung

---

## Konfiguration

```json
{
  "enable_auto_reorder": true,
  "low_stock_threshold_percentage": 20,
  "enable_email_alerts": false,
  "default_supplier_id": null
}
```

---

## API Endpoints

### Stock Management

#### `GET /api/v1/inventory/stock`
Liste alle Bestandslevel.

**Query Parameters:**
- `low_stock_only` (boolean): Nur Artikel mit niedrigem Bestand

**Response:**
```json
[
  {
    "id": 1,
    "product_id": 100,
    "quantity": 50.0,
    "min_level": 20.0,
    "max_level": 200.0,
    "reorder_point": 30.0,
    "reorder_quantity": 100.0,
    "unit_cost": 5.99,
    "supplier_id": 5,
    "barcode": "4006381333931",
    "location": "Regal A3",
    "is_low_stock": false
  }
]
```

#### `POST /api/v1/inventory/stock/adjust`
Bestand anpassen.

**Request:**
```json
{
  "product_id": 100,
  "quantity": 50,
  "movement_type": "in",
  "unit_cost": 5.99,
  "notes": "Lieferung von Lieferant XYZ"
}
```

**Movement Types:**
- `in` - Wareneingang
- `out` - Warenausgang
- `adjustment` - Bestandskorrektur

#### `GET /api/v1/inventory/movements`
Bewegungshistorie abrufen.

**Query Parameters:**
- `product_id` (optional): Filter nach Produkt
- `limit` (default: 100): Max. Anzahl Ergebnisse

#### `GET /api/v1/inventory/low-stock`
Artikel mit niedrigem Bestand.

**Response:**
```json
{
  "count": 5,
  "items": [
    {
      "product_id": 100,
      "quantity": 15.0,
      "reorder_point": 30.0,
      "reorder_quantity": 100.0,
      "supplier_id": 5
    }
  ]
}
```

---

### Supplier Management

#### `GET /api/v1/inventory/suppliers`
Liste alle Lieferanten.

#### `POST /api/v1/inventory/suppliers`
Neuen Lieferanten anlegen.

**Request:**
```json
{
  "name": "Großhandel Müller GmbH",
  "code": "GM001",
  "contact_person": "Herr Müller",
  "email": "mueller@grosshandel.de",
  "phone": "+49 123 456789",
  "address": "Musterstraße 123, 12345 Musterstadt",
  "notes": "Lieferung dienstags und freitags"
}
```

---

### Purchase Orders

#### `POST /api/v1/inventory/purchase-orders`
Neue Bestellung erstellen.

**Request:**
```json
{
  "supplier_id": 5,
  "order_date": "2025-11-06T10:00:00Z",
  "expected_delivery": "2025-11-08T14:00:00Z",
  "notes": "Dringend - Aktionsware",
  "items": [
    {
      "product_id": 100,
      "quantity": 200,
      "unit_cost": 5.99
    },
    {
      "product_id": 101,
      "quantity": 150,
      "unit_cost": 3.49
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "order_number": "PO-20251106100000",
  "total_amount": 1721.50
}
```

---

### Inventory Counts

#### `POST /api/v1/inventory/count/start`
Inventur starten.

**Request:**
```json
{
  "notes": "Monats-Inventur November 2025"
}
```

**Response:**
```json
{
  "id": 1,
  "count_number": "IC-20251106120000",
  "start_time": "2025-11-06T12:00:00Z"
}
```

#### `POST /api/v1/inventory/count/submit`
Inventur-Ergebnisse einreichen.

**Query Parameters:**
- `count_id`: ID der Inventur-Session

**Request:**
```json
{
  "items": [
    {
      "product_id": 100,
      "counted_quantity": 48,
      "notes": "2 Einheiten beschädigt"
    },
    {
      "product_id": 101,
      "counted_quantity": 150
    }
  ]
}
```

**Auto-Adjustment:** Bestände werden automatisch auf gezählte Mengen korrigiert. Differenzen werden in `stock_movements` protokolliert.

---

## Anwendungsbeispiele

### Beispiel 1: Wareneingang buchen

```bash
# 1. Lieferung erhalten
POST /api/v1/inventory/stock/adjust
{
  "product_id": 100,
  "quantity": 200,
  "movement_type": "in",
  "unit_cost": 5.99,
  "notes": "Lieferung PO-20251106100000"
}

# 2. Bestand wird automatisch aktualisiert
# 3. Movement wird in Historie gespeichert
```

### Beispiel 2: Automatische Bestellvorschläge

```bash
# 1. Artikel verkaufen (reduziert Bestand)
# 2. System erkennt: Bestand < Reorder Point
# 3. Abrufen der Vorschläge
GET /api/v1/inventory/low-stock

# 4. Purchase Order erstellen für alle low-stock Items
POST /api/v1/inventory/purchase-orders {...}
```

### Beispiel 3: Monats-Inventur

```bash
# 1. Inventur starten
POST /api/v1/inventory/count/start
# Response: count_id = 5

# 2. Mitarbeiter zählen Bestände
# 3. Ergebnisse einreichen
POST /api/v1/inventory/count/submit?count_id=5
{
  "items": [
    {"product_id": 100, "counted_quantity": 48},
    {"product_id": 101, "counted_quantity": 152}
  ]
}

# 4. System:
# - Berechnet Differenzen
# - Passt Bestände an
# - Erstellt Audit-Trail
```

---

## Best Practices

✅ **Reorder Points richtig setzen** - Basierend auf Verkaufsgeschwindigkeit
✅ **Regelmäßige Inventuren** - Mindestens quartalsweise
✅ **Lieferzeiten einplanen** - Lead Time bei Reorder Point berücksichtigen
✅ **Barcode-Scanner nutzen** - Für schnelle Inventur
✅ **Lagerorte pflegen** - Für effiziente Kommissionierung

---

## Integration

### Mit POS-Verkauf
```python
# Bei jedem Verkauf automatisch Bestand reduzieren
@router.post("/sales")
async def create_sale(sale_data: SaleCreate):
    # 1. Verkauf erstellen
    sale = create_sale(sale_data)

    # 2. Bestand reduzieren
    for item in sale.items:
        adjust_stock(
            product_id=item.product_id,
            quantity=item.quantity,
            movement_type="out",
            reference_type="sale",
            reference_id=sale.id
        )

    return sale
```

---

## Lizenzierung

**Standard:** 49€/Monat pro Location
**Enterprise:** Custom Pricing mit API-Integration

---

## Support

📧 dev@stumpf.works
📖 https://docs.stumpf.works/plugins/inventory-management
