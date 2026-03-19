#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

ENHANCED_CLOZE_NOTETYPE = "Enhanced Cloze 2.1 v2"
IMAGE_LINE_RE = re.compile(r"^Image:\s*(.+?)\s*$")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
OBSIDIAN_IMAGE_RE = re.compile(r"!\[\[([^\]#|]+)(?:[|#][^\]]+)?\]\]")


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


def _significant_words(text: str) -> set[str]:
    words = re.findall(r"[A-Za-zÄÖÜäöüß]{4,}", text.lower())
    stop = {
        "welche",
        "welcher",
        "welches",
        "warum",
        "wieso",
        "wodurch",
        "womit",
        "worin",
        "woraus",
        "nenne",
        "erkläre",
        "erklaere",
        "beschreibe",
        "karte",
        "konzept",
        "grundidee",
        "definition",
        "überblick",
        "ueberblick",
        "mechanismus",
        "strategie",
        "prozess",
        "modell",
        "theorie",
        "frage",
        "klausur",
        "image",
        "occlusion",
        "template",
    }
    return {w for w in words if w not in stop}


def _looks_like_answer_leakage(card_title: str, prompt: str) -> bool:
    title_words = _significant_words(card_title)
    prompt_words = _significant_words(prompt)
    if not title_words or not prompt_words:
        return False
    overlap = title_words & prompt_words
    return len(overlap) >= min(2, len(title_words))


def _has_explicit_question_prompt(lines: list[str]) -> bool:
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^\*\*.+\*\*$", stripped):
            continue
        if stripped.endswith("?"):
            return True
    return False


def _warn_if_long_comma_chain(content: str) -> bool:
    for line in content.splitlines():
        if line.count(",") >= 4 and not re.match(r"^\s*Quelle:", line):
            return True
    return False


def _extract_image_refs(line: str) -> list[str]:
    refs: list[str] = []
    m = IMAGE_LINE_RE.match(line.strip())
    if m:
        refs.append(m.group(1).strip())
    refs.extend(match.group(1).strip() for match in MD_IMAGE_RE.finditer(line))
    refs.extend(match.group(1).strip() for match in OBSIDIAN_IMAGE_RE.finditer(line))
    return refs


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
        if not m_title:
            i += 1
            continue

        card_title = m_title.group(1)
        if i + 1 >= len(lines) or not lines[i + 1].startswith("```"):
            issues.append(CardIssue(card_title, "Missing code fence after card title."))
            i += 1
            continue

        fence_type, q_lines, j = _consume_fence(lines, i + 1)
        if fence_type not in ("Frage", "Question", "Cloze", "EnhancedCloze"):
            issues.append(CardIssue(card_title, f"Unexpected fence type {fence_type!r} after title."))
            i = j
            continue

        answer_lines: list[str] = []
        notes_lines: list[str] = []
        note_lines: list[str] = []
        mnemonic_lines: list[str] = []
        extra_lines: list[str] = []
        legacy_back_extra_lines: list[str] = []
        k = j

        if fence_type in ("Frage", "Question"):
            if j >= len(lines) or not lines[j].startswith("```"):
                issues.append(CardIssue(card_title, "Missing Antwort/Answer fence after Frage/Question."))
                i = j
                continue
            a_type, answer_lines, k = _consume_fence(lines, j)
            if a_type not in ("Antwort", "Answer"):
                issues.append(CardIssue(card_title, f"Expected Antwort/Answer fence, got {a_type!r}."))
            blocks, k = _read_optional_fence_block(lines, k)
            notes_lines = blocks.get("Notes", [])
        elif fence_type == "EnhancedCloze":
            blocks, k = _read_optional_fence_block(lines, j)
            note_lines = blocks.get("Note", [])
            mnemonic_lines = blocks.get("Mnemonic", [])
            extra_lines = blocks.get("Extra", [])
        else:
            blocks, k = _read_optional_fence_block(lines, j)
            legacy_back_extra_lines = blocks.get("BackExtra", [])

        tags: list[str] = []
        image_refs: list[str] = []
        t = k
        while t < len(lines) and not lines[t].strip():
            t += 1
        while t < len(lines):
            if lines[t].startswith("#") or re.match(r"^\*\*.+:\*\*\s*$", lines[t]):
                break
            m_tag = re.match(r"^Tags:\s*(.+?)\s*$", lines[t])
            if m_tag:
                tags.extend(m_tag.group(1).split())
            image_refs.extend(_extract_image_refs(lines[t]))
            t += 1

        content = "\n".join(
            q_lines
            + answer_lines
            + notes_lines
            + note_lines
            + mnemonic_lines
            + extra_lines
            + legacy_back_extra_lines
        )
        if "SEITE_FEHLT" in content:
            issues.append(CardIssue(card_title, "Contains SEITE_FEHLT (must be resolved before export)."))

        if "Quelle:" not in content:
            issues.append(CardIssue(card_title, "Missing 'Quelle:' line."))

        if fence_type == "EnhancedCloze" and "{{c" not in "\n".join(q_lines):
            warnings.append(
                f"{md_path.name}:{i+1}: EnhancedCloze card without cloze markup detected. This is allowed, but verify that Basic would not be clearer. Title: {card_title!r}"
            )
        if fence_type == "EnhancedCloze" and not _has_explicit_question_prompt(q_lines):
            warnings.append(
                f"{md_path.name}:{i+1}: EnhancedCloze card without explicit guiding question detected. Keep a real question above the clozes. Title: {card_title!r}"
            )

        if fence_type == "Cloze":
            warnings.append(
                f"{md_path.name}:{i+1}: Legacy `Cloze` detected. Prefer `{ENHANCED_CLOZE_NOTETYPE}` for lists, mappings, or staged reveal. Title: {card_title!r}"
            )

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

        if re.search(r"warum\s+ist\s+.+?relevant", content, flags=re.IGNORECASE):
            warnings.append(
                f"{md_path.name}:{i+1}: Avoid relevance-framed cards when a concept/application card or Image Occlusion would test the material better. Title: {card_title!r}"
            )

        if "Grafik/Diagramm:" in content:
            warnings.append(
                f"{md_path.name}:{i+1}: Card references Grafik/Diagramm; exporter will enforce tag Add-Image. Title: {card_title!r}"
            )

        question_prompt = "\n".join(q_lines)
        if _looks_like_answer_leakage(card_title, question_prompt):
            warnings.append(
                f"{md_path.name}:{i+1}: Possible answer leakage from card title/question wording. Rewrite more indirectly if feasible. Title: {card_title!r}"
            )
        meta_fields = "\n".join(notes_lines + note_lines + mnemonic_lines + extra_lines + legacy_back_extra_lines)
        if re.search(
            r"\b(diese karte prüft|diese karte prueft|klausurnah|bewusst isoliert|die clozes sind absichtlich|die karte deckt bewusst)\b",
            meta_fields,
            flags=re.IGNORECASE,
        ):
            warnings.append(
                f"{md_path.name}:{i+1}: Avoid meta commentary about card design in Notes/Note/Mnemonic/Extra. Keep only content-related context. Title: {card_title!r}"
            )

        if _warn_if_long_comma_chain(content):
            warnings.append(
                f"{md_path.name}:{i+1}: Long comma-separated enumeration detected. Prefer bullet points or numbered lists for readability and HTML export. Title: {card_title!r}"
            )

        if fence_type == "EnhancedCloze":
            cloze_numbers = re.findall(r"\{\{c(\d+)::", "\n".join(q_lines))
            if cloze_numbers:
                max_group = max(cloze_numbers.count(num) for num in set(cloze_numbers))
                if max_group >= 4:
                    warnings.append(
                        f"{md_path.name}:{i+1}: Many elements share the same cloze number. Verify that the chunk is still genuinely one easy unit. Title: {card_title!r}"
                    )

        has_visual_reference = "Grafik/Diagramm:" in content or "\n".join(q_lines).strip().startswith("IMAGE OCCLUSION:")
        if has_visual_reference and not image_refs:
            warnings.append(
                f"{md_path.name}:{i+1}: Visual card without explicit image block. Add `Image: ./assets/...` or a markdown image under the card. Title: {card_title!r}"
            )
        if image_refs and not has_visual_reference:
            warnings.append(
                f"{md_path.name}:{i+1}: Image block found without `Grafik/Diagramm:` or `IMAGE OCCLUSION:` marker. Verify that the image is actually intended. Title: {card_title!r}"
            )
        for raw in image_refs:
            if raw.startswith(("http://", "https://")):
                warnings.append(
                    f"{md_path.name}:{i+1}: Remote image reference found ({raw}). Prefer local assets for portable exports. Title: {card_title!r}"
                )
                continue
            resolved = (md_path.parent / raw).resolve()
            if not resolved.exists():
                issues.append(CardIssue(card_title, f"Referenced image does not exist: {raw}"))

        i = t

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
