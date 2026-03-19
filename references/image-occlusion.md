# Image Occlusion (Template-Karten)

Ziel: Visuelle Inhalte (Diagramme, Tabellen, Schaubilder) effizient in Anki nutzbar machen, ohne dass man Zahlen/Details aus Bildern "raten" muss.

## Standard-Pattern

1. Erstelle eine Template-Karte, die klar beschreibt, welche Folie/Grafik als Image Occlusion in Anki angelegt werden soll.
2. Markiere diese Karte mit Tag `Add-Image`.

Beispiel:

````markdown
**Schema X (Image Occlusion Template):**
```Question
**Schema X (Image Occlusion Template):**
IMAGE OCCLUSION: Relevante Grafik/Abbildung aus dem Kursmaterial als Image Occlusion in Anki anlegen.
```
```Answer
Hinweis: Diese Karte ist absichtlich ein Template für eine Image-Occlusion-Karte.
Quelle: S. X
Grafik/Diagramm: <Kurzbezeichnung>, S. X
```
```Extra
Kurze Einordnung oder Hinweis zur Bildnutzung.
```
Image: ./assets/schema-x.png
Tags: Add-Image
````

## Regel

- Sobald eine Karte `Grafik/Diagramm:` referenziert, muss sie in Anki Tag `Add-Image` tragen (wird beim TSV-Export erzwungen).
- Das zugehörige Bild soll unter der Karte explizit referenziert werden.
- Das eigentliche Maskieren der Image Occlusion erfolgt weiterhin in Anki; die Pipeline bereitet nur Bild und Karteninhalt vor.
