# Table Management Plugin

**Kategorie:** `restaurant`
**Version:** 1.0.0
**Autor:** Stumpf.works

## Übersicht

Das Table Management Plugin ermöglicht die vollständige Verwaltung von Restaurant-Tischen, Reservierungen und Tischstatus. Ideal für Restaurants, Cafés und Bars, die eine professionelle Tischverwaltung benötigen.

---

## Features

### ✅ Tischverwaltung
- Tische anlegen mit Nummer, Name und Sitzplätzen
- Positionierung auf virtuellem Raumplan (X/Y-Koordinaten)
- Tische aktivieren/deaktivieren
- Notizen pro Tisch

### ✅ Reservierungssystem
- Reservierungen mit Kundendaten erstellen
- Zeitslot-Verwaltung mit Konflikterkennung
- Reservierungsstatus (confirmed, seated, completed, cancelled)
- Benachrichtigungen und Erinnerungen

### ✅ Echtzeit-Status
- Tischstatus (available, occupied, reserved, cleaning)
- Kellner-Zuweisung
- Gästeanzahl tracken
- Belegungszeit messen

### ✅ Statistiken
- Auslastungsrate in Echtzeit
- Tagesbelegung
- Umsatz pro Tisch (mit Integration)

---

## Konfiguration

```json
{
  "max_tables": 50,
  "default_reservation_duration": 120,
  "enable_floor_plan": true,
  "enable_waiter_assignment": true
}
```

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `max_tables` | integer | 50 | Maximale Anzahl Tische (1-500) |
| `default_reservation_duration` | integer | 120 | Standard-Reservierungsdauer in Minuten (30-480) |
| `enable_floor_plan` | boolean | true | Raumplan-Visualisierung aktivieren |
| `enable_waiter_assignment` | boolean | true | Kellner-Zuweisung aktivieren |

---

## API Endpoints

### Tische verwalten

#### `GET /api/v1/table-management/tables`
Liste alle Tische mit aktuellem Status.

**Response:**
```json
[
  {
    "id": 1,
    "table_number": 5,
    "table_name": "Fenster Tisch 5",
    "seats": 4,
    "position_x": 100,
    "position_y": 200,
    "is_active": true,
    "status": "occupied",
    "guests_count": 3,
    "assigned_waiter": "Max Mustermann",
    "occupied_since": "2025-11-06T18:30:00Z"
  }
]
```

#### `POST /api/v1/table-management/tables`
Erstelle einen neuen Tisch.

**Request:**
```json
{
  "table_number": 5,
  "table_name": "Fenster Tisch 5",
  "seats": 4,
  "position_x": 100,
  "position_y": 200,
  "notes": "Bevorzugte Position für Stammgäste"
}
```

#### `PATCH /api/v1/table-management/tables/{table_id}`
Aktualisiere Tisch-Einstellungen.

**Request:**
```json
{
  "table_name": "VIP Tisch 5",
  "seats": 6,
  "is_active": true
}
```

#### `PATCH /api/v1/table-management/tables/{table_id}/status`
Ändere Tischstatus.

**Request:**
```json
{
  "status": "occupied",
  "guests_count": 4,
  "assigned_waiter_id": 123,
  "current_order_id": 456
}
```

**Status-Optionen:**
- `available` - Tisch ist frei
- `occupied` - Tisch ist belegt
- `reserved` - Tisch ist reserviert
- `cleaning` - Tisch wird gereinigt

---

### Reservierungen verwalten

#### `GET /api/v1/table-management/reservations`
Liste Reservierungen (optional gefiltert nach Datum).

**Query Parameters:**
- `date` (optional): ISO-Datum (z.B. "2025-11-06")

**Response:**
```json
[
  {
    "id": 1,
    "table_id": 5,
    "table_number": 5,
    "customer_name": "Familie Schmidt",
    "customer_phone": "+49 123 456789",
    "guests_count": 4,
    "reservation_time": "2025-11-06T19:00:00Z",
    "duration_minutes": 120,
    "status": "confirmed",
    "notes": "Hochstuhl benötigt"
  }
]
```

#### `POST /api/v1/table-management/reservations`
Erstelle neue Reservierung.

**Request:**
```json
{
  "table_id": 5,
  "customer_name": "Familie Schmidt",
  "customer_phone": "+49 123 456789",
  "customer_email": "schmidt@example.com",
  "guests_count": 4,
  "reservation_time": "2025-11-06T19:00:00Z",
  "duration_minutes": 120,
  "notes": "Hochstuhl benötigt"
}
```

**Conflict Detection:** Das System prüft automatisch auf Überschneidungen und gibt `409 Conflict` zurück, falls der Tisch bereits reserviert ist.

#### `PATCH /api/v1/table-management/reservations/{reservation_id}/status`
Ändere Reservierungsstatus.

**Query Parameters:**
- `new_status`: `confirmed`, `seated`, `completed`, `cancelled`

**Beispiel:**
```bash
PATCH /api/v1/table-management/reservations/123/status?new_status=seated
```

**Auto-Status-Update:** Wenn Status auf `seated` gesetzt wird, wird der Tischstatus automatisch auf `occupied` aktualisiert.

---

### Statistiken

#### `GET /api/v1/table-management/stats`
Erhalte Restaurant-Statistiken.

**Response:**
```json
{
  "total_tables": 30,
  "tables_by_status": {
    "available": 10,
    "occupied": 15,
    "reserved": 3,
    "cleaning": 2
  },
  "todays_reservations": 12,
  "occupancy_rate": 60.0
}
```

---

## Anwendungsbeispiele

### Beispiel 1: Neuer Gast ohne Reservierung

```bash
# 1. Prüfe verfügbare Tische
GET /api/v1/table-management/tables

# 2. Setze Tisch auf "occupied"
PATCH /api/v1/table-management/tables/5/status
{
  "status": "occupied",
  "guests_count": 2,
  "assigned_waiter_id": 123
}

# 3. Erstelle Bestellung (separates Order-System)
# POST /api/v1/orders {...}
```

### Beispiel 2: Telefonische Reservierung

```bash
# 1. Prüfe Verfügbarkeit für gewünschte Zeit
GET /api/v1/table-management/reservations?date=2025-11-06

# 2. Erstelle Reservierung
POST /api/v1/table-management/reservations
{
  "table_id": 8,
  "customer_name": "Herr Müller",
  "customer_phone": "+49 171 1234567",
  "guests_count": 2,
  "reservation_time": "2025-11-06T20:00:00Z",
  "duration_minutes": 90
}

# 3. Bestätigungs-SMS senden (optional, externes System)
```

### Beispiel 3: Gast kommt zur Reservierung

```bash
# 1. Reservierung suchen
GET /api/v1/table-management/reservations?date=2025-11-06

# 2. Status auf "seated" setzen
PATCH /api/v1/table-management/reservations/123/status?new_status=seated
# -> Tisch wird automatisch auf "occupied" gesetzt

# 3. Bestellung aufnehmen
```

### Beispiel 4: Tagesabschluss

```bash
# 1. Statistiken abrufen
GET /api/v1/table-management/stats

# 2. Alle Tische auf "available" zurücksetzen
# (kann automatisiert werden)
```

---

## Integration mit anderen Modulen

### Mit Order-System
```python
# Beim Erstellen einer Bestellung
order = create_order(...)
# Verknüpfe mit Tisch
update_table_status(
    table_id=5,
    status="occupied",
    current_order_id=order.id
)
```

### Mit POS-Frontend
```javascript
// Raumplan-Visualisierung
const tables = await fetch('/api/v1/table-management/tables');
tables.forEach(table => {
    renderTable(table.position_x, table.position_y, table.status);
});
```

---

## Best Practices

### 1. Reservierungsmanagement
- ✅ Konflikte immer prüfen vor Bestätigung
- ✅ Buffer-Zeit einplanen (z.B. 15 Min zwischen Reservierungen)
- ✅ No-Show-Policy definieren (Auto-Stornierung nach 15 Min)

### 2. Tischstatus
- ✅ Status regelmäßig aktualisieren
- ✅ `cleaning` Status für Hygiene-Tracking nutzen
- ✅ Belegungszeit für Performance-Analyse tracken

### 3. Kellner-Zuweisung
- ✅ Gleichmäßige Verteilung sicherstellen
- ✅ Kellner-Bereiche definieren (z.B. Terrasse, Innenraum)
- ✅ Überlastung vermeiden (max. X Tische pro Kellner)

---

## Fehlerbehandlung

### Häufige Fehler

**`404 Not Found`** - Tisch oder Reservierung existiert nicht
```json
{
  "detail": "Table not found"
}
```

**`409 Conflict`** - Reservierung überschneidet sich
```json
{
  "detail": "Table is already reserved for this time slot"
}
```

**`400 Bad Request`** - Maximale Tischanzahl erreicht
```json
{
  "detail": "Maximum tables limit reached (50)"
}
```

---

## Performance-Tipps

### Caching
```python
# Tisch-Liste cachen (Frontend)
const cachedTables = useQuery('tables', fetchTables, {
    staleTime: 30000  # 30 Sekunden
});
```

### Polling für Echtzeit-Updates
```javascript
// Alle 5 Sekunden Status aktualisieren
setInterval(() => {
    updateTableStatus();
}, 5000);
```

### WebSocket-Alternative (zukünftig)
```javascript
// Real-time Updates per WebSocket
const ws = new WebSocket('ws://api/table-status');
ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    updateTableInUI(update);
};
```

---

## Lizenzierung

**Lizenz-Typ:** Standard / Trial / Enterprise

**Preismodell:**
- Trial: 30 Tage kostenlos
- Standard: 29€/Monat pro Location
- Enterprise: Custom Pricing

**Erforderliche Permissions:**
- Tenant Admin: Kann Tische und Reservierungen verwalten
- Kellner: Kann Status ändern (lesend)
- Hostess: Volle Reservierungsverwaltung

---

## Support

**Fragen?** dev@stumpf.works
**Bugs melden:** https://github.com/stumpfworks/pos/issues
**Dokumentation:** https://docs.stumpf.works/plugins/table-management
