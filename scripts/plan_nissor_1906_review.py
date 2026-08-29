from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def tier(row: dict[str, str]) -> tuple[int, str]:
    head = row.get("headword_candidate", "")
    entry_type = row.get("entry_type", "")
    gloss = row.get("historical_gloss_raw", "")
    existing = row.get("existing_master") == "yes"

    if existing:
        return 0, "existing-master-upgrade"
    if (
        entry_type == "word"
        and not head.startswith(("'", "’"))
        and "-" not in head
        and " " not in head
        and len(head) <= 24
        and len(gloss) <= 500
    ):
        return 1, "simple-historical-word"
    if entry_type in {"compound", "reduplication", "phrase"}:
        return 2, "compound-or-multiword"
    return 3, "complex-historical-entry"


def clean_sort_key(head: str) -> str:
    return head.lstrip("'’").casefold()


def main() -> None:
    parser = argparse.ArgumentParser(description="Partition the complete Nissor 1906 editorial queue into deterministic human-review batches.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()

    if args.batch_size < 1:
        raise SystemExit("--batch-size must be >= 1")

    with args.input.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    enriched: list[tuple[int, str, dict[str, str]]] = []
    for row in rows:
        tier_num, tier_name = tier(row)
        enriched.append((tier_num, tier_name, row))

    enriched.sort(
        key=lambda item: (
            item[0],
            clean_sort_key(item[2].get("normalized", "")),
            item[2].get("part_of_speech", ""),
            item[2].get("record_id", ""),
        )
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "global_sequence", "review_batch", "batch_sequence", "review_tier",
        "record_id", "headword_candidate", "normalized", "part_of_speech",
        "entry_type", "source_page_approx", "ocr_confidence",
        "existing_master", "verification_status", "human_review_required",
    ]

    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for index, (tier_num, tier_name, row) in enumerate(enriched, start=1):
            batch_number = ((index - 1) // args.batch_size) + 1
            batch_sequence = ((index - 1) % args.batch_size) + 1
            writer.writerow({
                "global_sequence": index,
                "review_batch": f"n1906-{batch_number:03d}",
                "batch_sequence": batch_sequence,
                "review_tier": f"{tier_num}:{tier_name}",
                "record_id": row.get("record_id", ""),
                "headword_candidate": row.get("headword_candidate", ""),
                "normalized": row.get("normalized", ""),
                "part_of_speech": row.get("part_of_speech", ""),
                "entry_type": row.get("entry_type", ""),
                "source_page_approx": row.get("source_page_approx", ""),
                "ocr_confidence": row.get("ocr_confidence", ""),
                "existing_master": row.get("existing_master", ""),
                "verification_status": row.get("verification_status", ""),
                "human_review_required": row.get("human_review_required", ""),
            })

    batches = math.ceil(len(enriched) / args.batch_size) if enriched else 0
    print(f"NISSOR 1906 REVIEW PLAN COMPLETE: {len(enriched)} candidates across {batches} batches of up to {args.batch_size}")


if __name__ == "__main__":
    main()
