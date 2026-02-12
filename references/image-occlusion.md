# Image Occlusion (Template-Karten)

Ziel: Visuelle Inhalte (Diagramme, Tabellen, Schaubilder) effizient in Anki nutzbar machen, ohne dass man Zahlen/Details aus Bildern "raten" muss.

## Standard-Pattern

1. Erstelle eine Template-Karte, die klar beschreibt, welche Folie/Grafik als Image Occlusion in Anki angelegt werden soll.
2. Markiere diese Karte mit Tag `Add-Image`.

Beispiel:

````markdown
**Schema X (Image Occlusion Template):**
```Frage
**Schema X (Image Occlusion Template):**
IMAGE OCCLUSION: Relevante Grafik/Abbildung aus dem Kursmaterial als Image Occlusion in Anki anlegen.
```
```Antwort
Hinweis: Diese Karte ist absichtlich ein Template fuer eine Image-Occlusion-Karte.
Quelle: S. X
Grafik/Diagramm: <Kurzbezeichnung>, S. X
```
Tags: Add-Image
````

## Regel

- Sobald eine Karte `Grafik/Diagramm:` referenziert, muss sie in Anki Tag `Add-Image` tragen (wird beim TSV-Export erzwungen).
