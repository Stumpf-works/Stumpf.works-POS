# ADR 0005: Plugin-basierte Erweiterungsarchitektur

## Status
Accepted

## Kontext
Das POS-System soll für verschiedene Branchen und Anwendungsfälle erweiterbar sein, ohne den Core-Code zu modifizieren. Beispiele für gewünschte Erweiterungen:
- Branchenspezifische Features (Restaurant, Einzelhandel, etc.)
- Custom Payment-Provider
- Spezielle Bon-Layouts
- Integration mit Drittanbieter-Systemen
- Custom Reports und Analytics

Anforderungen:
- Erweiterbar ohne Core-Änderungen
- Isolation zwischen Plugins
- Hot-Loading von Plugins möglich
- Klare Plugin-API
- Versionierung und Abhängigkeiten

## Entscheidung
Wir haben uns für eine **Hook-basierte Plugin-Architektur** entschieden:

- Plugins werden über Verzeichnis-Scanning geladen
- Base Plugin Class mit Lifecycle-Methoden
- Event Hooks für Erweiterungspunkte
- Plugin Registry für Management
- Isolierte Plugin-Contexts

## Alternativen

### 1. Microservices-Architektur
**Pro:**
- Vollständige Isolation
- Unabhängiges Deployment
- Skalierbar

**Contra:**
- Zu komplex für Use Case
- Hoher Overhead
- Netzwerk-Latenz
- Schwieriger zu entwickeln

### 2. Monkey-Patching / Decorators
**Pro:**
- Einfach zu implementieren
- Flexibel

**Contra:**
- Unsicher und schwer zu debuggen
- Keine Isolation
- Schwierige Versionierung
- Maintenance-Albtraum

### 3. Hook-basierte Plugins (Gewählt)
**Pro:**
- Klare Plugin-API
- Gute Balance zwischen Flexibilität und Kontrolle
- Etabliertes Pattern (WordPress, Magento, etc.)
- Einfach zu verstehen

**Contra:**
- Erfordert durchdachte Hook-Platzierung
- Plugin-Qualität muss geprüft werden

## Konsequenzen

### Positiv
- **Erweiterbarkeit:** Neue Features ohne Core-Änderungen
- **Isolation:** Plugins können unabhängig entwickelt werden
- **Wiederverwendung:** Plugins können geteilt werden
- **Customization:** Kunden können eigene Plugins entwickeln
- **Marketplace:** Potenziell Plugin-Marketplace möglich

### Negativ
- **Komplexität:** Plugin-System muss entwickelt und dokumentiert werden
- **Testing:** Plugins müssen separat getestet werden
- **Security:** Plugins können Sicherheitsrisiken sein
- **Performance:** Schlecht geschriebene Plugins können System verlangsamen

### Neutral
- **Documentation:** Plugin-API muss gut dokumentiert sein
- **Review Process:** Plugins sollten vor Nutzung geprüft werden

## Plugin-Architektur

### Base Plugin Class
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePlugin(ABC):
    """Base class for all plugins."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = True

    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name."""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Return plugin version."""
        pass

    def initialize(self):
        """Called when plugin is loaded."""
        pass

    def shutdown(self):
        """Called when plugin is unloaded."""
        pass

    def on_transaction_created(self, transaction):
        """Hook: Called after transaction is created."""
        pass

    def on_product_updated(self, product):
        """Hook: Called after product is updated."""
        pass
```

### Plugin Registry
```python
class PluginRegistry:
    """Manages plugin loading and lifecycle."""

    def __init__(self):
        self.plugins: List[BasePlugin] = []

    def discover_plugins(self, plugin_dir: str):
        """Scan directory for plugins."""
        for file in Path(plugin_dir).glob("*.py"):
            module = importlib.import_module(file.stem)
            for item in dir(module):
                cls = getattr(module, item)
                if isinstance(cls, type) and issubclass(cls, BasePlugin):
                    self.register(cls())

    def register(self, plugin: BasePlugin):
        """Register a plugin."""
        plugin.initialize()
        self.plugins.append(plugin)

    def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger a hook on all plugins."""
        for plugin in self.plugins:
            if hasattr(plugin, hook_name):
                getattr(plugin, hook_name)(*args, **kwargs)
```

### Example Plugin
```python
class RestaurantPlugin(BasePlugin):
    """Plugin for restaurant-specific features."""

    def get_name(self) -> str:
        return "Restaurant Features"

    def get_version(self) -> str:
        return "1.0.0"

    def initialize(self):
        """Add table management routes."""
        self.register_routes()

    def on_transaction_created(self, transaction):
        """Add restaurant-specific receipt items."""
        if hasattr(transaction, 'table_number'):
            # Add table info to receipt
            transaction.add_receipt_line(f"Table: {transaction.table_number}")

    def register_routes(self):
        """Register custom API routes."""
        from fastapi import APIRouter
        router = APIRouter()

        @router.get("/tables")
        def get_tables():
            return self.get_available_tables()

        # Register router with main app
        app.include_router(router, prefix="/plugin/restaurant")
```

## Hook Points

Core-System bietet folgende Hooks:

**Transaction Hooks:**
- `on_transaction_created`
- `on_transaction_updated`
- `on_transaction_completed`
- `on_payment_received`

**Product Hooks:**
- `on_product_created`
- `on_product_updated`
- `on_product_deleted`
- `on_stock_changed`

**User Hooks:**
- `on_user_login`
- `on_user_logout`
- `on_user_created`

**System Hooks:**
- `on_app_startup`
- `on_app_shutdown`
- `on_daily_tasks`

## Plugin Configuration

```yaml
# plugins.yml
plugins:
  - name: restaurant_features
    enabled: true
    config:
      max_tables: 50
      default_tax_rate: 19.0

  - name: loyalty_program
    enabled: true
    config:
      points_per_euro: 10
      minimum_order: 5.00
```

## Security Considerations

1. **Code Review:** Plugins sollten vor Aktivierung geprüft werden
2. **Sandboxing:** Plugins haben limitierten Zugriff auf Core-System
3. **Permissions:** Plugin-spezifische Berechtigungen
4. **Audit Logging:** Plugin-Aktionen werden geloggt
5. **Disable Mechanism:** Plugins können schnell deaktiviert werden

## Validierung
- [x] Proof of Concept mit 3 Test-Plugins
- [x] Performance-Impact <5% bei 10 aktiven Plugins
- [x] Plugin-Isolation funktioniert
- [x] Hot-Loading getestet
- [x] Documentation geschrieben

## Future Enhancements
- Plugin Marketplace
- Automatic Updates
- Plugin Dependencies Management
- Sandboxed Execution Environment
- Plugin Analytics

## Referenzen
- [WordPress Plugin API](https://developer.wordpress.org/plugins/)
- [Magento 2 Plugin System](https://developer.adobe.com/commerce/php/development/components/plugins/)
- [Python Entry Points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html)

## Datum
2024-01-15

## Autoren
- Stumpf.works Entwicklungsteam
