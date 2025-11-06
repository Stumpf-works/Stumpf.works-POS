# Loyalty Program Plugin

**Kategorie:** `marketing`
**Version:** 1.0.0
**Autor:** Stumpf.works

## Übersicht

Vollständiges Kundenbindungsprogramm mit Punktesystem, Tier-System und Kampagnen-Management. Steigern Sie Kundenloyalität und Wiederkaufsrate.

---

## Features

✅ **Points System** - Punkte sammeln und einlösen
✅ **4-Tier System** - Bronze, Silber, Gold, Platin
✅ **QR-Codes** - Digitale Kundenkarten
✅ **Campaigns** - Doppelte Punkte, Bonus-Aktionen
✅ **Rewards Catalog** - Einlösbare Prämien
✅ **Birthday Bonus** - Automatische Geburtstagsgeschenke
✅ **Welcome Bonus** - 50 Punkte bei Anmeldung
✅ **Points Expiry** - Konfigurierbar (0 = nie)

---

## Konfiguration

```json
{
  "points_per_euro": 10,
  "enable_tiers": true,
  "birthday_bonus_points": 100,
  "points_expiry_months": 12,
  "redemption_rate": 100
}
```

**Tier-Multiplikatoren:**
- Bronze: 1.0x (0-1.999 Lifetime Points)
- Silber: 1.2x (2.000-4.999 Lifetime Points)
- Gold: 1.5x (5.000-9.999 Lifetime Points)
- Platin: 2.0x (10.000+ Lifetime Points)

---

## API Endpoints

### Customer Management

#### `POST /api/v1/loyalty/customers`
Kunden registrieren.

**Request:**
```json
{
  "customer_name": "Anna Schmidt",
  "email": "anna@example.com",
  "phone": "+49 171 1234567",
  "date_of_birth": "1990-05-15",
  "notes": "Stammkundin seit 2020"
}
```

**Response:**
```json
{
  "id": 1,
  "card_number": "LC-20251106120000",
  "qr_code": "LOYALTY:tenant123:LC-20251106120000",
  "welcome_bonus": 50
}
```

**Auto-Features:**
- Kartennummer wird automatisch generiert
- QR-Code für App-Scan
- 50 Willkommens-Punkte

#### `GET /api/v1/loyalty/customers/{customer_id}`
Kundeninfo und Punktestand.

**Response:**
```json
{
  "id": 1,
  "customer_name": "Anna Schmidt",
  "email": "anna@example.com",
  "phone": "+49 171 1234567",
  "card_number": "LC-20251106120000",
  "qr_code": "LOYALTY:tenant123:LC-20251106120000",
  "points_balance": 2450,
  "lifetime_points": 5680,
  "tier": "gold",
  "date_of_birth": "1990-05-15",
  "enrollment_date": "2025-01-15T10:00:00Z",
  "last_activity": "2025-11-06T14:30:00Z",
  "is_active": true
}
```

---

### Points Management

#### `POST /api/v1/loyalty/earn`
Punkte sammeln (bei Einkauf).

**Request:**
```json
{
  "customer_id": 1,
  "amount_spent": 50.00,
  "reference_id": 12345
}
```

**Response:**
```json
{
  "customer_id": 1,
  "points_earned": 750,
  "points_balance": 3200,
  "tier": "gold"
}
```

**Berechnung:**
```
Basis: 50€ × 10 Punkte = 500 Punkte
Gold-Tier Multiplikator: 500 × 1.5 = 750 Punkte
Kampagne (falls aktiv): 750 × 2 = 1500 Punkte
```

#### `POST /api/v1/loyalty/redeem`
Punkte einlösen.

**Request:**
```json
{
  "customer_id": 1,
  "points": 1000,
  "reward_id": 5,
  "description": "10€ Rabatt-Gutschein"
}
```

**Response:**
```json
{
  "customer_id": 1,
  "points_redeemed": 1000,
  "points_balance": 2200,
  "discount_value": 10.00
}
```

**Redemption Rate:** 100 Punkte = 1€ Wert (konfigurierbar)

---

### Transaction History

#### `GET /api/v1/loyalty/history`
Punkte-Historie.

**Query Parameters:**
- `customer_id` (required)
- `limit` (default: 50)

**Response:**
```json
[
  {
    "id": 123,
    "customer_id": 1,
    "transaction_type": "earn",
    "points": 750,
    "points_before": 2450,
    "points_after": 3200,
    "reference_type": "sale",
    "reference_id": 12345,
    "amount_spent": 50.00,
    "description": "Purchase: 50.0€",
    "created_at": "2025-11-06T14:30:00Z"
  }
]
```

---

### Rewards Catalog

#### `GET /api/v1/loyalty/rewards`
Verfügbare Prämien.

**Response:**
```json
[
  {
    "id": 1,
    "reward_name": "5€ Rabatt-Gutschein",
    "description": "Einlösbar bei nächstem Einkauf ab 20€",
    "points_required": 500,
    "reward_type": "discount",
    "reward_value": 5.00,
    "is_active": true
  },
  {
    "id": 2,
    "reward_name": "Gratis Kaffee",
    "description": "Ein Kaffee Ihrer Wahl",
    "points_required": 200,
    "reward_type": "product",
    "reward_value": 3.50,
    "is_active": true
  }
]
```

---

### Campaigns

#### `POST /api/v1/loyalty/campaigns`
Kampagne erstellen.

**Request:**
```json
{
  "campaign_name": "Weekend Double Points",
  "description": "Doppelte Punkte am Wochenende",
  "campaign_type": "double_points",
  "points_multiplier": 2.0,
  "start_date": "2025-11-08T00:00:00Z",
  "end_date": "2025-11-10T23:59:59Z",
  "target_tier": null,
  "min_purchase_amount": null
}
```

**Campaign Types:**
- `double_points` - Punkte-Multiplikator (z.B. 2x, 3x)
- `bonus_points` - Fixe Bonus-Punkte (z.B. +100 Punkte)

---

### Tiers

#### `GET /api/v1/loyalty/tiers`
Tier-Übersicht.

**Response:**
```json
[
  {
    "tier_name": "bronze",
    "min_points": 0,
    "points_multiplier": 1.0,
    "discount_percentage": 0,
    "description": "Willkommen!"
  },
  {
    "tier_name": "silver",
    "min_points": 2000,
    "points_multiplier": 1.2,
    "discount_percentage": 5
  },
  {
    "tier_name": "gold",
    "min_points": 5000,
    "points_multiplier": 1.5,
    "discount_percentage": 10
  },
  {
    "tier_name": "platinum",
    "min_points": 10000,
    "points_multiplier": 2.0,
    "discount_percentage": 15
  }
]
```

---

## Anwendungsbeispiele

### Beispiel 1: Kunde registrieren an der Kasse

```bash
# 1. Kunde möchte mitmachen
POST /api/v1/loyalty/customers
{
  "customer_name": "Max Müller",
  "phone": "+49 171 9876543",
  "email": "max@example.com"
}

# Response: Karten-Nr. + 50 Welcome-Punkte
# Karte ausdrucken oder QR-Code zeigen
```

### Beispiel 2: Punkte sammeln bei jedem Kauf

```bash
# Kunde kauft für 75€
POST /api/v1/loyalty/earn
{
  "customer_id": 1,
  "amount_spent": 75.00,
  "reference_id": 98765
}

# Response: +1125 Punkte (Gold-Tier 1.5x)
# Neuer Punktestand: 3325
```

### Beispiel 3: Punkte einlösen

```bash
# Kunde möchte 10€ Rabatt
POST /api/v1/loyalty/redeem
{
  "customer_id": 1,
  "points": 1000,
  "reward_id": 3,
  "description": "10€ Rabatt"
}

# POS-System: Rabatt wird abgezogen
# Response: -1000 Punkte, 10€ Discount
```

### Beispiel 4: Weekend-Kampagne

```bash
# Freitag-Mittag: Kampagne aktivieren
POST /api/v1/loyalty/campaigns
{
  "campaign_name": "Wochenend-Aktion",
  "campaign_type": "double_points",
  "points_multiplier": 2.0,
  "start_date": "2025-11-08T00:00:00Z",
  "end_date": "2025-11-10T23:59:59Z"
}

# Samstag/Sonntag: Alle Kunden bekommen 2x Punkte
# Montag: Kampagne endet automatisch
```

---

## Best Practices

✅ **Tier-Schwellen realistisch** - Basierend auf durchschnittlichem Kaufverhalten
✅ **Regelmäßige Kampagnen** - Hält Programm interessant
✅ **Birthday-Bonus nutzen** - Persönliche Note
✅ **Points-Expiry kommunizieren** - Transparenz schafft Vertrauen
✅ **Rewards attraktiv gestalten** - Wert muss spürbar sein

---

## Marketing-Tipps

🎯 **Onboarding:**
- Willkommens-Email mit Erklärung
- Erste Punkte = erste Motivation
- QR-Code in Geldbeutel-App

🎯 **Engagement:**
- SMS bei Punkte-Änderung
- Email bei Tier-Upgrade
- Push-Notification bei Kampagnen

🎯 **Retention:**
- Punkte-Expiry-Warnung (30 Tage vorher)
- Exklusive Tier-Benefits (Gold = VIP-Events)
- Gamification (Badges, Challenges)

---

## ROI-Berechnung

**Beispiel-Szenario:**
- 1000 aktive Mitglieder
- Durchschnitt 5 Käufe/Jahr mehr pro Mitglied
- Durchschnittlicher Warenkorbwert: 40€
- **Zusatzumsatz: 200.000€/Jahr**

**Kosten:**
- Plugin-Lizenz: 39€/Monat = 468€/Jahr
- Prämien (2% vom Umsatz): 4.000€/Jahr
- **Total: 4.468€/Jahr**

**ROI: 4.378% 🚀**

---

## Integration

### Mit POS-Checkout
```javascript
// 1. Kundenkarte scannen
const customer = await loyaltyAPI.getCustomer(cardNumber);

// 2. Punktestand anzeigen
showPointsBalance(customer.points_balance);

// 3. Nach Zahlung: Punkte gutschreiben
await loyaltyAPI.earnPoints({
  customer_id: customer.id,
  amount_spent: totalAmount
});

// 4. Einlösen anbieten (falls genug Punkte)
if (customer.points_balance >= 1000) {
  offerRedemption();
}
```

---

## Lizenzierung

**Standard:** 39€/Monat
**Enterprise:** Custom mit White-Label-App

---

## Support

📧 dev@stumpf.works
📖 https://docs.stumpf.works/plugins/loyalty-program
