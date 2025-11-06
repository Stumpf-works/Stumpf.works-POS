# 🧾 Stumpf.works POS
> Cloud-basiertes, modulares und deutsches Kassensystem mit Multi-Tenancy, Cloud-TSE und SumUp-Integration.

## 📘 Übersicht
**Stumpf.works POS** ist ein modernes, modulares Kassensystem (Point of Sale), das speziell für den **deutschen Markt** entwickelt wird.  
Es erfüllt die gesetzlichen Anforderungen nach **GoBD**, **KassenSichV** und **DSFinV-K**, ist **multi-mandantenfähig**, **cloud-basiert** und durch ein **modulares Backend-Design** leicht erweiterbar.

Ziel ist eine Plattform, die mehrere Kunden (Mandanten) parallel verwalten kann – jede Filiale oder Firma mit eigenem Kassenserver, eigenem Cloud-TSE-Zugang und individueller Konfiguration.

---

## 🧱 Architektur
| Ebene | Technologie | Beschreibung |
|-------|--------------|--------------|
| **Backend** | Python **FastAPI**, SQLAlchemy, PostgreSQL | Multi-Tenant Backend mit Schema-Trennung pro Mandant, modularem Plugin-System und REST/WebSocket-API |
| **Frontend** | **React + Vite** | Touch-optimiertes POS-Frontend mit dynamischer Modul-Registry (Lazy Loading) |
| **Queue / Tasks** | Redis + Celery | Asynchrone Verarbeitung (Webhooks, TSE-Transaktionen) |
| **Datenbank** | PostgreSQL | Schema-per-Tenant-Modell |
| **Containerisierung** | Docker / Docker Compose | Einheitliches Deployment, leicht skalierbar |
| **Auth** | OAuth2 + JWT | Multi-Mandanten-fähige Authentifizierung |
| **Zahlungssystem** | SumUp API | Integrierte Zahlungsabwicklung |
| **TSE-Integration** | Cloud-TSE Adapter | Signierungspflichtige Transaktionen |
| **Exports / Reporting** | DSFinV-K / GoBD-konform | Datenexporte für Finanzamt und Steuerprüfung |

---

## 🧩 Kernfunktionen
- ✅ Multi-Tenant-fähiges System (mehrere Firmen / Mandanten parallel)
- ✅ Cloud-TSE-Integration
- ✅ SumUp-Anbindung
- ✅ Modulares Backend-Design
- ✅ DSFinV-K- und GoBD-konformer Export
- ✅ Offline-Funktion
- ✅ Dynamische Frontend-Module
- ✅ Docker-basiertes Deployment & saubere Projektstruktur

---

## 🗂️ Projektstruktur (Clean Repository)
```bash

stumpfworks-pos/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── alembic/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── public/
│   ├── vite.config.js
│   ├── package.json
│   └── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Documentation
├── Entwicklungsplan und Fortschritte 
└── README.md


Clean Code Policy:

Keine Secrets im Code

Alle Module = isoliert, mit eigener Migration

Plugins dürfen nie Core-Files verändern

⚙️ Installation (Dev)
git clone https://github.com/stumpfworks/stumpfworks-pos.git
cd stumpfworks-pos
cp .env.example .env
docker-compose up --build

🔐 Multi-Tenant-Konzept

Mandantentrennung per Header oder Subdomain:
X-Tenant-ID oder mandant.domain.de

💳 SumUp Integration

Mandantenbezogene API-Keys

Webhook → Transaktion → TSE-Signierung → Beleg

🧾 Cloud-TSE-Support

Fiskaly-kompatibel

GoBD-Log & DSFinV-K-Export

🧠 Offline & Sync

IndexedDB Speicherung + automatischer Sync nach Reconnect

🧰 Entwicklerhinweise

Linting: Black / Prettier

Tests: pytest / vitest

CI/CD: GitHub Actions

🧑‍💼 Rechtliches

Nutzung einer zertifizierten Cloud-TSE erforderlich

GoBD + DSGVO beachten

📦 Lizenz

© 2025 stumpf.works — MIT License