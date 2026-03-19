# anki-course-card-creator

Dieses Skill ist auf einen Workflow mit zwei bevorzugten Anki-Notiztypen ausgelegt:
- `Basic`
- `Enhanced Cloze 2.1 v2`

## Voraussetzungen für optimale Nutzung

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

## Aktuelle Export-Logik

Der lokale Exporter unterstützt:
- `Basic`
- `Enhanced Cloze 2.1 v2`
- Legacy-`Cloze` für ältere Bestände

Markdown-Entwürfe können daher gemischt sein. Beim Export werden Decks, Notiztyp und Tags automatisch gesetzt.

## Relevante Dateien

- [SKILL.md](./SKILL.md): Hauptanleitung für die Kartenerstellung
- [references/tsv-export.md](./references/tsv-export.md): Regeln für den finalen TSV-Export
- [scripts/export_tsv.py](./scripts/export_tsv.py): TSV-Exporter
- [scripts/preflight_check.py](./scripts/preflight_check.py): Vorabprüfung für Kartenentwürfe
