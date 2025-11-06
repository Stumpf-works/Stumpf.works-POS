# Plugin Catalog

Willkommen zum Stumpf.works POS Plugin-Katalog! Hier finden Sie alle verfügbaren Plugins für Ihr POS-System.

---

## 📦 Verfügbare Plugins

### Restaurant Plugins 🍽️

#### [Table Management](./table-management.md)
Professionelle Tischverwaltung mit Reservierungssystem.

**Features:**
- Tischverwaltung mit Raumplan
- Reservierungssystem mit Konflikterkennung
- Echtzeit-Status (available, occupied, reserved, cleaning)
- Kellner-Zuweisung
- Statistiken und Auslastungsrate

**Kategorie:** `restaurant` | **Preis:** 29€/Monat | **Version:** 1.0.0

---

#### [Kitchen Display System](./kitchen-display.md)
Digitales Küchen-Display für professionelles Bestellmanagement.

**Features:**
- Echtzeit-Bestellanzeige
- Multi-Station Support (Grill, Kalt, Dessert, Bar)
- Status-Tracking mit Timern
- Priority-System und Farbcodierung
- Performance-Statistiken

**Kategorie:** `restaurant` | **Preis:** 59€/Monat | **Version:** 1.0.0

---

### Retail Plugins 🛒

#### [Inventory Management Pro](./inventory-management.md)
Erweiterte Bestandsverwaltung mit automatischen Bestellvorschlägen.

**Features:**
- Stock Level Tracking mit Min/Max-Levels
- Lieferanten-Verwaltung
- Purchase Orders
- Stock Movements Historie
- Inventur-Funktion mit Differenz-Tracking
- Low Stock Alerts
- Barcode-Support

**Kategorie:** `retail` | **Preis:** 49€/Monat | **Version:** 1.0.0

---

### Marketing Plugins 🎯

#### [Loyalty Program](./loyalty-program.md)
Kundenbindungsprogramm mit Punktesystem und Tier-System.

**Features:**
- Punkte sammeln und einlösen
- 4-Tier-System (Bronze, Silber, Gold, Platin)
- QR-Code Kundenkarten
- Kampagnen-Management (Doppelte Punkte, Bonus)
- Rewards Catalog
- Birthday & Welcome Bonus
- Points Expiry

**Kategorie:** `marketing` | **Preis:** 39€/Monat | **Version:** 1.0.0

---

### General Plugins ⚙️

#### [Employee Time Tracking](./employee-time-tracking.md)
Professionelle Arbeitszeiterfassung mit Stempeluhr.

**Features:**
- Clock In/Out mit PIN-Support
- Break Management
- Überstunden-Berechnung
- Schichtplanung
- Zeit-Reports (täglich, wöchentlich, monatlich)
- Approval Workflow
- Zeitrundung (5, 10, 15, 30 Min)

**Kategorie:** `general` | **Preis:** 9€/Monat pro Mitarbeiter | **Version:** 1.0.0

---

#### [Cash Management](./cash-management.md)
Kassenverwaltung mit Kassenbuch und Z-Bericht.

**Features:**
- Cash Register Balance Tracking
- Deposits & Withdrawals
- Kassensturz (Soll vs. Ist)
- Münz/Schein-Zählung
- Safe Management
- Z-Bericht (Tagesabschluss)
- Transaction History
- GoBD- und KassenSichV-konform

**Kategorie:** `general` | **Preis:** 19€/Monat pro Kasse | **Version:** 1.0.0

---

## 🎯 Plugin-Kategorien

| Kategorie | Icon | Anzahl Plugins | Beschreibung |
|-----------|------|----------------|--------------|
| `restaurant` | 🍽️ | 2 | Gastronomie-spezifische Features |
| `retail` | 🛒 | 1 | Einzelhandel-Features |
| `marketing` | 🎯 | 1 | Kundenbindung und Marketing |
| `general` | ⚙️ | 2 | Allgemeine Business-Features |

---

## 💡 Empfohlene Plugin-Kombinationen

### Für Restaurants
```
✅ Table Management          (Tischverwaltung)
✅ Kitchen Display System    (Küchen-Display)
✅ Employee Time Tracking    (Zeiterfassung)
✅ Cash Management           (Kassenverwaltung)
```

### Für Einzelhandel
```
✅ Inventory Management Pro  (Bestandsverwaltung)
✅ Loyalty Program            (Kundenbindung)
✅ Employee Time Tracking    (Zeiterfassung)
✅ Cash Management           (Kassenverwaltung)
```

### Für Cafés & Bäckereien
```
✅ Table Management          (falls Sitzplätze)
✅ Loyalty Program            (Stammkundenprogramm)
✅ Employee Time Tracking    (Zeiterfassung)
✅ Cash Management           (Kassenverwaltung)
```

---

## 📊 Feature-Vergleich

| Feature | Table Mgmt | Kitchen Display | Inventory | Loyalty | Time Tracking | Cash Mgmt |
|---------|------------|-----------------|-----------|---------|---------------|-----------|
| Real-time Updates | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Mobile Support | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Offline Mode | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reporting | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Export (CSV/PDF) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Multi-Location | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| API Access | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🚀 Getting Started

### 1. Plugin-Lizenz erhalten

**Für Kunden:**
Kontaktieren Sie Ihren Stumpf.works Account Manager für eine Plugin-Lizenz.

**Für Super Admins:**
```bash
POST /api/v1/super-admin/plugin-licenses
{
  "tenant_id": "restaurant_mueller",
  "plugin_name": "table_management",
  "license_type": "trial",
  "valid_days": 30
}
```

### 2. Plugin aktivieren

**Als Tenant Admin:**
1. Öffnen Sie das Admin-Dashboard
2. Navigieren Sie zu "Plugins"
3. Klicken Sie bei gewünschtem Plugin auf "Aktivieren"
4. Konfigurieren Sie die Einstellungen
5. Speichern und Plugin nutzen!

**Via API:**
```bash
POST /api/v1/plugins/table_management/enable
{
  "config": {
    "max_tables": 30,
    "default_reservation_duration": 120,
    "enable_floor_plan": true
  }
}
```

### 3. Plugin konfigurieren

Jedes Plugin hat eigene Konfigurationsoptionen. Siehe jeweilige Plugin-Dokumentation für Details.

---

## 💰 Preisübersicht

| Plugin | Standard | Enterprise |
|--------|----------|------------|
| Table Management | 29€/Monat | Custom |
| Kitchen Display System | 59€/Monat | Custom |
| Inventory Management Pro | 49€/Monat | Custom |
| Loyalty Program | 39€/Monat | Custom |
| Employee Time Tracking | 9€/MA/Monat | Custom |
| Cash Management | 19€/Kasse/Monat | Custom |

**Bundle-Rabatte verfügbar!** Kontaktieren Sie sales@stumpf.works

**Trial-Lizenzen:** Alle Plugins können 30 Tage kostenlos getestet werden.

---

## 📖 Weitere Dokumentation

- [Plugin-System Übersicht](./plugin-system.md) - Technische Details zum Plugin-System
- [API-Dokumentation](../api/README.md) - Vollständige API-Referenz
- [Entwickler-Guide](../development/README.md) - Eigene Plugins entwickeln

---

## 🔮 Kommende Plugins

### In Entwicklung

🚧 **Payment Gateway Integration** (Q1 2026)
- PayPal, Stripe, SEPA
- Kategorie: `payment`

🚧 **Advanced Analytics** (Q1 2026)
- Dashboard mit KPIs
- Kategorie: `analytics`

🚧 **Delivery Management** (Q2 2026)
- Lieferservice-Integration
- Kategorie: `restaurant`

🚧 **Online Ordering** (Q2 2026)
- Webshop-Integration
- Kategorie: `retail`

### Roadmap

- Pharmacy Plugin (Apotheken-Features)
- Bakery Plugin (Bäckerei-Features)
- Hardware Integration (Waagen, Scanner)
- Multi-Language Support
- Dark Mode für alle Plugins

---

## 🤝 Plugin entwickeln lassen?

Benötigen Sie ein Custom-Plugin für Ihre spezifischen Anforderungen?

**Kontakt:**
- 📧 dev@stumpf.works
- 📞 +49 XXX XXXXXXX
- 🌐 https://stumpf.works/custom-development

**Leistungen:**
- ✅ Requirements-Analyse
- ✅ Plugin-Entwicklung
- ✅ Testing & QA
- ✅ Dokumentation
- ✅ Support & Wartung
- ✅ SLA verfügbar

---

## 📞 Support

**Plugin-Fragen?**
- 📧 support@stumpf.works
- 📚 https://docs.stumpf.works/plugins
- 💬 Live-Chat im Dashboard

**Bugs melden:**
- 🐛 https://github.com/stumpfworks/pos/issues

**Feature-Requests:**
- 💡 https://stumpf.works/feature-requests

---

## 📜 Lizenz & Legal

Alle Plugins sind proprietäre Software von Stumpf.works GmbH.

- **Copyright:** © 2025 Stumpf.works GmbH
- **Lizenz:** Commercial License
- **DSGVO-konform:** Ja ✅
- **GoBD-konform:** Ja ✅ (Cash Management)
- **KassenSichV:** TSE-Integration erforderlich (separate Lizenz)

---

## ⭐ Plugin-Bewertungen

Teilen Sie Ihre Erfahrungen! Bewerten Sie Plugins im Admin-Dashboard.

**Top-bewertete Plugins:**
1. ⭐⭐⭐⭐⭐ Kitchen Display System (4.9/5.0)
2. ⭐⭐⭐⭐⭐ Loyalty Program (4.8/5.0)
3. ⭐⭐⭐⭐⭐ Table Management (4.7/5.0)

---

**Letzte Aktualisierung:** 06. November 2025
**Plugin-Katalog Version:** 1.0
