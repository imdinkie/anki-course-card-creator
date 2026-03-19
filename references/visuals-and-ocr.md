# Visuals: Diagramme, Tabellen, Screenshots

## Grundprinzip

1. Erst konzeptionell fragen: Welche Kernaussage transportiert die Visualisierung?
2. Zahlen/Detailwerte nur abfragen, wenn sie sicher extrahierbar sind (und wirklich prüfungsrelevant).
3. Wenn Details im Bild stecken: nutze bevorzugt Image Occlusion Templates statt fragiler OCR-Raterei.

## Praktische Extraktion (je nach Umgebung)

- PDF Text: `pdftotext -layout` kann Text liefern, der im PDF als Textobjekte enthalten ist.
- Rendering: `pdftoppm` für visuelle Kontrolle.
- OCR: nur wenn im System verfügbar (z. B. tesseract). Wenn nicht verfügbar: Fallback auf konzeptionelle Karten + Image Occlusion.

## Kartenregel

- Karten mit `Grafik/Diagramm:` müssen Tag `Add-Image` erhalten (im TSV wird das erzwungen).
