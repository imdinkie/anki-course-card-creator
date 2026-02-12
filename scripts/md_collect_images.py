#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImageRef:
    md_file: Path
    raw: str
    resolved: Path
    exists: bool


RE_MD_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
RE_OBSIDIAN_EMBED = re.compile(r"!\[\[([^\]#|]+)(?:[|#][^\]]+)?\]\]")
RE_HTML_IMG = re.compile(r"<img[^>]*src=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)


def _collect_from_text(md_path: Path, text: str) -> list[ImageRef]:
    refs: list[ImageRef] = []
    base = md_path.parent

    for m in RE_MD_IMAGE.finditer(text):
        raw = m.group(1).strip()
        if raw.startswith("http://") or raw.startswith("https://"):
            refs.append(ImageRef(md_path, raw, Path(raw), exists=False))
            continue
        resolved = (base / raw).resolve()
        refs.append(ImageRef(md_path, raw, resolved, resolved.exists()))

    for m in RE_OBSIDIAN_EMBED.finditer(text):
        raw = m.group(1).strip()
        resolved = (base / raw).resolve()
        refs.append(ImageRef(md_path, raw, resolved, resolved.exists()))

    for m in RE_HTML_IMG.finditer(text):
        raw = m.group(1).strip()
        if raw.startswith("http://") or raw.startswith("https://"):
            refs.append(ImageRef(md_path, raw, Path(raw), exists=False))
            continue
        resolved = (base / raw).resolve()
        refs.append(ImageRef(md_path, raw, resolved, resolved.exists()))

    return refs


def collect(paths: list[Path]) -> list[ImageRef]:
    md_files: list[Path] = []
    for p in paths:
        if p.is_dir():
            md_files.extend(sorted(p.rglob("*.md")))
        else:
            md_files.append(p)

    all_refs: list[ImageRef] = []
    for md in md_files:
        try:
            text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = md.read_text(encoding="utf-8", errors="replace")
        all_refs.extend(_collect_from_text(md, text))

    seen = set()
    uniq: list[ImageRef] = []
    for r in all_refs:
        key = (str(r.md_file), r.raw, str(r.resolved))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="Markdown file(s) or directories")
    args = ap.parse_args()

    refs = collect([Path(p) for p in args.paths])
    missing = [r for r in refs if not r.exists and not (r.raw.startswith("http://") or r.raw.startswith("https://"))]
    remote = [r for r in refs if r.raw.startswith("http://") or r.raw.startswith("https://")]

    for r in refs:
        status = "OK" if r.exists else ("REMOTE" if r.raw.startswith("http") else "MISSING")
        print(f"{status}\t{r.md_file}\t{r.raw}\t{r.resolved}")

    print()
    print(f"Total refs: {len(refs)}")
    print(f"Missing local: {len(missing)}")
    print(f"Remote: {len(remote)}")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

