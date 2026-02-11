---
name: anki-course-card-creator
description: Erstellt und iteriert anspruchsvolle, atomare und quellenbasierte Anki-Karten aus Vorlesungs-PDFs, Skripten und Studiennotizen inklusive Seitenreferenzen, Grafik-/Diagrammverweisen und finalem Export. Verwenden bei Anfragen wie „Anki-Karten planen/erstellen“, „Karten aus PDF/Skript erzeugen“, „Karten korrigieren und neu versionieren“, „final als TSV exportieren“ oder „optional via AnkiConnect in Anki anlegen“.
---

# Anki-Karten für Hochschulkurse (quellenbasiert)

Arbeite standardmäßig auf Deutsch. Nutze eine gründliche, vollständige und prüfungsorientierte Abdeckung des geforderten Umfangs.

Wenn zusätzlich ein `pdf`-Skill installiert ist und der Nutzer als Input eine PDF bereitstellt, verwende für Extraktion/Seitenbezug/Rendering zuerst den `pdf`-Skill und arbeite anschließend mit dessen Output in diesem Workflow weiter.

## Workflow-Entscheidung

1. Wenn der Input ein komplettes Kursmaterial ist, arbeite im **Vollabdeckungsmodus**: decke alle Kapitel/Abschnitte systematisch ab.
2. Wenn der Input einen Teilbereich enthält, arbeite im **Fokusmodus**: decke nur den explizit gewünschten Bereich vollständig ab.
3. Wenn der Nutzer den Umfang nicht klar definiert, frage kurz nach:
   - gesamter Kurs oder Teilbereich,
   - Zielniveau (Grundlagen vs. vertieft),
   - gewünschte Kartenzahl grob als Rahmen.

## Dateinamen und Versionierung (verbindlich)

Verwende für jeden Lauf einen Kursslug in Kleinbuchstaben mit Bindestrichen, z. B. `wirtschaftsinformatik-1`.

1. Zusammenfassung: `<kurs_slug>_summary.md`
2. Erster Kartenentwurf: `<kurs_slug>_cards_v1.md`
3. Jede Korrekturrunde: neue Vollkopie mit fortlaufender Version
   - `<kurs_slug>_cards_v2.md`
   - `<kurs_slug>_cards_v3.md`
   - usw.
4. Finaler Export nach letzter Freigabe:
   - `<kurs_slug>_cards_final.tsv`

Regel: Überschreibe keine ältere Kartenversion. Jede Iteration erzeugt eine neue Datei mit eingearbeiteten Änderungen.

## Standardablauf

### 1) Materialaufnahme und Struktur

1. Erfasse die Inhaltsstruktur (Kapitel, Unterkapitel, zentrale Konzepte, Prozesse, Definitionen, Modelle, Beispiele).
2. Erfasse zu jedem relevanten Punkt die Quelle mit Seitenzahl.
3. Markiere visuelle Inhalte (Grafik, Diagramm, Tabelle, Modellbild) mit Seitenzahl.

### 2) Zusammenfassung erzeugen

Erstelle `<kurs_slug>_summary.md` als strukturierte Arbeitsbasis.

Anforderungen an die Zusammenfassung (detailliert und abdeckend):
1. Spiegel die Kurs-/Skriptstruktur als klare Kapitel- und Unterkapitelhierarchie.
2. Decke jeden Abschnitt des geforderten Umfangs ab (bei „gesamter Kurs“: alle Kapitel). Lasse keine Themen stillschweigend aus; wenn etwas irrelevanter wirkt, dann kurz, aber dennoch erfassen.
3. Schreibe pro Unterkapitel:
   - Kernaussage(n) in 2–5 Sätzen,
   - zentrale Begriffe/Definitionen (präzise, prüfungsnah),
   - Prozesse/Methoden als nummerierte Schritte,
   - Modelle/Frameworks mit Komponenten und Beziehungen,
   - typische Fehler/Missverständnisse (falls im Material angedeutet),
   - mindestens einen Quellenhinweis: `Quelle: S. X` bzw. `Quelle: S. X–Y`.
4. Für visuelle Inhalte:
   - erwähne relevante Grafiken/Diagramme/Tabellen mit Kontext und Page-Reference, z. B. `Grafik/Diagramm: <Kurzbezeichnung>, S. Z`,
   - benenne, wofür die Visualisierung gebraucht wird (welche Aussage/Beziehung sie trägt).
5. Markiere Prüfungsrelevanz explizit dort, wo das Material darauf hindeutet (Wiederholungen, Hervorhebungen, Definitionen, Klassifikationen, Prozessschritte).
6. Schließe die Zusammenfassung immer mit einer kurzen Sektion **ohne Musterlösung** ab:
   - Titel: `## Verständnisfragen (Essay, ohne Lösung)`
   - 5–12 bewusst komplexe, themenübergreifende Fragen (nicht atomar), die Verständnis, Transfer, Abwägungen und Verknüpfungen zwischen Kapiteln erzwingen.
   - Keine Antworten, keine Lösungsskizzen, keine Stichpunkte als „Hinweise“.

### 3) Kartenentwurf v1 erzeugen

Erstelle `<kurs_slug>_cards_v1.md` auf Basis der Zusammenfassung und des Quellmaterials.

Didaktik-Regeln:
1. Standardkartentyp: **Basic (Frage/Antwort)**.
2. **Cloze** nur, wenn für Schrittfolgen, Listen oder präzise Definitionen didaktisch klar besser.
3. Karten sind atomar, aber anspruchsvoll.
4. Keine trivialen Ein-Wort-Lücken ohne konzeptuelle Leistung.
5. Vermeide Prompt-Leakage: keine direkten Antwortbegriffe unnötig in der Frage.
6. Formulierungen der Fragen möglichst standardisiert und nüchtern halten.

Vollständigkeits-Regeln:
1. Bei „gesamter Kurs“: alle Kapitel abdecken.
2. Große Kapitel in mehrere Kartenserien aufteilen.
3. Wichtige Aufzählungen vollständig erfassen (nicht still kürzen).
4. Metadaten (ECTS, Orga, Modulnummern) nur aufnehmen, wenn explizit gewünscht.

### 4) Quellenpflicht pro Karte

Jede Karte enthält am Ende einen Quellenblock.

Pflicht:
1. `Quelle: S. X` oder `Quelle: S. X–Y`

Wenn visuelle Evidenz zur Karte gehört, zusätzlich Pflicht:
1. `Grafik/Diagramm: <Kurzbezeichnung>, S. Z`

Wenn Seite nicht sicher bestimmbar:
1. `Quelle: SEITE_FEHLT` setzen.
2. Karte für Klärung markieren.
3. Vor Finalisierung aktiv nachfordern oder bestätigen lassen.

### 5) Korrekturen iterativ einarbeiten

Bei Nutzerfeedback:
1. Übernehme Korrekturen in eine neue Version `<kurs_slug>_cards_vN.md`.
2. Erhalte bewährte Karten unverändert, ändere nur betroffene Inhalte.
3. Prüfe Konsistenz über Kapitel, Terminologie und Schwierigkeitsgrad.
4. Aktualisiere Quellen- und Grafikangaben, falls Inhalte verschoben wurden.

### 6) Finalisieren und Export

1. Exportiere erst nach finaler Korrektur oder expliziter Exportanweisung.
2. Standardpfad: TSV-Export gemäß `references/tsv-export.md`.
3. Optional: direkte Anlage in Anki via AnkiConnect gemäß `references/ankiconnect-api.md`.
4. Bei API-Problemen stets auf TSV-Fallback wechseln.

## Ausgabeformat für Kartenentwürfe (Markdown)

Nutze folgende Struktur pro Karte im Versionsdokument:

```markdown
## <Kapitelnummer> – <Kapiteltitel>

**<Kartentitel>:**
```Frage
**<Kartentitel>:**
<präzise Frage>
```
```Antwort
<prägnante, vollständige Antwort>
Quelle: S. X–Y
Grafik/Diagramm: <Kurzbezeichnung>, S. Z
```
```

Für Cloze:

```markdown
**<Kartentitel>:**
```Cloze
**<Kartentitel>:**
<Text mit {{c1::konzeptueller Lücke}}>
Quelle: S. X
Grafik/Diagramm: <Kurzbezeichnung>, S. Z
```
```

Wenn keine Grafik relevant ist, die Zeile `Grafik/Diagramm: ...` weglassen.

## Qualitätscheck vor Übergabe

Pro Karte:
1. Ist die Karte atomar?
2. Ist sie anspruchsvoll, aber fair lösbar?
3. Ist die Antwort ohne Mehrdeutigkeit prüfbar?
4. Ist `Quelle: ...` vorhanden?
5. Falls visuell relevant: Ist `Grafik/Diagramm: ...` vorhanden?

Für das Set:
1. Ist der geforderte Umfang vollständig abgedeckt?
2. Gibt es Redundanzen oder Lücken?
3. Sind Begriffe konsistent benannt?
4. Sind offene Marker wie `SEITE_FEHLT` geklärt oder explizit gemeldet?

## Wann `references/` laden

1. Lade `references/tsv-export.md`, sobald finaler TSV-Export verlangt ist.
2. Lade `references/ankiconnect-api.md`, sobald direkte Anki-Anlage via API verlangt ist.
3. Halte den Kernworkflow in dieser Datei, lade Detailregeln nur bei Bedarf nach.
