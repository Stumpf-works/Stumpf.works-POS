# Employee Time Tracking Plugin

**Kategorie:** `general`
**Version:** 1.0.0
**Autor:** Stumpf.works

## Übersicht

Professionelle Arbeitszeiterfassung mit Stempeluhr-Funktion, Überstunden-Berechnung und Schichtplanung. Für alle Branchen geeignet.

---

## Features

✅ **Clock In/Out** - Digitale Stempeluhr mit PIN-Support
✅ **Break Management** - Pausen erfassen (manuell)
✅ **Overtime Calculation** - Automatische Überstundenberechnung
✅ **Shift Planning** - Schichtpläne erstellen und verwalten
✅ **Time Reports** - Täglich, wöchentlich, monatlich
✅ **Approval Workflow** - Manager-Freigabe für Zeiteinträge
✅ **Rounding** - Zeitrundung (5, 10, 15, 30 Min)
✅ **Export** - CSV-Export für Lohn-Software

---

## Konfiguration

```json
{
  "work_hours_per_day": 8.0,
  "overtime_after_hours": 8.5,
  "auto_break_after_hours": 6.0,
  "break_duration_minutes": 30,
  "round_to_minutes": 15
}
```

---

## API Endpoints

### Clock In/Out

#### `POST /api/v1/time-tracking/clock-in`
Einstempeln.

**Request:**
```json
{
  "employee_id": 123,
  "pin": "1234",
  "notes": "Schicht Kasse"
}
```

**Response:**
```json
{
  "id": 456,
  "employee_id": 123,
  "clock_in": "2025-11-06T08:00:00Z",
  "message": "Clocked in successfully"
}
```

#### `POST /api/v1/time-tracking/clock-out`
Ausstempeln.

**Request:**
```json
{
  "employee_id": 123,
  "pin": "1234",
  "notes": "Schicht beendet"
}
```

**Response:**
```json
{
  "id": 456,
  "employee_id": 123,
  "clock_in": "2025-11-06T08:00:00Z",
  "clock_out": "2025-11-06T17:00:00Z",
  "total_hours": 8.5,
  "regular_hours": 8.5,
  "overtime_hours": 0.0,
  "break_minutes": 30,
  "message": "Clocked out successfully"
}
```

**Automatische Berechnung:**
- Gesamt-Zeit = Clock Out - Clock In - Pausen
- Rundung gemäß Config (z.B. 8:47 → 8:45 bei 15-Min-Rundung)
- Überstunden = Total > Threshold

---

### Break Management

#### `POST /api/v1/time-tracking/break/start`
Pause starten.

**Request:**
```json
{
  "time_entry_id": 456,
  "notes": "Mittagspause"
}
```

#### `POST /api/v1/time-tracking/break/end`
Pause beenden.

**Query Parameters:**
- `time_entry_id`: ID des Zeiteintrags

**Response:**
```json
{
  "id": 789,
  "break_start": "2025-11-06T12:00:00Z",
  "break_end": "2025-11-06T12:30:00Z",
  "duration_minutes": 30,
  "message": "Break ended"
}
```

---

### Current Status

#### `GET /api/v1/time-tracking/current`
Aktuellen Status abrufen.

**Response:**
```json
{
  "status": "clocked_in",
  "time_entry": {
    "id": 456,
    "clock_in": "2025-11-06T08:00:00Z",
    "current_hours": 4.5
  },
  "active_break": null
}
```

**Mögliche Status:**
- `clocked_out` - Nicht eingestempelt
- `clocked_in` - Eingestempelt, arbeitet
- `on_break` - In Pause

---

### Time Entries

#### `GET /api/v1/time-tracking/entries`
Zeiteinträge abrufen.

**Query Parameters:**
- `employee_id` (optional): Filter nach Mitarbeiter
- `start_date` (optional): Von Datum
- `end_date` (optional): Bis Datum

**Response:**
```json
[
  {
    "id": 456,
    "employee_id": 123,
    "employee_name": "Max Mustermann",
    "clock_in": "2025-11-06T08:00:00Z",
    "clock_out": "2025-11-06T17:00:00Z",
    "total_hours": 8.5,
    "regular_hours": 8.5,
    "overtime_hours": 0.0,
    "break_minutes": 30,
    "notes": "Schicht Kasse",
    "is_approved": true,
    "approved_by": 999,
    "approved_at": "2025-11-07T10:00:00Z"
  }
]
```

---

### Shifts

#### `GET /api/v1/time-tracking/shifts`
Schichtpläne abrufen.

**Query Parameters:**
- `employee_id` (optional)
- `start_date` (optional)
- `end_date` (optional)

#### `POST /api/v1/time-tracking/shifts`
Schicht erstellen.

**Request:**
```json
{
  "employee_id": 123,
  "shift_date": "2025-11-07",
  "start_time": "2025-11-07T08:00:00Z",
  "end_time": "2025-11-07T17:00:00Z",
  "shift_type": "morning",
  "notes": "Kassenbereich"
}
```

**Shift Types:**
- `morning` - Frühschicht
- `afternoon` - Mittagsschicht
- `evening` - Spätschicht
- `night` - Nachtschicht

---

### Reports

#### `GET /api/v1/time-tracking/report`
Zeitreport generieren.

**Query Parameters:**
- `employee_id` (optional): Für einen Mitarbeiter
- `start_date` (required): Von
- `end_date` (required): Bis

**Response:**
```json
{
  "period": {
    "start": "2025-11-01",
    "end": "2025-11-30"
  },
  "summary": {
    "total_entries": 20,
    "total_hours": 170.5,
    "regular_hours": 160.0,
    "overtime_hours": 10.5
  },
  "entries": [
    {
      "date": "2025-11-06",
      "clock_in": "2025-11-06T08:00:00Z",
      "clock_out": "2025-11-06T17:00:00Z",
      "total_hours": 8.5,
      "overtime_hours": 0.5
    }
  ]
}
```

---

## Anwendungsbeispiele

### Beispiel 1: Normaler Arbeitstag

```bash
# 08:00 - Mitarbeiter kommt
POST /api/v1/time-tracking/clock-in
{
  "employee_id": 123,
  "pin": "1234"
}

# 12:00 - Pause Start
POST /api/v1/time-tracking/break/start
{
  "time_entry_id": 456
}

# 12:30 - Pause Ende
POST /api/v1/time-tracking/break/end?time_entry_id=456

# 17:00 - Feierabend
POST /api/v1/time-tracking/clock-out
{
  "employee_id": 123
}
```

### Beispiel 2: Monatsreport für Lohnbuchhaltung

```bash
GET /api/v1/time-tracking/report?start_date=2025-11-01&end_date=2025-11-30

# Export als CSV für DATEV oder andere Lohn-Software
```

### Beispiel 3: Schichtplan für nächste Woche

```bash
# Schichten für alle Mitarbeiter anlegen
POST /api/v1/time-tracking/shifts
{
  "employee_id": 123,
  "shift_date": "2025-11-11",
  "start_time": "2025-11-11T08:00:00Z",
  "end_time": "2025-11-11T17:00:00Z",
  "shift_type": "morning"
}

# Wiederholen für alle Mitarbeiter und Tage
```

---

## Best Practices

✅ **PIN-Codes geheim halten** - 4-stellige PINs pro Mitarbeiter
✅ **Regelmäßige Approvals** - Manager sollte wöchentlich freigeben
✅ **Pausen einhalten** - Gesetzliche Pausenzeiten beachten
✅ **Schichtpläne im Voraus** - Mindestens 2 Wochen vorher planen
✅ **Überstunden tracken** - Für Ausgleich oder Vergütung

---

## Rechtliches (Deutschland)

⚖️ **Arbeitszeitgesetz (ArbZG):**
- Max. 8 Stunden pro Tag (10h bei Ausgleich)
- Nach 6 Stunden: 30 Min Pause (gesetzlich)
- Nach 9 Stunden: 45 Min Pause

⚖️ **Datenschutz (DSGVO):**
- Zeitdaten sind personenbezogen
- Aufbewahrungspflicht: 2 Jahre (Steuern)
- Löschung nach Aufbewahrungsfrist

---

## Integration

### Mit Payroll-Software
```python
# Export für DATEV
report = get_time_report(
    start_date="2025-11-01",
    end_date="2025-11-30"
)
export_to_datev_csv(report)
```

---

## Lizenzierung

**Standard:** 9€/Monat pro Mitarbeiter
**Enterprise:** Custom Pricing

---

## Support

📧 dev@stumpf.works
📖 https://docs.stumpf.works/plugins/employee-time-tracking
