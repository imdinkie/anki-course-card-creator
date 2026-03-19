#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path


TSV_HEADER = "\n".join(
    [
        "#separator:Tab",
        "#html:true",
        "#deck column:6",
        "#notetype column:7",
        "#tags column:8",
        "",
    ]
)

ENHANCED_CLOZE_NOTETYPE = "Enhanced Cloze 2.1 v2"
IMAGE_LINE_RE = re.compile(r"^Image:\s*(.+?)\s*$")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
OBSIDIAN_IMAGE_RE = re.compile(r"!\[\[([^\]#|]+)(?:[|#][^\]]+)?\]\]")


@dataclass(frozen=True)
class Note:
    title: str
    fields: tuple[str, str, str, str, str]
    deck: str
    notetype: str  # Basic|Enhanced Cloze 2.1 v2|Cloze
    tags: str
    media_paths: tuple[Path, ...]


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


def _inline_markdown_to_html(text: str) -> str:
    text = text.replace("\\n", "\n").replace('\\"', '"')
    text = text.replace("\t", "    ")
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def _list_item_info(line: str) -> tuple[int, str, str] | None:
    stripped = line.lstrip(" ")
    indent = (len(line) - len(stripped)) // 2

    if re.match(r"^[-*]\s+", stripped):
        return indent, "ul", re.sub(r"^[-*]\s+", "", stripped, count=1)

    if re.match(r"^\d+[.)]\s+", stripped):
        return indent, "ol", re.sub(r"^\d+[.)]\s+", "", stripped, count=1)

    return None


def _markdownish_to_html(text: str) -> str:
    if not text.strip():
        return ""

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    parts: list[str] = []
    list_stack: list[tuple[int, str]] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        joined = "<br>".join(_inline_markdown_to_html(line) for line in paragraph)
        parts.append(f"<div>{joined}</div>")
        paragraph = []

    def close_lists(target_indent: int = -1) -> None:
        while list_stack and list_stack[-1][0] >= target_indent:
            _, list_type = list_stack.pop()
            parts.append(f"</{list_type}>")

    for raw_line in lines:
        if not raw_line.strip():
            flush_paragraph()
            close_lists(0)
            continue

        item = _list_item_info(raw_line)
        if item:
            flush_paragraph()
            indent, list_type, content = item

            while list_stack and list_stack[-1][0] > indent:
                _, closing_type = list_stack.pop()
                parts.append(f"</{closing_type}>")

            if list_stack and list_stack[-1][0] == indent and list_stack[-1][1] != list_type:
                _, closing_type = list_stack.pop()
                parts.append(f"</{closing_type}>")

            if not list_stack or list_stack[-1][0] < indent or list_stack[-1][1] != list_type:
                parts.append(f"<{list_type}>")
                list_stack.append((indent, list_type))

            parts.append(f"<li>{_inline_markdown_to_html(content)}</li>")
            continue

        close_lists(0)
        paragraph.append(raw_line)

    flush_paragraph()
    close_lists(0)
    return "".join(parts).strip()


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


def _read_optional_fence_block(lines: list[str], start: int) -> tuple[dict[str, list[str]], int]:
    blocks: dict[str, list[str]] = {}
    i = start
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            break
        if lines[i].startswith("#") or re.match(r"^\*\*.+:\*\*\s*$", lines[i]):
            break
        if not lines[i].startswith("```"):
            break
        fence_type, fence_lines, i = _consume_fence(lines, i)
        blocks[fence_type] = fence_lines
    return blocks, i


def _extract_image_refs(line: str) -> list[str]:
    refs: list[str] = []
    m = IMAGE_LINE_RE.match(line.strip())
    if m:
        refs.append(m.group(1).strip())

    refs.extend(match.group(1).strip() for match in MD_IMAGE_RE.finditer(line))
    refs.extend(match.group(1).strip() for match in OBSIDIAN_IMAGE_RE.finditer(line))
    return refs


def _resolve_media_paths(md_path: Path, image_refs: list[str]) -> tuple[Path, ...]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    for raw in image_refs:
        if raw.startswith(("http://", "https://")):
            continue
        path = (md_path.parent / raw).resolve()
        if path in seen:
            continue
        seen.add(path)
        resolved.append(path)
    return tuple(resolved)


def _media_target_index(note_type: str) -> int:
    if note_type == "Basic":
        return 2
    if note_type == ENHANCED_CLOZE_NOTETYPE:
        return 3
    if note_type == "Cloze":
        return 1
    raise ValueError(f"Unsupported notetype for media injection: {note_type}")


def _image_html(filename: str) -> str:
    escaped = html.escape(filename, quote=True)
    return f'<div><img src="{escaped}"></div>'


def _prepend_html(existing: str, prefix_html: str) -> str:
    if not prefix_html:
        return existing
    if not existing:
        return prefix_html
    return prefix_html + existing


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", ascii_only).strip("-").lower()
    return safe or "image"


def _planned_media_name(path: Path) -> str:
    digest = hashlib.sha1(path.read_bytes()).hexdigest()[:12]
    stem = _slugify(path.stem)
    suffix = path.suffix.lower() or ".bin"
    return f"{stem}-{digest}{suffix}"


def _plan_media_filenames(notes: list[Note]) -> dict[Path, str]:
    mapping: dict[Path, str] = {}
    for note in notes:
        for media_path in note.media_paths:
            if not media_path.exists():
                raise SystemExit(f"Referenced media file does not exist: {media_path}")
            if media_path not in mapping:
                mapping[media_path] = _planned_media_name(media_path)
    return mapping


def inject_media(notes: list[Note], media_name_map: dict[Path, str]) -> list[Note]:
    enriched: list[Note] = []
    for note in notes:
        filenames = [media_name_map[path] for path in note.media_paths]
        if not filenames:
            enriched.append(note)
            continue

        target_idx = _media_target_index(note.notetype)
        prefix_html = "".join(_image_html(filename) for filename in filenames)
        fields = list(note.fields)
        fields[target_idx] = _prepend_html(fields[target_idx], prefix_html)
        enriched.append(replace(note, fields=tuple(fields)))
    return enriched


def create_media_bundle(media_name_map: dict[Path, str], bundle_dir: Path) -> list[Path]:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for src, out_name in sorted(media_name_map.items(), key=lambda item: item[1]):
        dest = bundle_dir / out_name
        shutil.copy2(src, dest)
        copied.append(dest)
    return copied


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

        m_title = re.match(r"^\*\*(.+):\*\*\s*$", line)
        if not m_title:
            i += 1
            continue

        card_title = m_title.group(1)
        if i + 1 >= len(lines) or not lines[i + 1].startswith("```"):
            i += 1
            continue

        fence_type, q_lines, j = _consume_fence(lines, i + 1)
        if fence_type not in ("Frage", "Question", "Cloze", "EnhancedCloze"):
            raise ValueError(f"Unexpected fence type after title: {fence_type}")

        note_type = "Basic"
        basic_notes_lines: list[str] = []
        enhanced_note_lines: list[str] = []
        mnemonic_lines: list[str] = []
        extra_lines: list[str] = []
        answer_lines: list[str] = []
        legacy_back_extra_lines: list[str] = []

        if fence_type in ("Frage", "Question"):
            if j >= len(lines) or not lines[j].startswith("```"):
                raise ValueError("Expected Antwort/Answer fence after Frage/Question")
            a_type, answer_lines, k = _consume_fence(lines, j)
            if a_type not in ("Antwort", "Answer"):
                raise ValueError(f"Expected Antwort/Answer fence, got {a_type}")
            extra_blocks, k = _read_optional_fence_block(lines, k)
            basic_notes_lines = extra_blocks.get("Notes", [])
        elif fence_type == "EnhancedCloze":
            note_type = ENHANCED_CLOZE_NOTETYPE
            extra_blocks, k = _read_optional_fence_block(lines, j)
            enhanced_note_lines = extra_blocks.get("Note", [])
            mnemonic_lines = extra_blocks.get("Mnemonic", [])
            extra_lines = extra_blocks.get("Extra", [])
        else:
            note_type = "Cloze"
            extra_blocks, k = _read_optional_fence_block(lines, j)
            legacy_back_extra_lines = extra_blocks.get("BackExtra", [])

        tags_from_md: list[str] = []
        image_refs: list[str] = []
        t = k
        while t < len(lines) and not lines[t].strip():
            t += 1
        while t < len(lines):
            if lines[t].startswith("#") or re.match(r"^\*\*.+:\*\*\s*$", lines[t]):
                break
            m_tag = re.match(r"^Tags:\s*(.+?)\s*$", lines[t])
            if m_tag:
                tags_from_md.extend(m_tag.group(1).split())
            image_refs.extend(_extract_image_refs(lines[t]))
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
        a_raw = "\n".join(answer_lines).strip()
        basic_notes_raw = "\n".join(basic_notes_lines).strip()
        enhanced_note_raw = "\n".join(enhanced_note_lines).strip()
        mnemonic_raw = "\n".join(mnemonic_lines).strip()
        extra_raw = "\n".join(extra_lines).strip()
        legacy_back_extra_raw = "\n".join(legacy_back_extra_lines).strip()

        add_image = any(
            "Grafik/Diagramm:" in raw
            for raw in (
                q_raw,
                a_raw,
                basic_notes_raw,
                enhanced_note_raw,
                mnemonic_raw,
                extra_raw,
                legacy_back_extra_raw,
            )
        )
        add_image = add_image or q_raw.strip().startswith("IMAGE OCCLUSION:")

        tag_set = {f"course::{course_slug}"}
        for tag in tags_from_md:
            tag_set.add(tag)
        if add_image:
            tag_set.add("Add-Image")

        context_html = _context_prefix_html(l1, l2, l3)
        fields = ("", "", "", "", "")

        if note_type == "Basic":
            fields = (
                context_html + _markdownish_to_html(q_raw),
                _markdownish_to_html(a_raw),
                _markdownish_to_html(basic_notes_raw),
                "",
                "",
            )
        elif note_type == ENHANCED_CLOZE_NOTETYPE:
            fields = (
                context_html + _markdownish_to_html(q_raw),
                _markdownish_to_html(enhanced_note_raw),
                _markdownish_to_html(mnemonic_raw),
                _markdownish_to_html(extra_raw),
                "",
            )
        else:
            fields = (
                context_html + _markdownish_to_html(q_raw),
                _markdownish_to_html(legacy_back_extra_raw),
                "",
                "",
                "",
            )

        notes.append(
            Note(
                title=card_title,
                fields=fields,
                deck=deck,
                notetype=note_type,
                tags=" ".join(sorted(tag_set)),
                media_paths=_resolve_media_paths(md_path, image_refs),
            )
        )

        i = t

    return notes


def prepare_export(
    md_path: Path,
    course_name: str,
    course_slug: str,
    deck_prefix: str,
    bundle_dir: Path | None = None,
) -> tuple[list[Note], dict[Path, str], Path | None]:
    notes = parse_notes(md_path, course_name=course_name, course_slug=course_slug, deck_prefix=deck_prefix)
    media_name_map = _plan_media_filenames(notes)
    bundle_target = bundle_dir
    if media_name_map:
        if bundle_target is None:
            raise ValueError("bundle_dir must be provided when notes reference media.")
        create_media_bundle(media_name_map, bundle_target)
        notes = inject_media(notes, media_name_map)
    return notes, media_name_map, bundle_target if media_name_map else None


def write_tsv(notes: list[Note], out_path: Path) -> None:
    for n in notes:
        if any("SEITE_FEHLT" in field for field in n.fields):
            raise SystemExit("Found SEITE_FEHLT in notes; refusing to export.")

    rows: list[str] = [TSV_HEADER]
    ordered_notes = sorted(notes, key=lambda n: (sum(bool(field) for field in n.fields), n.notetype), reverse=True)

    for n in ordered_notes:
        if n.notetype not in ("Basic", ENHANCED_CLOZE_NOTETYPE, "Cloze"):
            raise ValueError(f"Invalid notetype: {n.notetype}")
        rows.append("\t".join([*n.fields, n.deck, n.notetype, n.tags]))

    out_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input markdown cards file")
    ap.add_argument("--out", dest="out", required=True, help="Output TSV path")
    ap.add_argument("--course", default="Kurs", help="Course name for deck path")
    ap.add_argument("--slug", required=True, help="Course slug for tags, e.g. kurs-slug")
    ap.add_argument("--deck-prefix", default="Import", help="Deck root prefix")
    ap.add_argument("--media-bundle", help="Optional output dir for the final flat media bundle")
    args = ap.parse_args()

    out_path = Path(args.out)
    bundle_dir = Path(args.media_bundle) if args.media_bundle else out_path.parent / "media_bundle"

    notes, media_name_map, actual_bundle = prepare_export(
        Path(args.inp),
        course_name=args.course,
        course_slug=args.slug,
        deck_prefix=args.deck_prefix,
        bundle_dir=bundle_dir,
    )
    write_tsv(notes, out_path)
    print(f"Wrote {len(notes)} notes to {args.out}")
    if media_name_map and actual_bundle is not None:
        print(f"Prepared {len(media_name_map)} media files in {actual_bundle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
