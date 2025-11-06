# Architecture Decision Records (ADR)

Diese Dokumentation enthält alle wichtigen Architekturentscheidungen für das Stumpf.works POS System.

## Was sind ADRs?

Architecture Decision Records (ADRs) dokumentieren wichtige Architekturentscheidungen zusammen mit ihrem Kontext und den Konsequenzen. Sie helfen:

- **Nachvollziehbarkeit:** Warum wurden bestimmte Entscheidungen getroffen?
- **Onboarding:** Neue Entwickler verstehen die Architektur schneller
- **Diskussion:** Basis für technische Diskussionen
- **Geschichte:** Dokumentation der technischen Evolution

## ADR Format

Jede ADR folgt diesem Template:

```markdown
# ADR [Nummer]: [Titel]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Kontext
[Beschreibung des Problems und der Anforderungen]

## Entscheidung
[Was wurde entschieden und warum]

## Alternativen
[Welche Alternativen wurden betrachtet]

## Konsequenzen
### Positiv
[Vorteile der Entscheidung]

### Negativ
[Nachteile und Risiken]

### Neutral
[Weitere Auswirkungen]

## Referenzen
[Links zu relevanten Dokumenten]

## Datum
[Datum der Entscheidung]

## Autoren
[Wer war beteiligt]
```

## Übersicht aller ADRs

| Nr | Titel | Status | Datum |
|----|-------|--------|-------|
| [0001](./0001-multi-tenant-architecture.md) | Multi-Tenant Architecture mit PostgreSQL Schema-per-Tenant | Accepted | 2024-01-15 |
| [0002](./0002-async-tse-signing.md) | Asynchrone TSE-Signierung mit Celery | Accepted | 2024-01-15 |
| [0003](./0003-fastapi-sqlalchemy-stack.md) | FastAPI + SQLAlchemy 2.0 + AsyncIO Stack | Accepted | 2024-01-15 |
| [0004](./0004-react-vite-frontend.md) | React + Vite + TypeScript Frontend | Accepted | 2024-01-15 |
| [0005](./0005-plugin-architecture.md) | Plugin-basierte Erweiterungsarchitektur | Accepted | 2024-01-15 |
| [0006](./0006-offline-first-architecture.md) | Offline-First Architecture mit IndexedDB | Accepted | 2024-01-15 |

## Kategorien

### Backend Architecture
- [ADR 0001: Multi-Tenant Architecture](./0001-multi-tenant-architecture.md)
- [ADR 0003: FastAPI + SQLAlchemy Stack](./0003-fastapi-sqlalchemy-stack.md)

### Compliance & Legal
- [ADR 0002: Asynchrone TSE-Signierung](./0002-async-tse-signing.md)

### Frontend Architecture
- [ADR 0004: React + Vite Frontend](./0004-react-vite-frontend.md)
- [ADR 0006: Offline-First Architecture](./0006-offline-first-architecture.md)

### Extensibility
- [ADR 0005: Plugin Architecture](./0005-plugin-architecture.md)

## Neues ADR erstellen

1. **Nummer wählen:** Nächste verfügbare Nummer
2. **Template kopieren:** Nutze das Format oben
3. **Ausfüllen:** Alle Sections komplett ausfüllen
4. **Review:** Mit Team besprechen
5. **Committen:** ADR ins Repository aufnehmen

```bash
cp docs/adr/template.md docs/adr/000X-my-decision.md
# ADR ausfüllen
git add docs/adr/000X-my-decision.md
git commit -m "docs: Add ADR 000X - My Decision"
```

## ADR Status

- **Proposed:** Vorgeschlagen, noch in Diskussion
- **Accepted:** Akzeptiert und implementiert
- **Deprecated:** Veraltet, wird nicht mehr empfohlen
- **Superseded:** Ersetzt durch neuere ADR

## Wann ein ADR schreiben?

Schreibe ein ADR wenn:

✅ **JA:**
- Grundlegende Technologie-Entscheidungen (Framework, Datenbank, etc.)
- Architektur-Patterns (Multi-Tenancy, Event-Sourcing, etc.)
- Sicherheits-relevante Entscheidungen
- Performance-kritische Designs
- Compliance-relevante Entscheidungen
- Etwas, das schwer zu ändern ist

❌ **NEIN:**
- Code-Style Entscheidungen (dafür: Linting-Regeln)
- Temporäre Workarounds
- Implementierungs-Details
- Triviale Entscheidungen

## Best Practices

### 1. Kontext ist King
Erkläre **warum** die Entscheidung nötig war, nicht nur **was** entschieden wurde.

### 2. Alternativen dokumentieren
Zeige welche Optionen betrachtet wurden und warum sie verworfen wurden.

### 3. Ehrlich über Nachteile
Dokumentiere auch die Schattenseiten der Entscheidung.

### 4. Konkret bleiben
Nutze Code-Beispiele und konkrete Zahlen wo möglich.

### 5. Links und Referenzen
Verlinke relevante Dokumentation und Artikel.

### 6. Kurz und prägnant
ADRs sollten in 5-10 Minuten lesbar sein.

## ADR Review-Prozess

1. **Entwurf erstellen:** Autor schreibt ADR
2. **Team Review:** Mindestens 2 Reviews von Entwicklern
3. **Diskussion:** Bei Uneinigkeit: Team-Meeting
4. **Finalisierung:** Status auf "Accepted" setzen
5. **Kommunikation:** Team informieren

## ADR Ändern

ADRs sollten **nicht nachträglich geändert** werden. Stattdessen:

1. **Neues ADR:** Schreibe ein neues ADR das das alte "Supersedes"
2. **Status ändern:** Altes ADR auf "Superseded" setzen
3. **Verlinkung:** Beide ADRs verlinken

### Beispiel:

```markdown
# ADR 0001: Multi-Tenant Architecture

## Status
Superseded by [ADR 0010](./0010-multi-tenant-v2.md)
```

## Referenzen

- [ADR GitHub](https://adr.github.io/)
- [Michael Nygard's ADR Blog Post](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR Tools](https://github.com/npryce/adr-tools)

## Fragen?

Bei Fragen zu ADRs kontaktiere das Entwicklungsteam oder erstelle ein Issue im Repository.
