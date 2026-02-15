#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path


TSV_HEADER = "\n".join(
    [
        "#separator:Tab",
        "#html:true",
        "#deck column:3",
        "#notetype column:4",
        "#tags column:5",
        "",
    ]
)


@dataclass(frozen=True)
class Note:
    field1: str
    field2: str
    deck: str
    notetype: str  # Basic|Cloze
    tags: str


def _consume_fence(lines: list[str], i: int) -> tuple[str, list[str], int]:
    m = re.match(r"^```(\w+)\s*$", lines[i])
    if not m:
        raise ValueError(f"Expected fence at line {i+1}: {lines[i]!r}")
    fence_type = m.group(1)
    i += 1
    content: list[str] = []
    while i < len(lines) and lines[i].strip() != "```":
        content.append(lines[i])
        i += 1
    if i >= len(lines):
        raise ValueError(f"Unclosed fence for {fence_type}")
    return fence_type, content, i + 1


def _markdownish_to_html(text: str) -> str:
    text = text.replace("\\n", "\n").replace('\\"', '"')

    text = re.sub(r"\*\*(.+?)\*\*", r"@@B_START@@\1@@B_END@@", text)
    text = text.replace("\t", "    ")

    text = html.escape(text, quote=False)
    text = text.replace("@@B_START@@", "<b>").replace("@@B_END@@", "</b>")

    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    return text.strip()


def _heading_to_component(line: str) -> str | None:
    m = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
    if not m:
        return None
    return m.group(2).strip()


def _context_prefix_html(l1: str | None, l2: str | None, l3: str | None) -> str:
    parts = [p for p in (l1, l2, l3) if p]
    if not parts:
        return ""
    context_text = " / ".join(parts)
    context_text = html.escape(context_text, quote=False)
    return (
        '<div style="font-size:0.75em;color:#666;line-height:1.2;margin-bottom:6px;">'
        f"{context_text}</div>"
    )


def parse_notes(md_path: Path, course_name: str, course_slug: str, deck_prefix: str) -> list[Note]:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    notes: list[Note] = []

    l1: str | None = None
    l2: str | None = None
    l3: str | None = None

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("# "):
            l1 = _heading_to_component(line)
            l2 = None
            l3 = None
            i += 1
            continue
        if line.startswith("## "):
            l2 = _heading_to_component(line)
            l3 = None
            i += 1
            continue
        if line.startswith("### "):
            l3 = _heading_to_component(line)
            i += 1
            continue

        if re.match(r"^\*\*.+:\*\*\s*$", line):
            if i + 1 >= len(lines) or not lines[i + 1].startswith("```"):
                i += 1
                continue

            fence_type, q_lines, j = _consume_fence(lines, i + 1)
            if fence_type not in ("Frage", "Cloze"):
                raise ValueError(f"Unexpected fence type after title: {fence_type}")

            a_lines: list[str] = []
            note_type = "Basic"
            if fence_type == "Cloze":
                note_type = "Cloze"
                k = j
            else:
                if j >= len(lines) or not lines[j].startswith("```"):
                    raise ValueError("Expected Antwort fence after Frage")
                a_type, a_lines, k = _consume_fence(lines, j)
                if a_type != "Antwort":
                    raise ValueError(f"Expected Antwort fence, got {a_type}")

            tags_from_md: list[str] = []
            t = k
            while t < len(lines):
                if not lines[t].strip():
                    t += 1
                    break
                if lines[t].startswith("#") or re.match(r"^\*\*.+:\*\*\s*$", lines[t]):
                    break
                m_tag = re.match(r"^Tags:\s*(.+?)\s*$", lines[t])
                if m_tag:
                    tags_from_md.extend(m_tag.group(1).split())
                t += 1

            deck_parts = [deck_prefix, course_name]
            if l1:
                deck_parts.append(l1)
            if l2:
                deck_parts.append(l2)
            if l3:
                deck_parts.append(l3)
            deck = "::".join(deck_parts)

            q_raw = "\n".join(q_lines).strip()
            a_raw = "\n".join(a_lines).strip()

            add_image = ("Grafik/Diagramm:" in q_raw) or ("Grafik/Diagramm:" in a_raw)
            add_image = add_image or q_raw.strip().startswith("IMAGE OCCLUSION:")

            tag_set = {f"course::{course_slug}"}
            for tag in tags_from_md:
                tag_set.add(tag)
            if add_image:
                tag_set.add("Add-Image")

            context_html = _context_prefix_html(l1, l2, l3)
            field1 = context_html + _markdownish_to_html(q_raw)
            field2 = "" if note_type == "Cloze" else _markdownish_to_html(a_raw)

            notes.append(Note(field1=field1, field2=field2, deck=deck, notetype=note_type, tags=" ".join(sorted(tag_set))))

            i = t
            continue

        i += 1

    return notes


def write_tsv(notes: list[Note], out_path: Path) -> None:
    for n in notes:
        if "SEITE_FEHLT" in n.field1 or "SEITE_FEHLT" in n.field2:
            raise SystemExit("Found SEITE_FEHLT in notes; refusing to export.")

    rows: list[str] = [TSV_HEADER]
    for n in notes:
        if n.notetype not in ("Basic", "Cloze"):
            raise ValueError(f"Invalid notetype: {n.notetype}")
        rows.append("\t".join([n.field1, n.field2, n.deck, n.notetype, n.tags]))

    out_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input markdown cards file")
    ap.add_argument("--out", dest="out", required=True, help="Output TSV path")
    ap.add_argument("--course", default="Kurs", help="Course name for deck path")
    ap.add_argument("--slug", required=True, help="Course slug for tags, e.g. kurs-slug")
    ap.add_argument("--deck-prefix", default="Import", help="Deck root prefix")
    args = ap.parse_args()

    notes = parse_notes(
        Path(args.inp),
        course_name=args.course,
        course_slug=args.slug,
        deck_prefix=args.deck_prefix,
    )
    write_tsv(notes, Path(args.out))
    print(f"Wrote {len(notes)} notes to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
