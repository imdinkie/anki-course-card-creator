---
name: anki-course-card-creator
description: Erstellt und iteriert anspruchsvolle, atomare und quellenbasierte Anki-Karten aus Vorlesungs-PDFs, Skripten und Studiennotizen inklusive Seitenreferenzen, Grafik-/Diagrammverweisen und finalem Export. Verwenden bei Anfragen wie „Anki-Karten planen/erstellen“, „Karten aus PDF/Skript erzeugen“, „Karten korrigieren und neu versionieren“, „final als TSV exportieren“ oder „optional via AnkiConnect in Anki anlegen“.
---

# Anki-Karten für Hochschulkurse (quellenbasiert)

Arbeite standardmäßig auf Deutsch. Nutze eine gründliche, vollständige und prüfungsorientierte Abdeckung des geforderten Umfangs.

Schreibe deutsche Inhalte in diesem Skill, in den Referenzdokumenten und in den erzeugten Markdown-Artefakten standardmäßig mit echten Umlauten und `ß` in UTF-8. Verwende also `ä`, `ö`, `ü`, `Ä`, `Ö`, `Ü`, `ß` und nicht systematisch ASCII-Ersatzformen wie `ae`, `oe`, `ue`, `ss`, außer ein technischer Kontext erzwingt explizit ASCII.

Wenn zusätzlich ein `pdf`-Skill installiert ist und der Nutzer als Input eine PDF bereitstellt, verwende für Extraktion/Seitenbezug/Rendering zuerst den `pdf`-Skill und arbeite anschließend mit dessen Output in diesem Workflow weiter.

## Leitlinien (wichtig)

### Atomarität (Default)

Erstelle Karten standardmäßig eher atomar: lieber etwas mehr Karten, die schnell beantwortbar sind, als wenige Karten, bei denen man pro Karte lange nachdenken muss. Kompromittiere dabei keine technische Korrektheit.

Typische Split-Patterns:
- Lange Listen: zuerst Überblickskarte (falls sinnvoll), dann mehrere Karten mit Teilmengen oder je Item.
- Vergleiche: pro Vergleichsdimension eine Karte statt alles in eine Karte.
- Frameworks: pro Komponente/Begriff eigene Karte; Synthese-Karte optional.

Zusätzliche Guardrails:
- Wenn Frage oder Kartentitel die gesuchte Lösung schon direkt verraten, formuliere um.
- Lieber zwei gute Karten als eine Karte mit zwei halb-unabhängigen Gedankenschritten.
- Gruppiere mehrere Punkte nur dann auf derselben Karte bzw. unter derselben Cloze-Nummer, wenn sie wirklich als eine kleine, leicht merkbare Einheit gelernt werden können.
- Wenn eine Karte ohne Zusatzkontext zu nackt/kurz wäre, ergänze Kontext, Beispiel, Merkhilfe oder Einordnung in einem Zusatzfeld statt die Kernfrage künstlich aufzublähen.
- Wenn eine F/A-Karte in Wahrheit zwei Gedankenschritte oder zwei Teilfragen mischt, splitte sie oder baue sie in eine strukturierte Cloze mit echter Leitfrage um.

### Notiztyp-Policy (verbindlich)

Default:
- Standardkartentyp ist `Basic`.
- Standard-Cloze-Typ ist **nicht** mehr das Anki-Standard-Notizformat `Cloze`, sondern `Enhanced Cloze 2.1 v2`.

Verwendung:
- `Basic` für wirklich atomare Definitionen, Abgrenzungen, Zusammenhänge, Anwendungen, Vergleiche, Begründungen, Beispiele und andere konzeptuelle Fragen.
- `Enhanced Cloze 2.1 v2` bevorzugt für Listen, Zuordnungen, Sequenzen, Matrizen, Akronym-/Artefakt-Bündel und strukturierte Mehrfach-Reproduktion; im Zweifel eher Cloze als F/A, solange die Karte lösbar und nicht überladen bleibt.
- Das alte Standard-`Cloze` nur aus Kompatibilitätsgründen in Bestandsdateien akzeptieren, aber nicht mehr als Default erzeugen.

Feldnutzung:
- Bei `Basic` gibt es die Felder `Front`, `Back`, `Notes`. Nutze `Notes` großzügig für Kontext, Beispiele, Mnemonics, Eselsbrücken, typische Fehler oder kurze Einordnungen.
- Bei `Enhanced Cloze 2.1 v2` gibt es die Felder `Content`, `Note`, `Mnemonic`, `Extra`, `Cloze99`. Nutze `Note`, `Mnemonic` und `Extra` großzügig, aber nur wenn sie didaktisch helfen. `Cloze99` bleibt standardmäßig leer.
- In `Notes` / `Note` / `Mnemonic` / `Extra` nie Meta-Kommentare über die Karte selbst schreiben, also nichts wie „diese Karte prüft ...“, „klausurnah“, „bewusst isoliert“, „die Clozes sind absichtlich so gesetzt ...“. Dort gehört nur inhaltlicher Zusatznutzen hinein.

### Fragequalität / Prompt-Leakage (verbindlich)

Vermeide Formulierungen, bei denen Titel oder Frage die Antwort schon mitliefern.

Praktisch:
- Kartentitel eher neutral als etikettierend formulieren.
- In der Frage nicht unnötig den Zielbegriff nennen, wenn eine indirektere Formulierung die gleiche Präzision hat.
- Keine Fragen bauen, die sich durch das Lesen des Titels praktisch schon selbst beantworten.
- Vor jeder finalen Karte kurz prüfen: "Würde ich die Antwort auch dann noch aktiv erinnern müssen, wenn ich nur Titel + Frage sehe?"
- Auch `Grafik/Diagramm:` darf keine Lösung spoilern. Dort nur neutrale Kurzbezeichnungen verwenden, nicht schon die gesuchten Antwortbegriffe oder komplette Aufzählungen.

### Schema-/Schrittfolgen-Pattern (nur bei ausreichender Komplexität)

Wenn ein Schema/Prozess/Schrittfolge hinreichend komplex ist (mehrere Schritte, Abhängigkeiten, Fehlerpotenzial, prüfungsnah), nutze dieses Pattern:
1. Überblickskarte (F/A): "Welche Schritte/Phasen gehören zu X?"
2. Detailkarten: pro Schritt/Phase eine Karte, die Zweck, Inhalt und typische Inputs/Outputs erklärt.

Bei trivialen 2-3-Punkt-Listen ohne Tiefe nicht erzwingen.

### Hierarchische Ordnung (verbindlich)

Strukturiere den Kartenentwurf thematisch über Markdown-Headings:
- Level 1: `# 01 <Thema>`
- Level 2: `## 01 <Unterthema>`
- Level 3: `### 01 <Sub-Unterthema>` (selten, nur wenn wirklich nötig)

Nummerierungsregeln (verbindlich):
- Immer zweistellig (`01`, `02`, ...).
- Jede Ebene nummeriert nur innerhalb ihrer Ebene.
- Die zweite Ebene startet unter jedem neuen `#` wieder bei `01`.
- Keine hierarchische Nummerierung wie `01.02` verwenden.

### Kontext in Anki (Breadcrumb) (verbindlich)

Die Zugehörigkeit jeder Karte zum Themenblock wird beim TSV-Export automatisch als Breadcrumb aus der aktuellen `#`/`##`/`###`-Hierarchie in Anki sichtbar gemacht.

### Definitionen vor Details (verbindlich)

Wenn ein Begriff/Artefakt/Prozess neu eingeführt wird:
1. Erzeuge zuerst eine explizite Definitionskarte (`Was ist X?` / Definition + Scope).
2. Falls im Material ableitbar: zweite Karte zu Ziel/Aufgaben (`Was sind Ziele/Aufgaben von X?`).
3. Detailkarten (z. B. Inputs/Outputs, Kennzahlen, Regeln, Gremien, Dokumente) erst danach.

### Vereinfachtes Prozess/Topic-Pattern (overgeneration-sicher)

Default pro neuem Prozess/Topic: maximal 2 Karten (siehe oben: Definition + Aufgaben).

Optional, aber nur wenn explizit im Material und klar prüfbar:
- Zuordnungskarte: `Wo ist X eingeordnet?` (Framework/Phase/Kategorie), wenn die Einordnung gelehrt wird.
- Schritte/Artefakte: nur bei nicht-trivialer Liste/Abfolge/Artefakt-Set; dann strikt atomar splitten (keine Monsterkarte).

Guardrails:
- Generiere keine Inputs/Outputs/Kennzahlen/etc. "auf Verdacht".
- Wenn Definition + Aufgaben bereits abgedeckt sind: keine zusätzlichen Detailkarten ohne klaren Material-Anker.

### Verbotene Formulierungen (verbindlich)

Nicht verwenden:
- `klausurrelevant` / `prüfungsrelevant` als Fragestil (z. B. "Warum ist X prüfungsrelevant?")
- `laut Folie` / `laut Skript`

Stattdessen:
- objektive Inhaltsfragen (Definition, Abgrenzung, Anwendung, Beispiel, Konsequenz)
- bei visuellen Zuordnungen/Tabellen/Diagrammen: bevorzugt Image-Occlusion-Template (siehe `references/image-occlusion.md`)

### Akronyme & Artefakt-Mappings (Default: Enhanced Cloze)

Wenn mehrere Akronyme/Begriffe zusammengehören (z. B. Dokumente, Kennzahlen, Rollen):
- Nutze standardmäßig eine `Enhanced Cloze 2.1 v2`-Karte.
- Pro Begriff möglichst genau eine Completion.
- Schreibe Akronyme aus (EN + DE, falls im Material vorhanden).
- Packe ausgeschriebene Bedeutung und ggf. sehr kurzes Praxisbeispiel möglichst mit in die Completion, wenn das die Lernbarkeit klar verbessert.
- Wenn ein Akronym-Bündel inhaltlich zu komplex wird, splitte in zwei Karten statt alles auf eine Karte zu pressen.
- Lasse in der Cloze genug sprachlichen Rahmen stehen, damit die Karte lösbar bleibt; nicht den gesamten Satz blind leerziehen, wenn dadurch nur noch ein nacktes Loch ohne Kontext übrig bleibt.

### Abschlussfragen/Lernziele als Coverage-Checklist (ohne Tooling)

Wenn im Material Abschlussfragen/Lernziele/Review Questions existieren:
- Nutze sie als Abdeckungscheckliste.
- Stelle sicher, dass jede Frage inhaltlich mindestens einmal abgedeckt ist.
- Vermeide Redundanz: keine 1:1 Spiegelung erzwingen, sondern gezielt Lücken schließen.

### Visuals: Tag-Pflicht `Add-Image`

Wenn eine Karte visuell relevante Evidenz referenziert (z. B. `Grafik/Diagramm: ...`), muss sie in Anki mit Tag `Add-Image` markiert werden.

Praktisch:
- Im Markdown-Draft kannst du optional direkt nach der Antwort-Fence eine Zeile `Tags: ...` setzen (siehe unten).
- Beim TSV-Export wird `Add-Image` automatisch hinzugefügt, sobald `Grafik/Diagramm:` im Karteninhalt vorkommt (Enforcement).
- Bei visuellen Karten soll außerdem unter der Karte ein expliziter Bildblock stehen, z. B. `Image: ./assets/<datei>.png` oder `![](./assets/<datei>.png)`.
- Das finale Export-Bundle soll nur die tatsächlich referenzierten Bilder enthalten; Arbeits-Screenshots in `assets/` dürfen darüber hinausgehen.

### Markdown-Kursmaterial: Bilder mit einlesen

Wenn Kursmaterial auch aus `.md`-Dateien besteht, können dort Bilder verlinkt/eingebettet sein (z. B. `![](img.png)` oder `![[img.png]]`). Diese Bilder müssen mit eingelesen und inhaltlich verstanden werden, bevor du Zusammenfassung/Karten finalisierst.

## Workflow-Entscheidung

1. Wenn der Input ein komplettes Kursmaterial ist, arbeite im **Vollabdeckungsmodus**: decke alle Kapitel/Abschnitte systematisch ab.
2. Wenn der Input einen Teilbereich enthält, arbeite im **Fokusmodus**: decke nur den explizit gewünschten Bereich vollständig ab.
3. Wenn der Nutzer den Umfang nicht klar definiert, frage kurz nach:
   - gesamter Kurs oder Teilbereich,
   - Zielniveau (Grundlagen vs. vertieft),
   - gewünschte Kartenzahl grob als Rahmen.

## Dateinamen und Versionierung (verbindlich)

Verwende für jeden Lauf einen Kursslug in Kleinbuchstaben mit Bindestrichen, z. B. `kurs-slug`.

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
4. Wenn `.md`-Dateien Teil des Inputs sind: finde und betrachte alle dort referenzierten Bilder und extrahiere deren Kernaussagen für Summary/Karten.
5. Wenn du für PDF-/Skriptmaterial Bilder oder Diagramme renderst/croppst, speichere sie zunächst in `./assets/`. Referenziere später in Karten aber nur die wirklich benötigten Bilder.

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
2. **Enhanced Cloze 2.1 v2** verwenden, wenn für Listen, Schrittfolgen, Zuordnungen oder strukturierte Wiedererkennung didaktisch klar besser.
3. Karten sind atomar, aber anspruchsvoll.
4. Keine trivialen Ein-Wort-Lücken ohne konzeptuelle Leistung.
5. Vermeide Prompt-Leakage: keine direkten Antwortbegriffe unnötig in der Frage.
6. Formulierungen der Fragen möglichst standardisiert und nüchtern halten.
7. Definiere wichtige Begriffe zuerst auf High-Level, bevor du in Unterarten, Inputs/Outputs oder Spezialfälle gehst.
8. Gib bei schwierigen/abstrakten Karten lieber ein knappes Beispiel oder Zusatzkontext in `Notes` / `Note` / `Mnemonic` / `Extra`, statt die Kernfrage zu verwässern.
9. Antworten mit Aufzählungen als echte Listen formatieren, nicht als lange Komma-Ketten.
10. Hebe Schlüsselbegriffe in Antworten gezielt mit `*...*` oder `**...**` hervor.

Vollständigkeits-Regeln:
1. Bei „gesamter Kurs“: alle Kapitel abdecken.
2. Große Kapitel in mehrere Kartenserien aufteilen.
3. Wichtige Aufzählungen vollständig erfassen (nicht still kürzen).
4. Metadaten (ECTS, Orga, Modulnummern) nur aufnehmen, wenn explizit gewünscht.
5. Keine Karten zu Kurs-/Prüfungskontext oder Zusatzunterlagen (z. B. Ablauf, Hilfsmittel, Bewertungsregeln), außer der Nutzer fordert das explizit.

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
5. Kommentare mit führendem `>` sind reine Review-Anweisungen und dürfen nie in die finalen Karteninhalte oder Zusatzfelder übernommen werden.
6. Wenn Feedback auf Wiederholungen hinweist, streiche die Wiederholung standardmäßig, statt sie nur umzuschreiben.

### 6) Finalisieren und Export

1. Exportiere erst nach finaler Korrektur oder expliziter Exportanweisung.
2. Standardpfad: TSV-Export gemäß `references/tsv-export.md`.
3. Optional: direkte Anlage in Anki via AnkiConnect gemäß `references/ankiconnect-api.md`.
4. Bei API-Problemen stets auf TSV-Fallback wechseln.

## Ausgabeformat für Kartenentwürfe (Markdown)

Nutze folgende Struktur pro Karte im Versionsdokument. Beachte: thematische Ordnung über `#`/`##`/`###` ist verbindlich (siehe Leitlinien).

````markdown
# 01 <Thema>
## 01 <Unterthema>

**<Kartentitel>:**
```Question
**<Kartentitel>:**
<präzise Frage>
```
```Answer
<prägnante, vollständige Antwort>
Quelle: S. X–Y
Grafik/Diagramm: <Kurzbezeichnung>, S. Z
```
```Notes
<optionaler Zusatzkontext, Beispiel, Merkhilfe, Einordnung>
```
Image: ./assets/<datei>.png

Tags: Add-Image
````

Hinweise:
- `Notes` ist optional, sollte aber großzügig genutzt werden, wenn zusätzlicher Kontext das Erinnern stabilisiert.
- Wenn keine Grafik relevant ist, die Zeile `Grafik/Diagramm: ...` weglassen.
- Wenn du aus einem Review-Entwurf mit `>`-Kommentaren arbeitest, interpretiere diese Zeilen als Änderungsanweisungen und lasse sie in der neuen Version vollständig weg.

Für `Enhanced Cloze 2.1 v2`:

````markdown
**<Kartentitel>:**
```EnhancedCloze
**<Kartentitel>:**
<Text mit {{c1::konzeptueller Lücke}}>
Quelle: S. X
Grafik/Diagramm: <Kurzbezeichnung>, S. Z
```
```Note
<optionale kurze Einordnung oder Zusatzkontext>
```
```Mnemonic
<optionale Eselsbrücke / Merkhilfe>
```
```Extra
<optionale Zusatzinformation, Mini-Beispiel, Abgrenzung>
```
Image: ./assets/<datei>.png

Tags: Add-Image
````

Für Legacy-Bestände weiterhin erlaubt:

````markdown
**<Kartentitel>:**
```Cloze
**<Kartentitel>:**
<Legacy-Cloze-Text mit {{c1::...}}>
Quelle: S. X
```
```BackExtra
<optionaler Zusatzkontext; Bilder werden bei Legacy-Cloze hier vorne eingebunden>
```
Image: ./assets/<datei>.png
````

Regeln:
- `Note`, `Mnemonic` und `Extra` sind optional, aber ausdrücklich erwünscht, wenn sie das Lernen verbessern.
- Nicht alle Zusatzfelder künstlich befüllen. Nutze sie nur mit echtem didaktischem Mehrwert.
- Auch bei `Enhanced Cloze` muss die eigentliche Frage erhalten bleiben; keine kartenlose Cloze-Wand ohne explizite Leitfrage.
- Wenn mehrere Stichpunkte unabhängig sind, gib ihnen standardmäßig unterschiedliche Cloze-Nummern. Dieselbe Nummer nur bei eng zusammengehörigen Paaren/Bündeln.
- Clozes sollen den relevanten Chunk abdecken, aber nicht den gesamten sprachlichen Rahmen zerstören. Ein kurzer, lösbarer Kontext soll nach Möglichkeit sichtbar bleiben.
- `BackExtra` ist bei Legacy-`Cloze` optional, aber das vorgesehene Feld für Zusatzkontext und Bilder.
- Bilder werden im finalen Export immer **am Anfang** des jeweiligen Zielfelds eingebunden:
  - `Basic` -> `Notes`
  - `Enhanced Cloze 2.1 v2` -> `Extra`
  - `Legacy-Cloze` -> `Back Extra`
- Die `Tags:`-Zeile ist optional. Sie steht außerhalb der Codefences und wird beim TSV-Export in die Tag-Spalte gemappt.
- `Add-Image` ist Pflicht, sobald `Grafik/Diagramm:` vorkommt (wird beim Export zusätzlich erzwungen).

## Praktische Hilfstools (optional, empfohlen)

Wenn du im aktuellen Arbeitsordner schneller und fehlerärmer arbeiten willst, kannst du folgende Helper nutzen (siehe `scripts/`):
- `scripts/preflight_check.py`: prüft Kartenstruktur, Quellenpflicht, Heading-Nummerierung, `SEITE_FEHLT`; warnt u. a. bei verbotenen Formulierungen, Legacy-`Cloze`, möglicher Antwort-Leakage, schlecht formatierten Komma-Listen und fehlenden Bildblöcken bei visuellen Karten.
- `scripts/export_tsv.py`: exportiert final nach TSV für `Basic`, `Enhanced Cloze 2.1 v2` und Legacy-`Cloze`; wandelt Listen/Zeilenumbrüche in HTML um, leitet Subdecks aus Headings ab, baut automatisch ein `media_bundle/` mit allen referenzierten Bildern und bindet Bilder am Anfang des jeweiligen Zielfelds ein.
- `scripts/md_collect_images.py`: listet in `.md` referenzierte Bilder auf und prüft, ob sie existieren.
- `scripts/copy_media_bundle.py`: kopiert das finale `media_bundle/` in ein Anki-`collection.media`-Verzeichnis.
- `scripts/ankiconnect_smoke.py`: prüft, ob AnkiConnect läuft und ob die benötigten Notiztypen/Felder existieren.
- `scripts/ankiconnect_import.py`: lädt referenzierte Medien via AnkiConnect hoch und legt die Notizen direkt in Anki an.

Wenn pip/Installationen systemweit blockiert sind (PEP 668): nutze ein venv im Arbeitsordner, z. B. `python3 -m venv .venv` und dann `. .venv/bin/activate`.
Wenn dir bei Helper-Skripten Python-Pakete fehlen, erstelle standardmäßig selbst ein lokales `.venv` im Arbeitsordner und installiere die nötigen Pakete dort, statt auf systemweite Installation zu warten.

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
3. Lade `references/image-occlusion.md`, sobald visuelle Inhalte als Image Occlusion umgesetzt werden sollen.
4. Lade `references/visuals-and-ocr.md`, sobald Diagramme/Tabellen/Zahlen sauber aus Visuals extrahiert oder konzeptionell verarbeitet werden müssen.
5. Lade `references/md-images.md`, sobald Kursmaterial `.md`-Dateien mit Bildreferenzen enthält.
6. Halte den Kernworkflow in dieser Datei, lade Detailregeln nur bei Bedarf nach.
