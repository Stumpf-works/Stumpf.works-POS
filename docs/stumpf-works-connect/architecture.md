# Stumpf.Works Connect - Architecture

**Hardware-Client für Stumpf.works POS**

## Übersicht

Stumpf.Works Connect ist eine Clientanwendung, die **lokal beim Kunden läuft** und als Brücke zwischen dem Stumpf.works POS (Cloud/SaaS) und lokaler Hardware (Drucker, Kassenschubladen, Barcode-Scanner, etc.) dient.

### Problem

Cloud-basierte POS-Systeme können nicht direkt auf lokale Hardware zugreifen wegen:
- Browser-Sicherheitsbeschränkungen (kein direkter Zugriff auf USB/COM-Ports)
- Firewalls und Netzwerk-Isolation
- Verschiedene Drucker-Protokolle (ESC/POS, OPOS, etc.)
- Betriebssystem-spezifische Treiber

### Lösung: Stumpf.Works Connect

```
┌──────────────────────────────────────────────────────────────────┐
│                  Stumpf.works POS (Cloud/SaaS)                   │
│                     https://pos.stumpf.works                     │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            │ HTTPS/WebSocket
                            │ (Secure Connection)
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│              Stumpf.Works Connect (Kundenseite)                  │
│              Windows/Linux/macOS Client Application               │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Hardware Abstraction Layer                    │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │  • Printer Manager    • Cash Drawer Manager                │  │
│  │  • Scanner Manager    • Display Manager                    │  │
│  │  • Scale Manager      • Card Reader Manager                │  │
│  └────────────────────────────────────────────────────────────┘  │
└────────┬───────────┬───────────┬──────────┬─────────────────────┘
         │           │           │          │
         │           │           │          │
    ┌────▼───┐  ┌────▼───┐  ┌────▼────┐ ┌──▼──────┐
    │Drucker │  │Kassen- │  │Barcode- │ │Kunden-  │
    │        │  │schublade│  │Scanner  │ │display  │
    └────────┘  └─────────┘  └─────────┘ └─────────┘
```

---

## Hauptfunktionen

### 1. **Hardware-Erkennung & Management**
- Automatisches Erkennen angeschlossener Geräte
- Unterstützung für USB, Seriell (COM), Netzwerk (IP)
- Treiber-Management und Updates
- Gerätekonfiguration (Baudrate, Papiergröße, etc.)

### 2. **Drucker-Integration**
- **Bon-Drucker** (ESC/POS, OPOS, StarPRNT)
  - Quittungen/Belege drucken
  - Küchen-Bon (für Restaurants)
  - Rechnungen
- **Etikettendrucker** (Zebra, Brother, Dymo)
  - Produktetiketten
  - Preisschilder
  - Versandetiketten
- **Format-Support:**
  - 58mm, 80mm Thermodrucker
  - Custom Templates (HTML/CSS → ESC/POS)

### 3. **Kassenschublade**
- Automatisches Öffnen nach Zahlung
- Manuelles Öffnen (mit Berechtigung)
- Status-Überwachung (offen/geschlossen)

### 4. **Barcode-Scanner**
- USB HID Scanner (Plug & Play)
- Seriell/Bluetooth Scanner
- 1D/2D Barcodes (EAN, UPC, QR-Codes)
- Automatische Produktsuche im POS

### 5. **Kundendisplay**
- Preisanzeige für Kunden
- VFD/LCD Displays
- Sekundärer Monitor als Display

### 6. **Waage**
- Artikelwaage für Frischware
- Gewicht → Preis Berechnung
- Integration mit POS-Transaktion

### 7. **Kartenterminal** (Optional)
- Integration lokaler Terminals
- PAX, Verifone, Ingenico
- Zahlungsbestätigung an POS

---

## Technische Architektur

### Technologie-Stack

**Backend (Electron oder Tauri):**
```
┌─────────────────────────────────────┐
│     Stumpf.Works Connect Core      │
│                                     │
│  • Node.js / Rust (Tauri)          │
│  • Hardware Drivers & Managers     │
│  • WebSocket Client                │
│  • Local API Server (REST)         │
│  • SQLite (Local Cache)            │
└─────────────────────────────────────┘
```

**Frontend (React/Vue/Svelte):**
```
┌─────────────────────────────────────┐
│      Connect Control Panel         │
│                                     │
│  • Geräteverwaltung                │
│  • Konfiguration                   │
│  • Status-Dashboard                │
│  • Logs & Fehlerberichte           │
└─────────────────────────────────────┘
```

### Kommunikation mit POS

#### 1. **WebSocket Connection**
```javascript
// Persistente Verbindung zum POS
const ws = new WebSocket('wss://pos.stumpf.works/connect');

ws.on('message', async (message) => {
  const command = JSON.parse(message);

  switch (command.type) {
    case 'PRINT_RECEIPT':
      await printerManager.print(command.data);
      ws.send({ type: 'PRINT_SUCCESS', id: command.id });
      break;

    case 'OPEN_CASH_DRAWER':
      await cashDrawerManager.open();
      ws.send({ type: 'DRAWER_OPENED', id: command.id });
      break;

    case 'GET_DEVICES':
      const devices = await hardwareManager.getDevices();
      ws.send({ type: 'DEVICES_LIST', devices });
      break;
  }
});
```

#### 2. **REST API (Lokal)**
```
GET    http://localhost:9876/api/devices
GET    http://localhost:9876/api/printers
POST   http://localhost:9876/api/print
POST   http://localhost:9876/api/cash-drawer/open
GET    http://localhost:9876/api/status
```

#### 3. **Authentication & Security**
- **Pairing-Prozess:** QR-Code oder Pairing-Code im POS
- **JWT Token:** Für API-Authentifizierung
- **TLS/SSL:** Alle Verbindungen verschlüsselt
- **Lokales Token Storage:** Secure Storage (Keychain/Credential Manager)

---

## Installation & Setup

### Installation (Kunde)

1. **Download:**
   ```
   https://connect.stumpf.works/download
   ├── Windows (64-bit) - StumpfWorksConnect_Setup.exe
   ├── macOS (Intel/Apple Silicon) - StumpfWorksConnect.dmg
   └── Linux (deb/rpm/AppImage) - StumpfWorksConnect.AppImage
   ```

2. **Installation:**
   - Windows: Ausführen von Setup.exe → Auto-Update aktiviert
   - macOS: DMG öffnen → App nach Programme ziehen
   - Linux: AppImage executable machen oder .deb installieren

3. **Auto-Start:**
   - App startet automatisch mit System
   - Läuft im System Tray/Menüleiste
   - Minimale UI für Konfiguration

### Pairing mit POS

```
┌──────────────────────────────────────┐
│    Stumpf.works POS Web-Interface   │
│                                      │
│  Admin → Hardware → Connect Setup    │
│                                      │
│  ┌────────────────────────────────┐ │
│  │    Pairing Code: A4F-892-K3T   │ │
│  │                                 │ │
│  │    ████████████████████         │ │
│  │    ██ ▄▄▄▄▄ █▀▀▄█ ▄▄▄▄▄ ██     │ │
│  │    ██ █   █ █▄ ▄█ █   █ ██     │ │
│  │    ██ █▄▄▄█ █▄▀ █ █▄▄▄█ ██     │ │
│  │    ████████████████████         │ │
│  │          (QR-Code)              │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
         │
         │ User scannt QR oder gibt Code ein
         ▼
┌──────────────────────────────────────┐
│   Stumpf.Works Connect (Lokal)       │
│                                      │
│  Code eingeben: [A4F-892-K3T] ✓     │
│                                      │
│  ✅ Verbunden mit pos.stumpf.works  │
│  ✅ Tenant: Restaurant Müller        │
│                                      │
│  Erkannte Geräte:                    │
│  • Epson TM-T88VI (Drucker)          │
│  • Cash Drawer (COM3)                │
│  • Datalogic Scanner (USB)           │
└──────────────────────────────────────┘
```

---

## Hardware-Abstraktionsschicht

### Printer Manager

```typescript
interface PrinterManager {
  // Discovery
  discoverPrinters(): Promise<Printer[]>;

  // Printing
  print(receipt: Receipt, printer?: string): Promise<void>;
  printRaw(data: Buffer, printer?: string): Promise<void>;

  // Templates
  renderTemplate(template: string, data: any): Promise<Buffer>;

  // Configuration
  setPrinter(name: string, config: PrinterConfig): Promise<void>;
  testPrint(printer: string): Promise<void>;
}

interface Receipt {
  type: 'sale' | 'return' | 'kitchen' | 'label';
  data: {
    items: LineItem[];
    total: number;
    payment: PaymentInfo;
    customer?: CustomerInfo;
  };
  template?: string; // Custom template ID
}

// Beispiel: Bon drucken
await printerManager.print({
  type: 'sale',
  data: {
    items: [
      { name: 'Coca Cola', qty: 2, price: 2.50 },
      { name: 'Sandwich', qty: 1, price: 4.50 }
    ],
    total: 9.50,
    payment: { method: 'cash', amount: 10.00, change: 0.50 }
  }
});
```

### Cash Drawer Manager

```typescript
interface CashDrawerManager {
  // Discovery
  discoverDrawers(): Promise<CashDrawer[]>;

  // Control
  open(drawer?: string, pulse?: number): Promise<void>;

  // Status
  getStatus(drawer: string): Promise<'open' | 'closed'>;
  onStatusChange(callback: (status: string) => void): void;
}

// Beispiel
await cashDrawerManager.open(); // Standard-Pulse (100ms)
await cashDrawerManager.open('COM3', 200); // Custom Pulse
```

### Scanner Manager

```typescript
interface ScannerManager {
  // Discovery
  discoverScanners(): Promise<Scanner[]>;

  // Events
  onScan(callback: (barcode: string) => void): void;

  // Configuration
  setMode(mode: 'continuous' | 'trigger'): void;
  enableSound(enabled: boolean): void;
}

// Beispiel
scannerManager.onScan(async (barcode) => {
  console.log('Scanned:', barcode);

  // Sende an POS zur Produktsuche
  const product = await posAPI.searchProduct(barcode);
  if (product) {
    await posAPI.addToCart(product.id);
  }
});
```

---

## Deployment & Updates

### Auto-Update-Mechanismus

```
┌────────────────────────────────────────┐
│    Stumpf.Works Connect (v1.2.3)       │
│                                        │
│  ✅ Checking for updates...           │
│  📥 Update available: v1.3.0           │
│                                        │
│  Changelog:                            │
│  • Neue Drucker-Unterstützung          │
│  • Bugfix: Kassenschublade             │
│  • Performance-Verbesserungen          │
│                                        │
│  [Update Now]  [Later]  [Auto-Update]  │
└────────────────────────────────────────┘
```

**Update-Server:**
```
https://updates.stumpf.works/connect/
├── latest.yml (Version Info)
├── StumpfWorksConnect-1.3.0-win.exe
├── StumpfWorksConnect-1.3.0-mac.dmg
└── StumpfWorksConnect-1.3.0-linux.AppImage
```

**Electron Auto-Updater:**
```javascript
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-available', () => {
  // Show notification
});

autoUpdater.on('update-downloaded', () => {
  // Prompt user to restart
});
```

---

## Monitoring & Support

### Telemetrie & Error Reporting

```javascript
// Automatische Fehlerberichte (mit User-Consent)
{
  "timestamp": "2025-11-06T15:30:00Z",
  "version": "1.3.0",
  "tenant_id": "restaurant_mueller",
  "error": {
    "type": "PrinterOffline",
    "message": "Printer not responding",
    "device": "Epson TM-T88VI",
    "stack": "..."
  },
  "system": {
    "os": "Windows 11",
    "node": "18.16.0"
  }
}
```

### Remote Support

**Fernwartung (Optional, mit Zustimmung):**
- TeamViewer/AnyDesk Integration
- Remote Logs Download
- Remote Configuration

---

## Sicherheit

### Best Practices

1. **Authentifizierung:**
   - Pairing Code (einmalig, 12 Stunden gültig)
   - JWT Token (refresh nach 7 Tagen)
   - Revokable API Keys

2. **Verschlüsselung:**
   - TLS 1.3 für alle Verbindungen
   - Lokale Datenspeicherung verschlüsselt
   - Keine Klartext-Passwörter

3. **Berechtigungen:**
   - Minimal-Prinzip
   - Nur nötige Hardware-Zugriffe
   - User muss Hardware-Zugriff bestätigen (Windows UAC, macOS Keychain)

4. **Audit Log:**
   - Alle Aktionen geloggt
   - Zugriff auf sensible Operationen (Kassenschublade öffnen)
   - Log-Rotation (30 Tage)

---

## Preismodell & Lizenzierung

### Lizenz-Optionen

1. **Basic (Inkludiert in POS-Lizenz):**
   - 1 Connect-Client pro Standort
   - Standard-Drucker (ESC/POS)
   - Kassenschublade
   - Barcode-Scanner

2. **Professional (+10€/Monat):**
   - Bis zu 5 Connect-Clients
   - Erweiterte Drucker (Zebra, Brother)
   - Kundendisplay
   - Waage
   - Premium Support

3. **Enterprise (Custom):**
   - Unbegrenzte Clients
   - Custom Hardware-Integration
   - SLA-Garantie
   - Dedicated Support

---

## Roadmap

### Phase 1: MVP (Q1 2025)
- ✅ Bon-Drucker (ESC/POS)
- ✅ Kassenschublade
- ✅ Barcode-Scanner (USB HID)
- ✅ Windows Support
- ✅ WebSocket-Verbindung

### Phase 2: Erweiterte Hardware (Q2 2025)
- Etikettendrucker (Zebra)
- Kundendisplay (VFD/LCD)
- Waage-Integration
- macOS Support

### Phase 3: Advanced Features (Q3 2025)
- Linux Support
- Multi-Standort-Management
- Hardware-Templates (Custom Layouts)
- Offline-Modus mit Sync

### Phase 4: Enterprise (Q4 2025)
- Terminal-Integration (PAX, Verifone)
- Selbstbedienungs-Kiosk Modus
- API für Custom Integrationen
- White-Label Option

---

## Technische Anforderungen

### Systemanforderungen

**Minimum:**
- CPU: Dual-Core 1.5 GHz
- RAM: 2 GB
- Speicher: 200 MB
- OS: Windows 10, macOS 10.15, Ubuntu 20.04

**Empfohlen:**
- CPU: Quad-Core 2.0 GHz
- RAM: 4 GB
- Speicher: 500 MB
- SSD für bessere Performance

### Netzwerk

- Internet: Mindestens 1 Mbit/s
- Latenz: <100ms zur Cloud (für Echtzeit-Kommunikation)
- Ports: 9876 (lokal), 443 (HTTPS/WSS)

---

## Entwicklung

### Repository-Struktur

```
stumpf-works-connect/
├── src/
│   ├── main/           # Electron Main Process
│   │   ├── hardware/   # Hardware Managers
│   │   ├── api/        # Local API Server
│   │   ├── websocket/  # POS WebSocket Client
│   │   └── updater/    # Auto-Update Logic
│   ├── renderer/       # Frontend (React)
│   │   ├── pages/      # UI Pages
│   │   └── components/ # React Components
│   └── shared/         # Shared Code
├── drivers/            # Hardware Drivers
├── tests/              # Unit & Integration Tests
├── docs/               # Documentation
└── build/              # Build Configuration
```

### Entwicklungs-Setup

```bash
# Clone Repository
git clone https://github.com/stumpfworks/connect.git
cd connect

# Install Dependencies
npm install

# Development Mode
npm run dev

# Build für Produktion
npm run build:win   # Windows
npm run build:mac   # macOS
npm run build:linux # Linux
```

---

## Support & Dokumentation

**Dokumentation:**
- https://docs.stumpf.works/connect

**Support:**
- Email: support@stumpf.works
- Live-Chat im Admin-Panel
- Community-Forum

**Entwickler:**
- API-Dokumentation: https://api.stumpf.works/connect/docs
- GitHub: https://github.com/stumpfworks/connect
- Discord: https://discord.gg/stumpfworks

---

## Fazit

**Stumpf.Works Connect** ist der Schlüssel für eine vollständige POS-Lösung, die Cloud-Vorteile mit lokaler Hardware-Integration verbindet:

✅ **Einfache Installation** - One-Click Setup
✅ **Hardware-Kompatibilität** - Breite Geräte-Unterstützung
✅ **Sicherheit** - Ende-zu-Ende verschlüsselt
✅ **Zuverlässigkeit** - Auto-Update & Fehlerbehandlung
✅ **Skalierbarkeit** - Von Einzelstandort bis Enterprise
✅ **Support** - Deutsche Dokumentation & Support

**Perfekt für:**
- Restaurants, Cafés, Bars
- Einzelhandel, Boutiquen
- Bäckereien, Metzgereien
- Apotheken
- Jeden, der professionelle POS-Hardware nutzt
