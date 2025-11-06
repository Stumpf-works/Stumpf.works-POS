# 🧾 Stumpf.works POS

> Cloud-basiertes, modulares und deutsches Kassensystem mit Multi-Tenancy, Cloud-TSE und SumUp-Integration.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)

## 📘 Übersicht

**Stumpf.works POS** ist ein modernes, modulares Kassensystem (Point of Sale), das speziell für den **deutschen Markt** entwickelt wurde. Es erfüllt die gesetzlichen Anforderungen nach **GoBD**, **KassenSichV** und **DSFinV-K**, ist **multi-mandantenfähig**, **cloud-basiert** und durch ein **modulares Backend-Design** leicht erweiterbar.

### Kernfunktionen

- ✅ **Multi-Tenant-System** - Mehrere Firmen/Mandanten parallel verwalten
- ✅ **Cloud-TSE-Integration** - Fiskaly-kompatible TSE-Signierung
- ✅ **SumUp-Anbindung** - Integrierte Zahlungsabwicklung
- ✅ **Modulares Backend** - Plugin-System für einfache Erweiterungen
- ✅ **DSFinV-K & GoBD** - Konforme Datenexporte
- ✅ **Offline-Funktion** - IndexedDB mit automatischem Sync
- ✅ **Touch-optimiert** - Responsive POS-Oberfläche
- ✅ **Docker-basiert** - Einfaches Deployment

## 🏗️ Architektur

| Komponente | Technologie | Beschreibung |
|------------|-------------|--------------|
| **Backend** | FastAPI + SQLAlchemy | Multi-Tenant REST/WebSocket API |
| **Frontend** | React + Vite | Touch-optimierte POS-Oberfläche |
| **Datenbank** | PostgreSQL | Schema-per-Tenant Isolation |
| **Cache/Queue** | Redis + Celery | Async Task Processing |
| **Auth** | OAuth2 + JWT | Multi-Tenant Authentication |
| **Payment** | SumUp API | Zahlungsintegration |
| **TSE** | Cloud-TSE (Fiskaly) | Signierungspflichtige Transaktionen |
| **Deployment** | Docker Compose | Containerisiertes Setup |

## 🚀 Quick Start

### Voraussetzungen

- Docker & Docker Compose
- Git
- (Optional) Node.js 18+ für lokale Frontend-Entwicklung
- (Optional) Python 3.11+ für lokale Backend-Entwicklung

### Installation

```bash
# Repository klonen
git clone https://github.com/stumpfworks/stumpfworks-pos.git
cd stumpfworks-pos

# Umgebungsvariablen konfigurieren
cp .env.example .env
# Bearbeite .env und setze deine API-Keys

# System starten
docker-compose up --build

# Backend läuft auf: http://localhost:8000
# Frontend läuft auf: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

## 📁 Projektstruktur

```
stumpfworks-pos/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── core/        # Kern-Konfiguration & Settings
│   │   ├── api/         # API Endpoints
│   │   ├── models/      # SQLAlchemy Models
│   │   ├── schemas/     # Pydantic Schemas
│   │   ├── services/    # Business Logic
│   │   ├── plugins/     # Plugin System
│   │   ├── middleware/  # Custom Middleware
│   │   └── utils/       # Helper Functions
│   ├── tests/           # Backend Tests
│   ├── alembic/         # Database Migrations
│   └── requirements.txt
│
├── frontend/            # React + Vite Frontend
│   ├── src/
│   │   ├── components/  # React Components
│   │   ├── pages/       # Page Components
│   │   ├── services/    # API Services
│   │   ├── stores/      # State Management
│   │   ├── hooks/       # Custom React Hooks
│   │   └── utils/       # Helper Functions
│   └── package.json
│
├── docs/                # Dokumentation
│   ├── adr/            # Architecture Decision Records
│   └── api/            # API Dokumentation
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔐 Multi-Tenant Konzept

Mandanten werden über zwei Methoden identifiziert:

1. **HTTP Header**: `X-Tenant-ID: tenant-slug`
2. **Subdomain**: `tenant-slug.yourdomain.com`

Jeder Mandant erhält:
- Eigenes PostgreSQL Schema
- Isolierte Daten
- Eigene SumUp & TSE Konfiguration
- Separate Benutzer & Berechtigungen

## 💳 SumUp Integration

- Mandantenbezogene API-Keys
- Webhook-basierte Zahlungsbestätigung
- Automatische TSE-Signierung nach erfolgreicher Zahlung
- Belegausgabe

## 🧾 Cloud-TSE Support

- Fiskaly-kompatibel
- Automatische Transaktionssignierung
- GoBD-konforme Logging
- DSFinV-K Export

## 🧠 Offline-Modus

- Lokale Speicherung in IndexedDB
- Automatischer Sync bei Wiederverbindung
- Konfliktauflösung
- Queue für ausstehende TSE-Signaturen

## 🧪 Entwicklung

### Backend-Tests

```bash
cd backend
pytest
```

### Frontend-Tests

```bash
cd frontend
npm test
```

### Code-Qualität

```bash
# Backend (Black, isort, mypy)
cd backend
black app/
isort app/
mypy app/

# Frontend (ESLint, Prettier)
cd frontend
npm run lint
npm run format
```

## 📚 Dokumentation

- [API Dokumentation](http://localhost:8000/docs) - Interaktive OpenAPI Docs
- [Architecture Decision Records](./docs/adr/) - Wichtige Architekturentscheidungen
- [Backend README](./backend/README.md) - Backend-spezifische Infos
- [Frontend README](./frontend/README.md) - Frontend-spezifische Infos

## 🛠️ Technologie-Stack

**Backend:**
- FastAPI 0.104+
- SQLAlchemy 2.0
- PostgreSQL 15
- Redis 7
- Celery 5
- Pydantic 2.0
- Alembic

**Frontend:**
- React 18
- Vite 5
- TypeScript 5
- TanStack Query
- Zustand (State)
- TailwindCSS
- Shadcn/ui

**DevOps:**
- Docker & Docker Compose
- GitHub Actions
- pytest & vitest
- Black & Prettier

## 🧑‍💼 Rechtliche Hinweise

⚠️ **Wichtig**: Dieses System erfordert:
- Nutzung einer **zertifizierten Cloud-TSE** (z.B. Fiskaly)
- Einhaltung der **GoBD-Richtlinien**
- Beachtung der **DSGVO** (Datenschutz)
- Registrierung beim zuständigen **Finanzamt**

## 🤝 Beitragen

Contributions sind willkommen! Bitte beachte:
- Keine Secrets im Code committen
- Module sind isoliert mit eigenen Migrationen
- Plugins dürfen nie Core-Files ändern
- Tests für neue Features schreiben
- Code-Style Guidelines befolgen

## 📄 Lizenz

© 2025 stumpf.works - MIT License

Siehe [LICENSE](./LICENSE) für Details.

## 📞 Support

Bei Fragen oder Problemen:
- GitHub Issues: [github.com/stumpfworks/stumpfworks-pos/issues](https://github.com/stumpfworks/stumpfworks-pos/issues)
- Email: support@stumpf.works
- Dokumentation: [docs.stumpf.works](https://docs.stumpf.works)
