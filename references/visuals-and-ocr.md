# Visuals: Diagramme, Tabellen, Screenshots

## Grundprinzip

1. Erst konzeptionell fragen: Welche Kernaussage transportiert die Visualisierung?
2. Zahlen/Detailwerte nur abfragen, wenn sie sicher extrahierbar sind (und wirklich pruefungsrelevant).
3. Wenn Details im Bild stecken: nutze bevorzugt Image Occlusion Templates statt fragiler OCR-Raterei.

## Praktische Extraktion (je nach Umgebung)

- PDF Text: `pdftotext -layout` kann Text liefern, der im PDF als Textobjekte enthalten ist.
- Rendering: `pdftoppm` fuer visuelle Kontrolle.
- OCR: nur wenn im System verfuegbar (z.B. tesseract). Wenn nicht verfuegbar: fallback auf konzeptionelle Karten + Image Occlusion.

## Kartenregel

- Karten mit `Grafik/Diagramm:` muessen Tag `Add-Image` erhalten (im TSV wird das erzwungen).
