#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _detect_collection_media() -> Path:
    root = Path.home() / ".local" / "share" / "Anki2"
    candidates = sorted(root.glob("*/collection.media"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SystemExit("No collection.media directory found under ~/.local/share/Anki2. Pass --collection-media explicitly.")
    raise SystemExit(
        "Multiple collection.media directories found. Pass --collection-media explicitly:\n"
        + "\n".join(str(path) for path in candidates)
    )


def copy_bundle(bundle_dir: Path, collection_media: Path) -> int:
    if not bundle_dir.exists():
        raise SystemExit(f"Bundle directory does not exist: {bundle_dir}")
    if not bundle_dir.is_dir():
        raise SystemExit(f"Bundle path is not a directory: {bundle_dir}")
    collection_media.mkdir(parents=True, exist_ok=True)

    copied = 0
    for src in sorted(bundle_dir.iterdir()):
        if not src.is_file():
            continue
        shutil.copy2(src, collection_media / src.name)
        copied += 1
    return copied


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, help="Path to the generated media_bundle directory")
    ap.add_argument("--collection-media", help="Target collection.media directory (auto-detect if omitted)")
    args = ap.parse_args()

    bundle_dir = Path(args.bundle)
    target = Path(args.collection_media).expanduser() if args.collection_media else _detect_collection_media()
    copied = copy_bundle(bundle_dir, target)
    print(f"Copied {copied} files to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
