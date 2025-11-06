# ADR 0001: Multi-Tenant Architecture mit PostgreSQL Schema-per-Tenant

## Status
Accepted

## Kontext
Das Stumpf.works POS System soll mehrere unabhängige Organisationen (Mandanten) auf einer gemeinsamen Infrastruktur unterstützen. Jeder Mandant benötigt vollständige Datenisolation und die Möglichkeit, unabhängige Konfigurationen zu haben.

## Entscheidung
Wir haben uns für einen **Schema-per-Tenant** Ansatz mit PostgreSQL entschieden:

- Jeder Mandant erhält ein eigenes PostgreSQL-Schema
- Ein gemeinsames "public" Schema für mandantenübergreifende Daten (z.B. Tenant-Metadaten)
- Tenant-Identifikation via HTTP-Header (`X-Tenant-ID`) oder Subdomain
- PostgreSQL `search_path` wird zur Laufzeit pro Request gesetzt

## Alternativen

### 1. Database-per-Tenant
**Pro:**
- Stärkste Datenisolation
- Einfache Backups pro Mandant
- Unabhängige Skalierung

**Contra:**
- Hoher Verwaltungsaufwand bei vielen Mandanten
- Schwieriger bei Schema-Migrationen
- Höhere Infrastrukturkosten

### 2. Row-Level-Security (RLS)
**Pro:**
- Einfachste Implementierung
- Keine Schema-Verwaltung nötig
- Einfache Queries

**Contra:**
- Risiko von Sicherheitslücken (vergessene WHERE-Klauseln)
- Performance-Overhead bei großen Datenmengen
- Schwierigere Datentrennung

### 3. Schema-per-Tenant (Gewählt)
**Pro:**
- Gute Balance zwischen Isolation und Verwaltbarkeit
- Klare Datentrennung auf Datenbankebene
- Moderate Komplexität
- Gute Performance

**Contra:**
- Mittlerer Verwaltungsaufwand
- Limitierung durch maximale Anzahl von Schemas
- Schema-Migrationen müssen für alle Tenants laufen

## Konsequenzen

### Positiv
- **Datenisolation:** Physische Trennung auf Schema-Ebene
- **Sicherheit:** Versehentlicher Zugriff auf falsche Daten ist unmöglich
- **Compliance:** Einfachere DSGVO-konforme Datenlöschung
- **Performance:** Keine Row-Level-Checks bei Queries
- **Backups:** Schema-spezifische Backups möglich

### Negativ
- **Migration-Komplexität:** Migrationen müssen für alle Schemas ausgeführt werden
- **Schema-Limit:** PostgreSQL kann theoretisch nur begrenzt viele Schemas handhaben
- **Monitoring:** Mehr Aufwand beim Monitoring vieler Schemas

### Neutral
- **Middleware:** Benötigt Tenant-Detection-Middleware für jeden Request
- **Connection Pooling:** Funktioniert normal, `SET search_path` ist pro Session

## Implementierung

```python
# Middleware setzt search_path
async def set_tenant_schema(request, call_next):
    tenant_id = get_tenant_from_request(request)
    async with get_db() as session:
        await session.execute(f'SET search_path TO "{tenant_id}", public')
        response = await call_next(request)
    return response
```

## Validierung
- [x] Proof of Concept mit 3 Test-Tenants erfolgreich
- [x] Performance-Tests zeigen akzeptable Geschwindigkeit
- [x] Migration-Skript für alle Schemas funktioniert
- [x] Tenant-Isolation wurde in Security-Tests bestätigt

## Referenzen
- [Multi-tenancy with PostgreSQL Schemas](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Django Tenant Schemas](https://django-tenant-schemas.readthedocs.io/)
- [Multi-tenant Data Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/overview)

## Datum
2024-01-15

## Autoren
- Stumpf.works Entwicklungsteam
