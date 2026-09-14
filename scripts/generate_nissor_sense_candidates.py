from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

FIELDS = [
    "sense_candidate_id",
    "structured_id",
    "source_record_id",
    "historical_headword",
    "historical_part_of_speech",
    "source_sense_id",
    "candidate_index",
    "candidate_gloss_en",
    "split_trigger",
    "candidate_status",
    "current_semantic_status",
    "requires_human_review",
]

SPLIT_RE = re.compile(r"\s*(;|—)\s*")


def split_gloss(gloss: str, split_status: str) -> list[tuple[str, str]]:
    text = (gloss or "").strip()
    if not text:
        return [("", "empty_historical_gloss")]
    if split_status != "needs_semantic_split":
        return [(text, "no_automatic_split")]

    parts = SPLIT_RE.split(text)
    output: list[tuple[str, str]] = []
    trigger = ""
    for part in parts:
        if part in {";", "—"}:
            trigger = "semicolon" if part == ";" else "em_dash"
            continue
        segment = part.strip()
        if not segment:
            continue
        output.append((segment, trigger or "initial_segment"))
        trigger = ""

    # The segments are review candidates only. Punctuation can separate examples,
    # usage notes, or POS changes rather than true lexical senses.
    return output or [(text, "split_failed_preserve_original")]


def build_candidates(structured_path: Path) -> list[dict[str, str]]:
    with structured_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    output: list[dict[str, str]] = []
    for row in rows:
        segments = split_gloss(row.get("historical_gloss_en", ""), row.get("sense_split_status", ""))
        for index, (segment, trigger) in enumerate(segments, start=1):
            output.append(
                {
                    "sense_candidate_id": f"{row['sense_id']}-candidate-{index}",
                    "structured_id": row["structured_id"],
                    "source_record_id": row["source_record_id"],
                    "historical_headword": row["historical_headword"],
                    "historical_part_of_speech": row["historical_part_of_speech"],
                    "source_sense_id": row["sense_id"],
                    "candidate_index": str(index),
                    "candidate_gloss_en": segment,
                    "split_trigger": trigger,
                    "candidate_status": "unreviewed_draft",
                    "current_semantic_status": "unassessed",
                    "requires_human_review": "yes",
                }
            )
    return output


def write_candidates(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate punctuation-based historical sense candidates for human semantic review."
    )
    parser.add_argument("--structured", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = build_candidates(args.structured)
    write_candidates(args.output, rows)
    print(
        f"NISSOR SENSE CANDIDATES: {len(rows)} review-only candidate segments; "
        "no semantic segment is automatically verified."
    )


if __name__ == "__main__":
    main()
