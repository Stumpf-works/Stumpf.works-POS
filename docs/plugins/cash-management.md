# Cash Management Plugin

**Kategorie:** `general`
**Version:** 1.0.0
**Autor:** Stumpf.works

## Übersicht

Professionelle Kassenverwaltung mit Kassenbuch, Kassensturz und Z-Bericht. Für alle Branchen mit Bargeldumsätzen. DSGVO- und finanzamtkonform.

---

## Features

✅ **Cash Register Balance** - Kassenstand in Echtzeit
✅ **Deposits & Withdrawals** - Ein- und Auszahlungen
✅ **Cash Counts** - Kassensturz (Soll vs. Ist)
✅ **Denominations** - Münz/Schein-Zählung
✅ **Safe Management** - Tresor-Einzahlungen
✅ **Z-Report** - Tagesabschluss
✅ **Transaction History** - Vollständige Historie
✅ **Difference Tracking** - Differenzen tracken

---

## Konfiguration

```json
{
  "starting_float": 200.0,
  "max_cash_limit": 1000.0,
  "safe_deposit_threshold": 800.0,
  "enable_denomination_tracking": true,
  "require_manager_approval": false
}
```

---

## API Endpoints

### Balance

#### `GET /api/v1/cash/balance`
Aktueller Kassenstand.

**Query Parameters:**
- `register_id` (optional): Für eine bestimmte Kasse

**Response (single register):**
```json
{
  "register_id": 1,
  "register_name": "Hauptkasse",
  "current_balance": 543.50,
  "starting_float": 200.00,
  "status": "open"
}
```

**Response (all registers):**
```json
{
  "registers": [
    {
      "id": 1,
      "register_name": "Hauptkasse",
      "current_balance": 543.50
    },
    {
      "id": 2,
      "register_name": "Kasse 2",
      "current_balance": 312.75
    }
  ],
  "total_balance": 856.25
}
```

---

### Transactions

#### `POST /api/v1/cash/deposit`
Einzahlung tätigen.

**Request:**
```json
{
  "register_id": 1,
  "amount": 100.00,
  "notes": "Wechselgeld auffüllen"
}
```

**Response:**
```json
{
  "register_id": 1,
  "amount": 100.00,
  "balance_before": 543.50,
  "balance_after": 643.50,
  "message": "Cash deposited successfully"
}
```

#### `POST /api/v1/cash/withdrawal`
Entnahme tätigen.

**Request:**
```json
{
  "register_id": 1,
  "amount": 200.00,
  "description": "Bank-Einzahlung vorbereiten"
}
```

**Response:**
```json
{
  "register_id": 1,
  "amount": 200.00,
  "balance_before": 643.50,
  "balance_after": 443.50,
  "message": "Cash withdrawn successfully"
}
```

**Error Handling:**
```json
{
  "detail": "Insufficient cash in register"
}
```

#### `GET /api/v1/cash/transactions`
Transaktions-Historie.

**Query Parameters:**
- `register_id` (optional)
- `start_date` (optional)
- `end_date` (optional)
- `limit` (default: 100)

**Response:**
```json
[
  {
    "id": 123,
    "register_id": 1,
    "transaction_type": "deposit",
    "amount": 100.00,
    "balance_before": 543.50,
    "balance_after": 643.50,
    "reference_type": "manual",
    "description": "Wechselgeld auffüllen",
    "created_at": "2025-11-06T14:30:00Z"
  }
]
```

---

### Cash Count

#### `POST /api/v1/cash/count`
Kassensturz durchführen.

**Request:**
```json
{
  "register_id": 1,
  "count_type": "closing",
  "counted_amount": 442.75,
  "denominations": [
    {"type": "bill", "value": 50.00, "quantity": 5},
    {"type": "bill", "value": 20.00, "quantity": 5},
    {"type": "bill", "value": 10.00, "quantity": 4},
    {"type": "bill", "value": 5.00, "quantity": 1},
    {"type": "coin", "value": 2.00, "quantity": 1},
    {"type": "coin", "value": 0.50, "quantity": 1},
    {"type": "coin", "value": 0.20, "quantity": 1},
    {"type": "coin", "value": 0.05, "quantity": 1}
  ],
  "notes": "Tagesabschluss"
}
```

**Response:**
```json
{
  "count_id": 456,
  "register_id": 1,
  "expected_amount": 443.50,
  "counted_amount": 442.75,
  "difference": -0.75,
  "message": "Cash count completed"
}
```

**Count Types:**
- `opening` - Kassenöffnung
- `closing` - Kassenschließung
- `intermediate` - Zwischenzählung

**Auto-Adjustment:** Wenn Differenz vorhanden, wird Kassenstand automatisch korrigiert.

---

### Z-Report

#### `GET /api/v1/cash/z-report`
Tagesabschluss-Bericht.

**Query Parameters:**
- `register_id` (required)
- `date` (optional, default: heute)

**Response:**
```json
{
  "register_id": 1,
  "register_name": "Hauptkasse",
  "report_date": "2025-11-06",
  "starting_balance": 200.00,
  "ending_balance": 442.75,
  "summary": {
    "total_transactions": 45,
    "total_deposits": 300.00,
    "total_withdrawals": 200.00,
    "total_sales": 1142.75,
    "net_change": 242.75
  },
  "cash_counts": [
    {
      "count_type": "opening",
      "expected": 200.00,
      "counted": 200.00,
      "difference": 0.00,
      "time": "2025-11-06T08:00:00Z"
    },
    {
      "count_type": "closing",
      "expected": 443.50,
      "counted": 442.75,
      "difference": -0.75,
      "time": "2025-11-06T20:00:00Z"
    }
  ]
}
```

**Rechtliches:** Z-Bericht muss für Finanzamt 10 Jahre aufbewahrt werden!

---

### Safe Deposit

#### `POST /api/v1/cash/safe-deposit`
Tresor-Einzahlung.

**Request:**
```json
{
  "register_id": 1,
  "amount": 500.00,
  "deposit_type": "safe",
  "notes": "Tageseinnahmen sichern"
}
```

**Response:**
```json
{
  "deposit_id": 789,
  "amount": 500.00,
  "balance_after": 142.75,
  "message": "Safe deposit completed"
}
```

**Auto-Deposit:** Wenn `current_balance > safe_deposit_threshold`, wird automatisch vorgeschlagen.

---

### Denominations

#### `GET /api/v1/cash/denominations`
Münz/Schein-Aufschlüsselung einer Zählung.

**Query Parameters:**
- `count_id` (required)

**Response:**
```json
{
  "count_id": 456,
  "denominations": [
    {"type": "bill", "value": 50.00, "quantity": 5, "total": 250.00},
    {"type": "bill", "value": 20.00, "quantity": 5, "total": 100.00},
    {"type": "bill", "value": 10.00, "quantity": 4, "total": 40.00},
    {"type": "bill", "value": 5.00, "quantity": 1, "total": 5.00},
    {"type": "coin", "value": 2.00, "quantity": 1, "total": 2.00},
    {"type": "coin", "value": 0.50, "quantity": 1, "total": 0.50},
    {"type": "coin", "value": 0.20, "quantity": 1, "total": 0.20},
    {"type": "coin", "value": 0.05, "quantity": 1, "total": 0.05}
  ],
  "total": 397.75
}
```

---

## Anwendungsbeispiele

### Beispiel 1: Tagesablauf

```bash
# 08:00 - Kasse öffnen
POST /api/v1/cash/deposit
{
  "register_id": 1,
  "amount": 200.00,
  "notes": "Wechselgeld Kassenöffnung"
}

# 08:05 - Opening Count
POST /api/v1/cash/count
{
  "register_id": 1,
  "count_type": "opening",
  "counted_amount": 200.00
}

# 08:00 - 20:00: Normale Geschäftstätigkeit
# (Verkäufe werden automatisch gebucht)

# 20:00 - Closing Count
POST /api/v1/cash/count
{
  "register_id": 1,
  "count_type": "closing",
  "counted_amount": 1342.75,
  "denominations": [...]
}

# 20:10 - Z-Bericht abrufen
GET /api/v1/cash/z-report?register_id=1&date=2025-11-06
```

### Beispiel 2: Zwischensturz bei Schichtwechsel

```bash
# 14:00 - Schicht 1 endet
POST /api/v1/cash/count
{
  "register_id": 1,
  "count_type": "intermediate",
  "counted_amount": 745.50
}

# Manager prüft Differenz
# Falls OK: Schicht 2 übernimmt
```

### Beispiel 3: Tresor-Einzahlung bei hohem Bargeld

```bash
# Kassenstand: 950€ (über Threshold 800€)
# System schlägt vor: Safe Deposit

POST /api/v1/cash/safe-deposit
{
  "register_id": 1,
  "amount": 500.00,
  "deposit_type": "safe"
}

# Kassenstand: 450€ (sicherer Bereich)
```

---

## Best Practices

✅ **Opening Count** - Immer Startzählung machen
✅ **Closing Count** - Täglich Abschlusszählung
✅ **Differenzen dokumentieren** - Im Notizen-Feld
✅ **Safe Deposits** - Bei hohen Beträgen (Versicherung!)
✅ **Z-Bericht archivieren** - 10 Jahre Aufbewahrungspflicht

---

## Rechtliches (Deutschland)

### Finanzamt-Anforderungen

⚖️ **Kassensicherungsverordnung (KassenSichV):**
- TSE-Signierung erforderlich (separate Integration)
- Z-Berichte müssen 10 Jahre aufbewahrt werden
- Manipulationssichere Speicherung

⚖️ **GoBD-Konformität:**
- Vollständigkeit (alle Transaktionen)
- Unveränderlichkeit (Read-Only nach Speicherung)
- Nachvollziehbarkeit (Audit-Trail)
- Zeitnähe (Tagesabschluss)

### Empfohlene Dokumentation

```
docs/
├── z-reports/
│   ├── 2025-11-06.pdf
│   ├── 2025-11-07.pdf
│   └── ...
├── cash-counts/
│   └── 2025-11/
│       ├── opening-2025-11-06.pdf
│       └── closing-2025-11-06.pdf
└── audits/
    └── 2025-Q4-audit.pdf
```

---

## Integration

### Mit POS-System
```python
# Bei Bargeld-Zahlung
@router.post("/sales/checkout")
async def checkout(payment: PaymentData):
    if payment.method == "cash":
        # 1. Verkauf buchen
        sale = create_sale(payment)

        # 2. Kassenbuch-Eintrag
        await cash_management.add_transaction(
            register_id=payment.register_id,
            transaction_type="sale",
            amount=payment.amount,
            reference_type="sale",
            reference_id=sale.id
        )

        # 3. Prüfen ob Safe Deposit nötig
        balance = await cash_management.get_balance(payment.register_id)
        if balance > 800.00:
            notify_manager("Safe deposit recommended")

    return sale
```

---

## Fehlerbehandlung

### Häufige Fehler

**`400 Insufficient cash`** - Nicht genug Bargeld für Entnahme
```json
{
  "detail": "Insufficient cash in register",
  "current_balance": 150.00,
  "requested_amount": 200.00
}
```

**`404 Register not found`** - Kasse existiert nicht
```json
{
  "detail": "Register not found"
}
```

---

## Security

### Zugriffsrechte

| Rolle | Deposit | Withdrawal | Count | Z-Report | Safe |
|-------|---------|------------|-------|----------|------|
| Cashier | ✅ | ❌ | ✅ | ❌ | ❌ |
| Shift Leader | ✅ | ✅ | ✅ | ✅ | ❌ |
| Manager | ✅ | ✅ | ✅ | ✅ | ✅ |

### Audit-Log

Alle Cash-Transaktionen werden geloggt:
- Wer? (User ID)
- Wann? (Timestamp)
- Was? (Transaction Type)
- Wie viel? (Amount)
- Referenz? (Sale ID, Count ID, etc.)

---

## Performance-Tipps

### Caching
```javascript
// Kassenstand cachen (5 Min)
const balance = useCachedQuery('cash-balance', {
  staleTime: 300000
});
```

### Batch-Updates
```python
# Bei vielen Verkäufen: Batch-Update
transactions = []
for sale in sales_batch:
    transactions.append({
        "type": "sale",
        "amount": sale.amount
    })

bulk_add_transactions(transactions)
```

---

## Lizenzierung

**Standard:** 19€/Monat pro Kasse
**Enterprise:** Custom mit Multi-Location

**Hinweis:** TSE-Integration separat erforderlich für Deutschland!

---

## Support

📧 dev@stumpf.works
📖 https://docs.stumpf.works/plugins/cash-management

⚠️ **Steuerberatung:** Konsultieren Sie einen Steuerberater für rechtliche Anforderungen in Ihrem Land!
