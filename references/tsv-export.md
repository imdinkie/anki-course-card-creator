# TSV-Export für Anki (Standardpfad)

Nutze dieses Dokument nur bei finalem Export.

## Ziel

Erzeuge eine UTF-8-TSV-Datei für den direkten Anki-Import mit den Notiztypen:
- `Basic`
- `Enhanced Cloze 2.1 v2`
- optional Legacy-`Cloze` für Altbestände

## Pflicht-Header (exakt)

```tsv
#separator:Tab
#html:true
#deck column:6
#notetype column:7
#tags column:8
```

Keine zusätzliche Datenkopfzeile ausgeben.

## Spalten (Reihenfolge fix)

1. `Field1`
2. `Field2`
3. `Field3`
4. `Field4`
5. `Field5`
6. `Deck`
7. `NoteType`
8. `Tags`

## Mapping

### Basic

1. `Field1`: `Front`
2. `Field2`: `Back`
3. `Field3`: `Notes`
4. `Field4`: leer
5. `Field5`: leer
6. `NoteType`: `Basic`

### Enhanced Cloze 2.1 v2

1. `Field1`: `Content`
2. `Field2`: `Note`
3. `Field3`: `Mnemonic`
4. `Field4`: `Extra`
5. `Field5`: `Cloze99` (standardmäßig leer)
6. `NoteType`: `Enhanced Cloze 2.1 v2`

### Legacy-Cloze

1. `Field1`: kompletter Cloze-Text inkl. `{{c1::...}}`
2. `Field2`: `Back Extra`
3. `Field3` bis `Field5`: leer
3. `NoteType`: `Cloze`

## Wichtiger Import-Hinweis

Anki richtet sich beim CSV/TSV-Import mit `#notetype column` faktisch nach der maximalen Feldanzahl der ersten Datenzeilen. Deshalb:
- Exportiere immer alle Zeilen mit fest 8 Spalten.
- Sorge dafür, dass Zeilen mit maximaler Feldnutzung zuerst stehen.
- Genau das übernimmt der Exporter automatisch.

## Quellen- und Grafikangaben

1. Behalte `Quelle: S. ...` im Antworts-/Cloze-Inhalt.
2. Bei visueller Relevanz beibehalten: `Grafik/Diagramm: <...>, S. ...`.
3. Wenn `SEITE_FEHLT` vorhanden ist, nicht exportieren, bis das geklärt ist.
4. Bilder werden nicht als Binärdaten in die TSV geschrieben, sondern als HTML-Referenzen wie `<img src="...">`.
5. Der Exporter erzeugt dafür automatisch ein flaches `media_bundle/`, das nur die tatsächlich referenzierten Bilder enthält.
6. Zeilen mit `Quelle:` und `Grafik/Diagramm:` werden automatisch als dezente Meta-Zeilen in HTML gerendert.

## Deck- und Tag-Regeln

1. Deckpfad standardmäßig: `Import::<Kurs>::<L1>::<L2>` (optional `::<L3>`).
2. `L1/L2/L3` werden aus den Markdown-Headings abgeleitet:
   - `# 01 Thema` -> `L1 = "01 Thema"`
   - `## 01 Unterthema` -> `L2 = "01 Unterthema"`
   - `### 01 Sub` -> `L3 = "01 Sub"`
3. Nummerierung: immer zweistellig (`01`, `02`, ...), sonst sortiert Anki bei >10 Elementen nicht zuverlässig.
4. Jede Ebene zählt nur innerhalb ihrer Ebene; zweite Ebene startet unter jedem neuen `#` wieder bei `01`.
5. Tags: mindestens `course::<kurs_slug>`. Weitere Tags optional.
6. Sobald eine Karte `Grafik/Diagramm: ...` referenziert oder ein `IMAGE OCCLUSION:`-Template ist, muss `Add-Image` gesetzt sein; der Exporter erzwingt das.

## Bild-Workflow

1. In Markdown-Entwürfen unter der Karte ein Bild referenzieren, z. B.:
   - `Image: ./assets/diagramm-01.png`
   - `![](./assets/diagramm-01.png)`
2. Beim finalen Export:
   - werden nur die tatsächlich referenzierten Bilder in `media_bundle/` kopiert
   - werden `<img src="...">`-Tags in die TSV-Felder geschrieben
   - stehen Bilder immer **am Anfang** des jeweiligen Zielfelds
3. Zielfelder:
   - `Basic` -> `Notes`
   - `Enhanced Cloze 2.1 v2` -> `Extra`
   - `Legacy-Cloze` -> `Back Extra`

## Import in Anki ohne API

1. Export ausführen und `*_cards_final.tsv` plus `media_bundle/` erzeugen.
2. Die Dateien aus `media_bundle/` in das gewünschte `collection.media` kopieren.
3. Die TSV in Anki importieren und `Allow HTML in fields` aktivieren.
4. Alternativ den Helper `scripts/copy_media_bundle.py` verwenden.

## Formatierungsregeln

1. Feldtrennzeichen ausschließlich Tab (`\t`).
2. HTML ist erlaubt und wird aktiv genutzt.
3. Zeilenumbrüche, Bullet-Lists und nummerierte Listen sollen sauber als HTML ausgegeben werden.
4. `*...*` und `**...**` sollen im Export als HTML-Kursiv/Fett erhalten bleiben.
5. Für die Umwandlung wird das Python-Paket `markdown` verwendet.
6. UTF-8 sicherstellen.

## Vor dem finalen Export prüfen

1. Header vollständig vorhanden.
2. Jede Zeile hat 8 Spalten.
3. Notetype-Werte ausschließlich `Basic`, `Enhanced Cloze 2.1 v2` oder optional `Cloze`.
4. Quellenangaben sind je Karte enthalten.
5. Headings im Markdown sind korrekt nummeriert (`# NN ...`, `## NN ...`).
6. Karten mit `Grafik/Diagramm:` haben `Add-Image` als Tag.
7. Stichprobe mit Umlauten, Klammern, Listen und Fett/Kursiv ist stabil.
