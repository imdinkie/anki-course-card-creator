# anki-course-card-creator

Dieses Skill ist auf einen Workflow mit zwei bevorzugten Anki-Notiztypen ausgelegt:
- `Basic`
- `Enhanced Cloze 2.1 v2`

Zusätzlich benötigt der Export-/Importpfad für saubere Markdown-zu-HTML-Konvertierung das Python-Paket `markdown`.

## Voraussetzungen für optimale Nutzung

### 0. Python-Markdown verfügbar machen

Der TSV-Export und der direkte AnkiConnect-Import verwenden denselben Markdown-Renderer. Dadurch werden z. B. `**fett**`, `*kursiv*`, Bullet-Lists und nummerierte Listen sauber in schlichtes HTML übertragen.

Im aktuellen Profil ist das Paket auf dieser Maschine bereits verfügbar. Falls es in einer anderen Umgebung fehlt:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Hinweis:
- Wenn dem Modell bei der Arbeit Python-Pakete fehlen, soll es standardmäßig selbst ein lokales `.venv` im Arbeitsordner erstellen und die fehlenden Pakete dort installieren.

### 1. Enhanced Cloze installieren

Für den empfohlenen Cloze-Workflow wird das Add-on `Enhanced Cloze` benötigt, konkret der Notiztyp `Enhanced Cloze 2.1 v2`.

Referenz:
- https://ankiweb.net/shared/info/1990296174

Warum:
- pseudo clozes bleiben sichtbar bzw. separat aufdeckbar
- Listen, Zuordnungen und mehrstufige Inhalte lassen sich deutlich besser lernen als mit Standard-Cloze
- auf Mobilgeräten ist das schrittweise Aufdecken angenehmer

### 2. Dem Basic-Notiztyp das Feld `Notes` hinzufügen

Für optimale Ergebnisse sollte dein `Basic`-Notiztyp nicht nur `Front` und `Back`, sondern zusätzlich ein drittes Feld `Notes` haben.

Empfohlene Felder:
- `Front`
- `Back`
- `Notes`

Warum:
- schwierige oder konzeptionelle Karten brauchen oft etwas Kontext
- Beispiele, Eselsbrücken und Einordnungen können in `Notes` ausgelagert werden, ohne die Kernfrage zu verwässern
- dadurch bleiben die Karten atomar, aber nicht zu nackt

### 2a. Empfohlenes Basic-Template

Damit `Notes` inklusive eingebetteter Bilder auf der Kartenrückseite sichtbar ist, sollte das `Basic`-Notizformat in Anki mindestens so konfiguriert sein:

Back Template:

```html
{{FrontSide}}

<hr id=answer>

<div class="answer-block">
  {{Back}}
</div>

{{#Notes}}
<div class="notes-block">
  {{Notes}}
</div>
{{/Notes}}
```

Zusätzliche CSS-Regeln:

```css
.answer-block {
  margin-bottom: 14px;
}

.notes-block {
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px solid #ddd;
}

.notes-block img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 0 0 10px 0;
  border-radius: 6px;
}
```

Hinweis:
- `Notes` bleibt dabei optisch normal lesbar und wird nicht künstlich ausgegraut.
- Bilder aus dem Import erscheinen im `Notes`-Block.

### 3. Legacy-Cloze nur mit `Back Extra`

Falls ältere Kartensätze weiterhin das Standard-Notizformat `Cloze` verwenden, sollte dieses Modell das Feld `Back Extra` besitzen.

Warum:
- dort werden bei Legacy-Cloze Zusatzkontext und referenzierte Bilder eingebunden

### 4. Erwartete Felder in Anki

Der direkte Import und der TSV-Workflow erwarten diese Felder:

`Basic`
- `Front`
- `Back`
- `Notes`

`Enhanced Cloze 2.1 v2`
- `Content`
- `Note`
- `Mnemonics`
- `Extra`
- `Cloze99`

`Cloze`
- `Text`
- `Back Extra`

## Aktuelle Export-Logik

Der lokale Exporter unterstützt:
- `Basic`
- `Enhanced Cloze 2.1 v2`
- Legacy-`Cloze` für ältere Bestände

Zusätzlich gilt:
- Markdown in Kartenfeldern wird vor Export bzw. Direktimport in schlichtes HTML umgewandelt.
- `Quelle:` und `Grafik/Diagramm:` werden automatisch als dezente Meta-Zeilen gerendert.

Markdown-Entwürfe können daher gemischt sein. Beim Export werden Decks, Notiztyp und Tags automatisch gesetzt.

## Werkzeuge und Verwendung

### 1. Kartenentwurf prüfen

```bash
python3 scripts/preflight_check.py --in mein-kurs_cards_v3.md
```

### 2. Finalen TSV-Export + Medienbundle erzeugen

```bash
python3 scripts/export_tsv.py \
  --in mein-kurs_cards_v3.md \
  --out mein-kurs_cards_final.tsv \
  --course "Mein Kurs" \
  --slug mein-kurs
```

Optional mit explizitem Bundle-Ziel:

```bash
python3 scripts/export_tsv.py \
  --in mein-kurs_cards_v3.md \
  --out mein-kurs_cards_final.tsv \
  --course "Mein Kurs" \
  --slug mein-kurs \
  --media-bundle ./media_bundle
```

### 3. Medienbundle nach Anki kopieren

```bash
python3 scripts/copy_media_bundle.py --bundle ./media_bundle
```

### 4. AnkiConnect Smoke Test

```bash
python3 scripts/ankiconnect_smoke.py
```

### 5. Direkten Import aus Markdown ausführen

```bash
python3 scripts/ankiconnect_import.py \
  --in mein-kurs_cards_v3.md \
  --course "Mein Kurs" \
  --slug mein-kurs
```

## Bild-Workflow

Es gibt jetzt zwei Bildordner mit unterschiedlicher Aufgabe:
- `assets/`: Arbeitsordner für gerenderte/cropte Bilder und Diagramme
- `media_bundle/`: finaler, schlanker Exportordner mit nur den tatsächlich referenzierten Bildern

Wichtig:
- Die TSV enthält nur Bildreferenzen wie `<img src="...">`, nicht die Binärdaten selbst.
- Für normalen Anki-Import müssen die Dateien aus `media_bundle/` in `collection.media` landen.
- Dafür gibt es den Helper:

```bash
python3 scripts/copy_media_bundle.py --bundle ./media_bundle
```

Wenn nur eine lokale Anki-Collection gefunden wird, erkennt das Skript `collection.media` automatisch. Sonst kann der Pfad explizit gesetzt werden:

```bash
python3 scripts/copy_media_bundle.py \
  --bundle ./media_bundle \
  --collection-media ~/.local/share/Anki2/User\\ 1/collection.media
```

## AnkiConnect optional

AnkiConnect ist jetzt über zwei Skripte vorbereitet:
- `scripts/ankiconnect_smoke.py`
- `scripts/ankiconnect_import.py`

Mit AnkiConnect brauchst du **keinen** TSV-/CSV-Export mehr. Der Direktimport geht direkt aus dem Markdown in Anki.

Der TSV-Export bleibt sinnvoll als:
- Fallback, wenn AnkiConnect nicht läuft
- portabler Exportweg
- kontrollierbarer Zwischenstand vor dem Import

### Einrichtung

1. In Anki das Add-on **AnkiConnect** installieren.
2. Anki neu starten.
3. Smoke Test ausführen:

```bash
python3 scripts/ankiconnect_smoke.py
```

### Direktimport testen

```bash
python3 scripts/ankiconnect_import.py \
  --in mein-kurs_cards_v3.md \
  --course "Mein Kurs" \
  --slug mein-kurs
```

Das Skript:
- parst die Markdown-Karten
- prüft die nötigen Notiztypen/Felder
- lädt referenzierte Bilder via AnkiConnect hoch
- erstellt die Zieldecks bei Bedarf automatisch
- legt anschließend die Notizen direkt an

## Relevante Dateien

- [SKILL.md](./SKILL.md): Hauptanleitung für die Kartenerstellung
- [references/tsv-export.md](./references/tsv-export.md): Regeln für den finalen TSV-Export
- [scripts/export_tsv.py](./scripts/export_tsv.py): TSV-Exporter
- [scripts/preflight_check.py](./scripts/preflight_check.py): Vorabprüfung für Kartenentwürfe
