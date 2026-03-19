#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


DEFAULT_URL = "http://127.0.0.1:8765"


def invoke(action: str, params: dict, url: str) -> object:
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach AnkiConnect at {url}: {exc}") from exc

    if data.get("error"):
        raise SystemExit(f"AnkiConnect action {action!r} failed: {data['error']}")
    return data.get("result")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL, help="AnkiConnect endpoint URL")
    args = ap.parse_args()

    version = invoke("version", {}, args.url)
    models = invoke("modelNames", {}, args.url)
    print(f"AnkiConnect version: {version}")

    required_models = ["Basic", "Cloze", "Enhanced Cloze 2.1 v2"]
    for model in required_models:
        if model in models:
            fields = invoke("modelFieldNames", {"modelName": model}, args.url)
            print(f"{model}: {fields}")
        else:
            print(f"{model}: NOT FOUND")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
