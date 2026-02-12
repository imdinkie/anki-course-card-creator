# TSV-Export für Anki (Standardpfad)

Nutze dieses Dokument nur bei finalem Export.

## Ziel

Erzeuge eine UTF-8-TSV-Datei für den direkten Anki-Import mit Standard-Notiztypen `Basic` und `Cloze`.

## Pflicht-Header (exakt)

```tsv
#separator:Tab
#html:true
#deck column:3
#notetype column:4
#tags column:5
```

Keine zusätzliche Datenkopfzeile ausgeben.

## Spalten (Reihenfolge fix)

1. `Field1`
2. `Field2`
3. `Deck`
4. `NoteType`
5. `Tags`

## Mapping

### Basic

1. `Field1`: Frageinhalt (inkl. Kartentitel, falls im Entwurf enthalten)
2. `Field2`: Antwortinhalt inkl. Quellenblock
3. `NoteType`: `Basic`

### Cloze

1. `Field1`: kompletter Cloze-Text inkl. `{{c1::...}}`
2. `Field2`: leer
3. `NoteType`: `Cloze`

## Quellen- und Grafikangaben

1. Behalte `Quelle: S. ...` im Antwort-/Cloze-Inhalt.
2. Bei visueller Relevanz beibehalten: `Grafik/Diagramm: <...>, S. ...`.
3. Wenn `SEITE_FEHLT` vorhanden ist, vor Export warnen und nur auf ausdrückliche Bestätigung exportieren.

## Deck- und Tag-Regeln

1. Deckpfad standardmäßig: `Import::<Kurs>::<L1>::<L2>` (optional `::<L3>`).
2. `L1/L2/L3` werden aus den Markdown-Headings abgeleitet:
   - `# 01 Thema` -> `L1 = "01 Thema"`
   - `## 01 Unterthema` -> `L2 = "01 Unterthema"`
   - `### 01 Sub` (selten) -> `L3 = "01 Sub"`
3. Nummerierung: immer zweistellig (`01`, `02`, ...), sonst sortiert Anki bei >10 Elementen nicht zuverlässig.
4. Jede Ebene zählt nur innerhalb ihrer Ebene; zweite Ebene startet unter jedem neuen `#` wieder bei `01` (keine `01.02`).
5. Tags: mindestens `course::<kurs_slug>`. Weitere Tags optional.
6. Pflicht: sobald eine Karte `Grafik/Diagramm: ...` referenziert, muss der Tag `Add-Image` gesetzt sein (wird beim Export erzwungen).
7. Wenn kein Tag benötigt: fünfte Spalte leer lassen.

## Formatierungsregeln

1. Feldtrennzeichen ausschließlich Tab (`\t`).
2. Bei HTML-Inhalten korrekt quoten.
3. Zeilenumbrüche im Feld als `<br>` ausgeben, wenn nötig.
4. UTF-8 sicherstellen.

## Vor dem finalen Export prüfen

1. Header vollständig vorhanden.
2. Jede Zeile hat 5 Spalten.
3. Notetype-Werte ausschließlich `Basic` oder `Cloze`.
4. Quellenangaben sind je Karte enthalten.
5. Stichprobe mit Sonderzeichen (Umlaute, Klammern, Doppelpunkte) ist stabil.
6. Headings im Markdown sind korrekt nummeriert (`# NN ...`, `## NN ...`).
7. Karten mit `Grafik/Diagramm:` haben `Add-Image` als Tag.
