# Markdown-Inhalte: Bilder und Embeds

Wenn Kursmaterial auch aus `.md`-Dateien besteht, koennen dort Bilder eingebettet oder verlinkt sein. Diese Visuals gehoeren zum Fachinhalt und muessen in Summary/Karten inhaltlich beruecksichtigt werden.

## Typische Syntax

- Standard Markdown: `![](path/to/image.png)` oder `![alt](path/to/image.png)`
- Obsidian Embed: `![[image.png]]` (optional mit Alias, z.B. `![[image.png|600]]`)
- HTML: `<img src=\"path/to/image.png\">`

## Workflow

1. Sammle referenzierte Bilder (z.B. via `scripts/md_collect_images.py`).
2. Oeffne/render die Bilder und notiere die Kernaussage pro Bild.
3. Erzeuge Karten:
   - konzeptionelle Karte zur Bildaussage
   - ggf. Image Occlusion Template, wenn Details im Bild geprueft werden sollen
4. Wenn in der Karte `Grafik/Diagramm:` referenziert wird: Tag `Add-Image` setzen.
