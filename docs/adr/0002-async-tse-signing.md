# ADR 0002: Asynchrone TSE-Signierung mit Celery

## Status
Accepted

## Kontext
Nach deutschem Recht (KassenSichV) müssen alle Kassenvorgänge mit einer Technischen Sicherheitseinrichtung (TSE) signiert werden. Die Signierung via Cloud-TSE (Fiskaly) benötigt:
- API-Authentifizierung
- Netzwerk-Calls zur Fiskaly API
- Durchschnittlich 500-1500ms pro Signierung

Synchrone Signierung würde den Checkout-Prozess erheblich verlangsamen und zu schlechter User Experience führen.

## Entscheidung
Wir haben uns für **asynchrone TSE-Signierung mit Celery** entschieden:

- Transaktionen werden sofort als "completed" markiert
- TSE-Signierung läuft asynchron im Hintergrund via Celery Task
- Retry-Mechanismus für fehlgeschlagene Signaturen
- Periodischer Job synchronisiert ausstehende Signaturen

## Alternativen

### 1. Synchrone Signierung
**Pro:**
- Einfachste Implementierung
- Transaktion ist sofort vollständig signiert
- Keine zusätzliche Infrastruktur nötig

**Contra:**
- Schlechte User Experience (1-2 Sekunden Wartezeit)
- Blockiert Checkout bei Netzwerkproblemen
- Keine Offline-Fähigkeit

### 2. Webhook-basierte Signierung
**Pro:**
- Entkopplung von Checkout und Signierung
- Skalierbar

**Contra:**
- Komplexere Architektur
- Webhook-Verwaltung und Monitoring nötig
- Schwierigere Fehlerbehandlung

### 3. Asynchrone Queue mit Celery (Gewählt)
**Pro:**
- Schneller Checkout ohne Wartezeit
- Automatische Retries bei Fehlern
- Offline-Fähigkeit mit späterer Synchronisation
- Monitoring via Flower möglich

**Contra:**
- Zusätzliche Infrastruktur (Redis, Celery Workers)
- Komplexere Fehlerbehandlung
- Transaktionen sind initial nicht signiert

## Konsequenzen

### Positiv
- **User Experience:** Checkout in <200ms statt 1-2 Sekunden
- **Resilience:** System funktioniert auch bei Fiskaly-Ausfällen
- **Offline-Capability:** Transaktionen können offline erstellt werden
- **Retry-Mechanik:** Automatische Wiederholung bei Fehlern
- **Skalierung:** Worker können horizontal skaliert werden

### Negativ
- **Infrastruktur:** Benötigt Redis und Celery Worker
- **Komplexität:** Mehr bewegliche Teile im System
- **Eventual Consistency:** Signatur ist nicht sofort vorhanden
- **Monitoring:** Zusätzliches Monitoring für Queue-Status nötig

### Neutral
- **GoBD-Compliance:** Bleibt gewahrt, da Nachsignierung erlaubt ist
- **Reporting:** Berichte müssen ggf. auf unsignierte Transaktionen hinweisen

## Implementierung

```python
# Celery Task für TSE-Signierung
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sign_transaction_async(self, transaction_id: int, tenant_id: str):
    try:
        transaction = get_transaction(transaction_id)
        fiskaly = FiskalyAdapter(...)
        fiskaly.sign_transaction(transaction)
    except Exception as exc:
        raise self.retry(exc=exc)

# Periodischer Job für ausstehende Signaturen
@periodic_task(run_every=timedelta(minutes=5))
def sync_pending_signatures():
    unsigned = get_unsigned_transactions()
    for txn in unsigned:
        sign_transaction_async.delay(txn.id, txn.tenant_id)
```

## Risiken und Mitigation

### Risiko: Viele unsignierte Transaktionen
**Mitigation:**
- Monitoring-Alert wenn >100 unsignierte Transaktionen
- Dashboard zeigt Anzahl ausstehender Signaturen
- Manueller Trigger für Bulk-Signierung

### Risiko: Fiskaly-Ausfall >24h
**Mitigation:**
- Dokumentierter Prozess für manuelle Nachsignierung
- Export von unsignierten Transaktionen
- Benachrichtigung an Mandant

### Risiko: Queue-Overload
**Mitigation:**
- Rate-Limiting auf Fiskaly-API-Calls
- Queue-Monitoring mit Alerts
- Auto-Scaling von Celery Workers

## Validierung
- [x] Load-Tests mit 1000 Transaktionen/Minute erfolgreich
- [x] Retry-Mechanismus funktioniert bei simulierten Fehlern
- [x] Offline-Modus mit späterer Synchronisation getestet
- [x] Monitoring-Dashboard zeigt Queue-Status korrekt

## GoBD/KassenSichV Compliance
Nach Rücksprache mit Steuerberater:
- ✅ Nachträgliche Signierung ist zulässig
- ✅ Wichtig: Zeitstempel der Transaktion bleibt original
- ✅ Signierung muss "zeitnah" erfolgen (definiert als <24h)
- ✅ Alle Transaktionen müssen dokumentiert sein

## Referenzen
- [Celery Documentation](https://docs.celeryproject.org/)
- [KassenSichV §6 Technische Sicherheitseinrichtung](https://www.gesetze-im-internet.de/kassensichv/)
- [Fiskaly API Documentation](https://developer.fiskaly.com/)

## Datum
2024-01-15

## Autoren
- Stumpf.works Entwicklungsteam
