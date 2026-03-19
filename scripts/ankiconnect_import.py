#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

from export_tsv import ENHANCED_CLOZE_NOTETYPE, _plan_media_filenames, inject_media, parse_notes


DEFAULT_URL = "http://127.0.0.1:8765"


def invoke(action: str, params: dict, url: str) -> object:
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach AnkiConnect at {url}: {exc}") from exc

    if data.get("error"):
        raise SystemExit(f"AnkiConnect action {action!r} failed: {data['error']}")
    return data.get("result")


def ensure_model_fields(url: str) -> None:
    models = invoke("modelNames", {}, url)
    required = {
        "Basic": ["Front", "Back", "Notes"],
        "Cloze": ["Text", "Back Extra"],
        ENHANCED_CLOZE_NOTETYPE: ["Content", "Note", "Mnemonics", "Extra", "Cloze99"],
    }
    for model, expected in required.items():
        if model not in models:
            raise SystemExit(f"Required note type missing in Anki: {model}")
        actual = invoke("modelFieldNames", {"modelName": model}, url)
        missing = [field for field in expected if field not in actual]
        if missing:
            raise SystemExit(f"Note type {model} is missing required fields: {missing}")


def upload_media(media_name_map: dict[Path, str], url: str) -> None:
    for path, filename in sorted(media_name_map.items(), key=lambda item: item[1]):
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        invoke("storeMediaFile", {"filename": filename, "data": encoded}, url)


def note_payload(note) -> dict:
    if note.notetype == "Basic":
        fields = {
            "Front": note.fields[0],
            "Back": note.fields[1],
            "Notes": note.fields[2],
        }
    elif note.notetype == ENHANCED_CLOZE_NOTETYPE:
        fields = {
            "Content": note.fields[0],
            "Note": note.fields[1],
            "Mnemonics": note.fields[2],
            "Extra": note.fields[3],
            "Cloze99": note.fields[4],
        }
    elif note.notetype == "Cloze":
        fields = {
            "Text": note.fields[0],
            "Back Extra": note.fields[1],
        }
    else:
        raise SystemExit(f"Unsupported note type for import: {note.notetype}")

    return {
        "deckName": note.deck,
        "modelName": note.notetype,
        "fields": fields,
        "tags": note.tags.split(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input markdown cards file")
    ap.add_argument("--course", default="Kurs", help="Course name for deck path")
    ap.add_argument("--slug", required=True, help="Course slug for tags, e.g. kurs-slug")
    ap.add_argument("--deck-prefix", default="Import", help="Deck root prefix")
    ap.add_argument("--url", default=DEFAULT_URL, help="AnkiConnect endpoint URL")
    args = ap.parse_args()

    invoke("version", {}, args.url)
    ensure_model_fields(args.url)

    notes = parse_notes(Path(args.inp), args.course, args.slug, args.deck_prefix)
    media_name_map = _plan_media_filenames(notes)
    upload_media(media_name_map, args.url)
    enriched_notes = inject_media(notes, media_name_map)
    for deck in sorted({note.deck for note in enriched_notes}):
        invoke("createDeck", {"deck": deck}, args.url)
    payload = [note_payload(note) for note in enriched_notes]

    can_add = invoke("canAddNotes", {"notes": payload}, args.url)
    blocked = [idx for idx, ok in enumerate(can_add) if not ok]
    if blocked:
        raise SystemExit(f"Anki rejected notes at indices: {blocked}")

    added = invoke("addNotes", {"notes": payload}, args.url)
    created = sum(1 for note_id in added if note_id is not None)
    print(f"Uploaded {len(media_name_map)} media files and created {created} notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
