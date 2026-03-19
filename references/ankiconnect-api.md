# Optionale Direktanlage via AnkiConnect (API v6)

Nutze dieses Dokument nur, wenn direkte Anlage in Anki explizit gewünscht ist.

## Grundprinzip

1. Endpoint: `http://127.0.0.1:8765`
2. Methode: `POST`
3. Request-Envelope:

```json
{
  "action": "deckNames",
  "version": 6,
  "params": {}
}
```

4. Response-Form (v6):

```json
{
  "result": <wert oder null>,
  "error": null
}
```

Wenn `error != null`, gilt der Aufruf als fehlgeschlagen.

## Empfohlener Ablauf

1. Verfügbarkeit testen mit `version`.
2. Decks lesen mit `deckNames`.
3. Falls Zieldeck fehlt: `createDeck`.
4. Notiztypen prüfen: `modelNames` und ggf. `modelFieldNames`.
5. Medien hochladen mit `storeMediaFile`.
6. Vor Massenschreiben validieren: `canAddNotes`.
7. Schreiben mit `addNotes`.
8. Optional prüfen mit `findNotes` + `notesInfo`.

## Einrichtung / erster Test

1. In Anki das Add-on **AnkiConnect** installieren und Anki neu starten.
2. Prüfen, dass Anki läuft und der lokale Endpoint `http://127.0.0.1:8765` erreichbar ist.
3. Sicherstellen, dass das Python-Paket `markdown` im aktiven Environment verfügbar ist.
3. Smoke Test im Repo ausführen:

```bash
python3 scripts/ankiconnect_smoke.py
```

Der Smoke Test prüft:
- AnkiConnect-Version
- ob `Basic`, `Cloze` und `Enhanced Cloze 2.1 v2` existieren
- ob die benötigten Felder vorhanden sind

## Relevante Actions

1. `version`
2. `deckNames`
3. `createDeck` (Parameter: `deck`)
4. `modelNames`
5. `modelFieldNames` (Parameter: `modelName`)
6. `canAddNotes` (Parameter: `notes`)
7. `addNotes` (Parameter: `notes`)
8. `findNotes` (Parameter: `query`)
9. `notesInfo` (Parameter: `notes`)
10. `guiBrowse` (Parameter: `query`)
11. `storeMediaFile` (Parameter: `filename`, `data` base64)

## Notizobjekt (Beispiel)

```json
{
  "deckName": "Import::Kurs",
  "modelName": "Basic",
  "fields": {
    "Front": "Frage...",
    "Back": "Antwort...<br>Quelle: S. 12"
  },
  "tags": ["course::kurs-slug"]
}
```

## Fehler- und Fallback-Regeln

1. Connection-Fehler (z. B. Add-on nicht aktiv, Port nicht erreichbar): nicht weiter versuchen, TSV-Fallback anbieten.
2. API-Fehler je Request (`error` gesetzt): Ursache melden, TSV-Fallback anbieten.
3. Teilfehler bei `addNotes` (einzelne `null` IDs): fehlerhafte Einträge separat melden und als TSV sichern.

## Skripte im Repo

### Smoke Test

```bash
python3 scripts/ankiconnect_smoke.py
```

### Direktimport aus Markdown

```bash
python3 scripts/ankiconnect_import.py \
  --in kurs_cards_v3.md \
  --course "Mein Kurs" \
  --slug mein-kurs
```

Das Skript:
1. parst die Markdown-Karten,
2. rendert Markdown in schlichtes HTML (`**`, `*`, Listen, Absätze),
3. stylt `Quelle:` und `Grafik/Diagramm:` automatisch als dezente Meta-Zeilen,
4. prüft die Notiztypen/Felder,
5. lädt referenzierte Bilder via `storeMediaFile` hoch,
6. bindet Bilder am Anfang des passenden Zielfelds ein,
7. legt die Notizen via `addNotes` an.

## Hinweise zur Robustheit

1. Bei Windows-Firewall-Anfrage Anki zulassen.
2. Für große Batches in sinnvolle Blöcke teilen.
3. Vor endgültigem Abschluss Anzahl erwarteter vs. tatsächlich angelegter Notizen vergleichen.
