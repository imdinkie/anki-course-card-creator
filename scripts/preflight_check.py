#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CardIssue:
    card_title: str
    issue: str


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


def _check_heading(line: str) -> str | None:
    m = re.match(r"^(#{1,3})\s+(\d{2})\s+.+$", line)
    if not m:
        return "Heading must start with two-digit number, e.g. '# 01 Thema' or '## 01 Unterthema'."
    return None


def preflight(md_path: Path) -> tuple[list[str], list[CardIssue]]:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    warnings: list[str] = []
    issues: list[CardIssue] = []

    saw_heading = False
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("#"):
            saw_heading = True
            err = _check_heading(line)
            if err:
                warnings.append(f"{md_path.name}:{i+1}: {err} Got: {line!r}")
            i += 1
            continue

        m_title = re.match(r"^\*\*(.+):\*\*\s*$", line)
        if m_title:
            card_title = m_title.group(1)
            if i + 1 >= len(lines) or not lines[i + 1].startswith("```"):
                issues.append(CardIssue(card_title, "Missing code fence after card title."))
                i += 1
                continue

            fence_type, q_lines, j = _consume_fence(lines, i + 1)
            if fence_type not in ("Frage", "Cloze"):
                issues.append(CardIssue(card_title, f"Unexpected fence type {fence_type!r} after title."))
                i = j
                continue

            a_lines: list[str] = []
            k = j
            if fence_type == "Frage":
                if j >= len(lines) or not lines[j].startswith("```"):
                    issues.append(CardIssue(card_title, "Missing Antwort fence after Frage."))
                    i = j
                    continue
                a_type, a_lines, k = _consume_fence(lines, j)
                if a_type != "Antwort":
                    issues.append(CardIssue(card_title, f"Expected Antwort fence, got {a_type!r}."))

            content = "\n".join(q_lines + a_lines)
            if "SEITE_FEHLT" in content:
                issues.append(CardIssue(card_title, "Contains SEITE_FEHLT (must be resolved before export)."))

            if "Quelle:" not in content:
                issues.append(CardIssue(card_title, "Missing 'Quelle:' line."))

            # Style/anti-pattern warnings (do not fail the run).
            if re.search(r"\bklausurrelevant\b", content, flags=re.IGNORECASE):
                warnings.append(
                    f"{md_path.name}:{i+1}: Avoid 'klausurrelevant' in card wording. Rewrite to an objective content question. Title: {card_title!r}"
                )
            if re.search(r"warum\s+ist\s+.+?pr(?:ue|ü)fungsrelevant", content, flags=re.IGNORECASE):
                warnings.append(
                    f"{md_path.name}:{i+1}: Avoid 'Warum ist ... prüfungsrelevant?'. Prefer a content/definition/application question or Image Occlusion for visuals. Title: {card_title!r}"
                )
            if re.search(r"\blaut\s+(folie|skript)\b", content, flags=re.IGNORECASE):
                warnings.append(
                    f"{md_path.name}:{i+1}: Avoid 'laut Folie/Skript'. Provide the needed context directly in the question. Title: {card_title!r}"
                )

            if "Grafik/Diagramm:" in content:
                warnings.append(
                    f"{md_path.name}:{i+1}: Card references Grafik/Diagramm; exporter will enforce tag Add-Image. Title: {card_title!r}"
                )

            i = k
            continue

        i += 1

    if not saw_heading:
        warnings.append(f"{md_path.name}: No headings (#/##) found; deck hierarchy will be flat/unsorted.")

    return warnings, issues


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Input markdown cards file")
    args = ap.parse_args()

    warnings, issues = preflight(Path(args.inp))
    for w in warnings:
        print(f"WARNING: {w}")
    for iss in issues:
        print(f"ERROR: {iss.card_title}: {iss.issue}")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
