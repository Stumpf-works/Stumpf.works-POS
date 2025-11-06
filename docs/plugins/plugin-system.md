# Plugin System Documentation

Das Stumpf.works POS Plugin-System ermöglicht modulare Erweiterungen mit einem zwei-stufigen Lizenz-System.

## Übersicht

### Zwei-stufige Admin-Hierarchie

**1. Super Admin (Stumpf.works Team)**
- Vergibt Plugin-Lizenzen an Tenants
- Verwaltet globale Plugin-Verfügbarkeit
- Kann Trial-Lizenzen erstellen
- Separate Management-Oberfläche

**2. Tenant Admin (Kunden)**
- Sieht nur lizenzierte Plugins
- Kann lizenzierte Plugins aktivieren/deaktivieren
- Kann Plugin-Konfiguration anpassen
- Keine Plugin-Installation ohne Lizenz möglich

---

## Plugin-Architektur

### Plugin-Verzeichnisstruktur

```
backend/app/plugins/
├── __init__.py                    # Plugin-Registry
├── base.py                        # BasePlugin Klasse
├── restaurant/                    # Restaurant-Plugins
│   ├── __init__.py
│   ├── table_management.py
│   └── kitchen_display.py
├── retail/                        # Retail-Plugins
│   ├── __init__.py
│   ├── inventory_tracking.py
│   └── loyalty_program.py
└── hardware/                      # Hardware-Plugins
    ├── __init__.py
    ├── receipt_printer.py
    └── cash_drawer.py
```

### Plugin-Kategorien

| Kategorie | Beschreibung | Icon |
|-----------|--------------|------|
| `restaurant` | Gastronomie-spezifische Features | 🍽️ |
| `retail` | Einzelhandel-Features | 🛒 |
| `pharmacy` | Apotheken-Features | 💊 |
| `bakery` | Bäckerei-Features | 🥖 |
| `hardware` | Hardware-Integration | 🖨️ |
| `payment` | Payment-Provider | 💳 |
| `analytics` | Analytics & Reporting | 📊 |
| `general` | Allgemeine Features | ⚙️ |

---

## Neues Plugin erstellen

### 1. Plugin-Klasse erstellen

```python
# backend/app/plugins/restaurant/table_management.py

from app.plugins.base import BasePlugin
from fastapi import APIRouter
from typing import Optional, List, Dict

class TableManagementPlugin(BasePlugin):
    """
    Plugin für Restaurant-Tischverwaltung.

    Features:
    - Tischpläne erstellen
    - Reservierungen verwalten
    - Tischstatus tracking
    """

    def __init__(self):
        self.name = "table_management"
        self.router = None

    def get_name(self) -> str:
        return self.name

    def get_display_name(self) -> str:
        return "Tischverwaltung"

    def get_description(self) -> str:
        return "Verwalten Sie Tische, Reservierungen und Tischstatus"

    def get_version(self) -> str:
        return "1.0.0"

    def get_author(self) -> str:
        return "Stumpf.works"

    def get_category(self) -> str:
        return "restaurant"

    def get_requires(self) -> List[str]:
        """Abhängigkeiten zu anderen Plugins."""
        return []  # Keine Abhängigkeiten

    def get_config_schema(self) -> Optional[Dict]:
        """JSON-Schema für Plugin-Konfiguration."""
        return {
            "type": "object",
            "properties": {
                "max_tables": {
                    "type": "integer",
                    "default": 50,
                    "description": "Maximale Anzahl Tische"
                },
                "reservation_duration_minutes": {
                    "type": "integer",
                    "default": 120,
                    "description": "Standard-Reservierungsdauer in Minuten"
                },
                "enable_notifications": {
                    "type": "boolean",
                    "default": True,
                    "description": "Benachrichtigungen aktivieren"
                }
            }
        }

    def configure(self, config: Dict):
        """Plugin konfigurieren."""
        self.config = config
        # Validierung durchführen
        max_tables = config.get("max_tables", 50)
        if max_tables < 1 or max_tables > 500:
            raise ValueError("max_tables muss zwischen 1 und 500 liegen")

    async def startup(self):
        """Plugin-Initialisierung beim Start."""
        print(f"[TableManagement] Plugin gestartet")
        # Datenbank-Tabellen erstellen, etc.

    async def shutdown(self):
        """Plugin-Cleanup beim Stoppen."""
        print(f"[TableManagement] Plugin gestoppt")

    def get_router(self) -> Optional[APIRouter]:
        """API-Router für Plugin-Endpoints."""
        if self.router:
            return self.router

        router = APIRouter(prefix="/table-management", tags=["Table Management"])

        @router.get("/tables")
        async def list_tables():
            """Liste alle Tische."""
            return {"tables": []}

        @router.post("/tables")
        async def create_table(table_number: int, seats: int):
            """Erstelle neuen Tisch."""
            return {"table_number": table_number, "seats": seats}

        @router.get("/reservations")
        async def list_reservations():
            """Liste alle Reservierungen."""
            return {"reservations": []}

        self.router = router
        return router
```

### 2. Plugin registrieren

```python
# backend/app/plugins/restaurant/__init__.py

from app.plugins.restaurant.table_management import TableManagementPlugin

__all__ = ["TableManagementPlugin"]
```

### 3. Plugin entdeckbar machen

Das Plugin wird automatisch von der Plugin-Registry entdeckt, wenn es in einem der Plugin-Verzeichnisse liegt.

---

## Plugin-Lizenzierung

### Super Admin: Lizenz vergeben

**API Endpoint:** `POST /api/v1/super-admin/plugin-licenses`

```bash
curl -X POST "https://api.stumpf.works/api/v1/super-admin/plugin-licenses" \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "restaurant_mueller",
    "plugin_name": "table_management",
    "license_type": "standard",
    "valid_days": 365,
    "max_users": null,
    "max_locations": 1,
    "notes": "Jahres-Lizenz für Restaurant Müller"
  }'
```

**Lizenz-Typen:**
- `standard` - Standard-Lizenz (unlimitiert oder zeitlich begrenzt)
- `trial` - Test-Lizenz (meist 30 Tage)
- `enterprise` - Enterprise-Lizenz mit erweiterten Features

### Tenant Admin: Plugin aktivieren

**API Endpoint:** `POST /api/v1/plugins/{plugin_name}/enable`

```bash
curl -X POST "https://api.stumpf.works/api/v1/plugins/table_management/enable" \
  -H "Authorization: Bearer TENANT_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "max_tables": 30,
      "reservation_duration_minutes": 90,
      "enable_notifications": true
    }
  }'
```

**Wichtig:** Tenant Admin kann nur Plugins aktivieren, für die eine gültige Lizenz existiert!

---

## API-Endpunkte

### Super Admin API

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/super-admin/plugin-licenses/tenants` | GET | Liste alle Tenants mit ihren Lizenzen |
| `/api/v1/super-admin/plugin-licenses` | GET | Liste alle Plugin-Lizenzen (mit Filtern) |
| `/api/v1/super-admin/plugin-licenses` | POST | Neue Lizenz vergeben |
| `/api/v1/super-admin/plugin-licenses/{id}` | PATCH | Lizenz aktualisieren |
| `/api/v1/super-admin/plugin-licenses/{id}` | DELETE | Lizenz widerrufen |
| `/api/v1/super-admin/plugin-licenses/{id}/extend` | POST | Lizenz verlängern |

### Tenant Admin API

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/plugins` | GET | Liste lizenzierte Plugins |
| `/api/v1/plugins/{name}` | GET | Plugin-Details |
| `/api/v1/plugins/{name}/enable` | POST | Plugin aktivieren |
| `/api/v1/plugins/{name}/disable` | POST | Plugin deaktivieren |
| `/api/v1/plugins/{name}/config` | PATCH | Plugin konfigurieren |
| `/api/v1/plugins/categories/available` | GET | Verfügbare Kategorien |

---

## Lizenz-Validierung

### Automatische Checks

Das System prüft automatisch:

1. **Bei Plugin-Aktivierung:**
   - Existiert gültige Lizenz?
   - Ist Lizenz noch nicht abgelaufen?
   - Sind Abhängigkeiten erfüllt?

2. **Bei Plugin-Liste:**
   - Nur lizenzierte Plugins werden angezeigt
   - Lizenz-Status wird mitgeliefert (valid, trial, days_remaining)

3. **Bei Lizenz-Ablauf:**
   - Plugin wird automatisch deaktiviert
   - Tenant Admin erhält Warnung
   - Daten bleiben erhalten (nur Plugin ist inaktiv)

### Lizenz-Status-Eigenschaften

```python
class PluginLicense:
    @property
    def is_valid(self) -> bool:
        """Lizenz ist aktiv und nicht abgelaufen."""
        return (
            self.is_active and
            datetime.utcnow() >= self.valid_from and
            (not self.valid_until or datetime.utcnow() <= self.valid_until)
        )

    @property
    def is_trial(self) -> bool:
        """Ist Trial-Lizenz."""
        return self.license_type == "trial"

    @property
    def days_remaining(self) -> Optional[int]:
        """Verbleibende Tage."""
        if not self.valid_until:
            return None
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)
```

---

## Workflow-Beispiele

### Szenario 1: Restaurant bekommt Tischverwaltung

1. **Plugin entwickeln** (Entwickler):
   ```bash
   # Neues Plugin erstellen
   touch backend/app/plugins/restaurant/table_management.py
   # Plugin implementieren (siehe oben)
   ```

2. **Lizenz vergeben** (Super Admin):
   ```bash
   # Via Super Admin UI oder API
   POST /api/v1/super-admin/plugin-licenses
   {
     "tenant_id": "restaurant_mueller",
     "plugin_name": "table_management",
     "license_type": "trial",
     "valid_days": 30
   }
   ```

3. **Plugin aktivieren** (Tenant Admin):
   ```bash
   # Restaurant Müller Admin loggt sich ein
   # Sieht neues Plugin "Tischverwaltung" in Liste
   # Klickt "Aktivieren"
   POST /api/v1/plugins/table_management/enable
   ```

4. **Plugin nutzen** (Restaurant Mitarbeiter):
   ```bash
   # Neue Endpoints sind verfügbar:
   GET /api/v1/table-management/tables
   POST /api/v1/table-management/reservations
   ```

### Szenario 2: Trial-Lizenz verlängern

1. **Kunde kontaktiert Support** (Email):
   > "Hallo, unser Trial für Tischverwaltung läuft in 3 Tagen ab.
   > Wir möchten auf Standard-Lizenz upgraden."

2. **Super Admin verlängert** (Super Admin):
   ```bash
   PATCH /api/v1/super-admin/plugin-licenses/123
   {
     "license_type": "standard",
     "valid_until": null  # Unlimitiert
   }
   ```

3. **Kunde wird benachrichtigt** (Auto-Email):
   > "Ihre Lizenz für 'Tischverwaltung' wurde auf Standard upgraded!"

### Szenario 3: Einzelhandel hat keine Restaurant-Plugins

1. **Einzelhändler loggt sich ein** (Tenant Admin):
   ```bash
   GET /api/v1/plugins
   # Response:
   {
     "plugins": [
       {
         "name": "inventory_tracking",
         "category": "retail",
         "is_licensed": true
       },
       {
         "name": "loyalty_program",
         "category": "retail",
         "is_licensed": true
       }
     ]
   }
   ```

2. **Restaurant-Plugins sind nicht sichtbar**:
   - Keine Lizenz = nicht in Liste
   - Kunde sieht nur relevante Plugins
   - Übersichtliche UI

---

## Plugin-Development Best Practices

### 1. Namenskonventionen

```
Plugin-Name: snake_case
Display Name: Title Case
Category: lowercase
```

### 2. Versionierung

Verwenden Sie Semantic Versioning:
- **1.0.0** - Initial Release
- **1.1.0** - Neue Features (backwards-compatible)
- **1.0.1** - Bugfixes
- **2.0.0** - Breaking Changes

### 3. Abhängigkeiten

```python
def get_requires(self) -> List[str]:
    return ["base_plugin", "other_plugin"]
```

System prüft automatisch, dass Required-Plugins aktiviert sind.

### 4. Konfiguration

Verwenden Sie JSON-Schema für Typ-Sicherheit:

```python
def get_config_schema(self) -> Dict:
    return {
        "type": "object",
        "properties": {
            "setting_name": {
                "type": "string|integer|boolean",
                "default": "default_value",
                "description": "Was macht diese Einstellung?"
            }
        },
        "required": ["required_setting"]
    }
```

### 5. API-Routen

Verwenden Sie eindeutige Präfixe:

```python
router = APIRouter(
    prefix="/table-management",  # Eindeutig!
    tags=["Table Management"]
)
```

### 6. Fehlerbehandlung

```python
async def startup(self):
    try:
        # Initialisierung
        await self.init_database()
    except Exception as e:
        logger.error(f"Plugin startup failed: {e}")
        raise  # Plugin wird nicht geladen
```

---

## Migration & Deployment

### 1. Database Migration

Wenn Plugin neue Tabellen benötigt:

```bash
# Alembic Migration erstellen
cd backend
alembic revision -m "add_table_management_tables"

# Migration implementieren
# alembic/versions/xxx_add_table_management_tables.py

def upgrade():
    op.create_table('plugin_table_management_tables',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(100), nullable=False),
        sa.Column('table_number', sa.Integer(), nullable=False),
        sa.Column('seats', sa.Integer(), nullable=False),
    )

def downgrade():
    op.drop_table('plugin_table_management_tables')
```

### 2. Plugin Deployment

```bash
# 1. Code committen
git add backend/app/plugins/restaurant/table_management.py
git commit -m "feat: Add table management plugin"
git push

# 2. Auf Server deployen
ssh production
cd /app
git pull
sudo systemctl restart pos-api

# 3. Migration ausführen (falls nötig)
alembic upgrade head

# 4. Plugin wird automatisch entdeckt
# (beim nächsten Server-Start)
```

### 3. Plugin aktivieren für ersten Kunden

```bash
# Super Admin Portal öffnen
# https://admin.stumpf.works

# 1. Plugin in Katalog sehen
# 2. "Grant License" klicken
# 3. Tenant auswählen
# 4. Lizenz-Typ wählen (Trial/Standard/Enterprise)
# 5. Bestätigen

# Kunde kann jetzt Plugin aktivieren!
```

---

## Troubleshooting

### Plugin wird nicht entdeckt

**Problem:** Plugin erscheint nicht in Liste

**Lösungen:**
1. Prüfen: Plugin-Klasse erbt von `BasePlugin`
2. Prüfen: Plugin ist in `__init__.py` importiert
3. Prüfen: Plugin-Verzeichnis ist in `app/plugins/`
4. Server neu starten: `systemctl restart pos-api`

### License Check schlägt fehl

**Problem:** Tenant Admin kann Plugin nicht aktivieren

**Lösungen:**
1. Prüfen: Lizenz existiert in DB (`plugin_licenses` Tabelle)
2. Prüfen: `is_active = true`
3. Prüfen: `valid_from` ist in Vergangenheit
4. Prüfen: `valid_until` ist in Zukunft (oder NULL)
5. Prüfen: `tenant_id` stimmt überein

### Plugin-Abhängigkeiten

**Problem:** Plugin kann nicht aktiviert werden wegen Abhängigkeiten

**Lösung:**
1. Prüfen welche Plugins required sind: `plugin.get_requires()`
2. Andere Plugins zuerst aktivieren
3. Oder: Abhängigkeit entfernen (falls nicht nötig)

---

## Security Considerations

### Plugin-Isolation

- Plugins laufen im gleichen Prozess (kein Sandbox)
- **Vorsicht:** Plugins haben vollen Datenbankzugriff
- Nur vertrauenswürdige Plugins installieren
- Code-Review für alle Plugins

### Lizenz-Validierung

- Jede Plugin-Aktion prüft Lizenz
- Expired-Licenses blockieren Zugriff
- Super Admin kann Lizenzen nicht umgehen (good!)

### API-Sicherheit

- Plugin-Endpoints respektieren gleiche Auth wie Haupt-API
- Rate Limiting gilt für alle Endpoints
- CORS-Policy gilt für Plugin-Routen

---

## Zukünftige Erweiterungen

### Geplante Features

1. **Plugin-Marketplace:**
   - Öffentlicher Katalog
   - One-Click-Installation
   - Bewertungen & Reviews

2. **Plugin-Sandboxing:**
   - Isolierte Ausführung
   - Resource Limits (CPU, Memory)
   - Permissions-System

3. **Auto-Updates:**
   - Automatische Plugin-Updates
   - Changelog-Benachrichtigungen
   - Rollback-Funktionalität

4. **Analytics:**
   - Plugin-Usage-Tracking
   - Performance-Metriken
   - Error-Reporting

---

## Support & Kontakt

**Fragen zum Plugin-System?**
- Email: dev@stumpf.works
- Docs: https://docs.stumpf.works/plugins
- GitHub: https://github.com/stumpfworks/pos/issues

**Plugin entwickeln lassen?**
- Custom-Development: sales@stumpf.works
- SLA verfügbar für Enterprise-Kunden
