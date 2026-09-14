from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

TIER_ORDER = {
    "tier1_strong_candidate": 1,
    "tier2_current_attested": 2,
    "tier3_pos_conflict": 3,
    "tier4_variant_candidate": 4,
    "tier5_lexicographic_only": 5,
    "tier6_historical_only": 6,
}

FIELDS = [
    "global_rank",
    "tier",
    "tier_rank",
    "batch_id",
    "batch_position",
    "structured_id",
    "source_record_id",
    "historical_headword",
    "historical_part_of_speech",
    "modern_canonical_candidate",
    "modern_part_of_speech_candidate",
    "current_use_status",
    "modern_standard_status",
    "pos_evidence_status",
    "variant_status",
    "variant_candidate",
    "borrowing_status",
    "sense_split_status",
    "current_evidence_source_count",
    "current_evidence_sources",
    "current_corpus_frequency",
    "review_decision",
    "review_notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def integer(value: str) -> int:
    try:
        return int(value or "0")
    except ValueError:
        return 0


def classify(row: dict[str, str]) -> str:
    if row.get("pos_evidence_status") in {
        "conflict_requires_review",
        "ambiguous_multiple_modern_pos",
    }:
        return "tier3_pos_conflict"
    if row.get("variant_status") == "orthographic_variant_candidate" or row.get("current_use_status") == "current_variant_attested_candidate":
        return "tier4_variant_candidate"
    if row.get("modern_standard_status") == "strong_candidate":
        return "tier1_strong_candidate"
    if row.get("current_use_status") == "current_attested":
        return "tier2_current_attested"
    if row.get("modern_standard_status") == "lexicographic_candidate":
        return "tier5_lexicographic_only"
    return "tier6_historical_only"


def ranking_key(row: dict[str, str]):
    tier = classify(row)
    return (
        TIER_ORDER[tier],
        -integer(row.get("current_evidence_source_count", "0")),
        -integer(row.get("current_corpus_frequency", "0")),
        0 if row.get("sense_split_status") != "needs_semantic_split" else 1,
        row.get("historical_headword", "").casefold(),
        row.get("historical_part_of_speech", ""),
        row.get("source_record_id", ""),
    )


def build_queue(rows: list[dict[str, str]], batch_size: int = 100) -> list[dict[str, str]]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    ordered = sorted(rows, key=ranking_key)
    tier_counts: Counter[str] = Counter()
    tier_batches: defaultdict[str, int] = defaultdict(int)
    output: list[dict[str, str]] = []

    previous_tier = None
    position_in_tier = 0
    for global_index, row in enumerate(ordered, start=1):
        tier = classify(row)
        if tier != previous_tier:
            previous_tier = tier
            position_in_tier = 0
        position_in_tier += 1
        tier_counts[tier] += 1
        batch_number = ((position_in_tier - 1) // batch_size) + 1
        batch_position = ((position_in_tier - 1) % batch_size) + 1
        tier_batches[tier] = max(tier_batches[tier], batch_number)
        short_tier = tier.split("_", 1)[0]
        batch_id = f"modern-{short_tier}-{batch_number:03d}"

        output.append(
            {
                "global_rank": str(global_index),
                "tier": tier,
                "tier_rank": str(position_in_tier),
                "batch_id": batch_id,
                "batch_position": str(batch_position),
                "structured_id": row.get("structured_id", ""),
                "source_record_id": row.get("source_record_id", ""),
                "historical_headword": row.get("historical_headword", ""),
                "historical_part_of_speech": row.get("historical_part_of_speech", ""),
                "modern_canonical_candidate": row.get("modern_canonical_candidate", ""),
                "modern_part_of_speech_candidate": row.get("modern_part_of_speech_candidate", ""),
                "current_use_status": row.get("current_use_status", ""),
                "modern_standard_status": row.get("modern_standard_status", ""),
                "pos_evidence_status": row.get("pos_evidence_status", ""),
                "variant_status": row.get("variant_status", ""),
                "variant_candidate": row.get("variant_candidate", ""),
                "borrowing_status": row.get("borrowing_status", ""),
                "sense_split_status": row.get("sense_split_status", ""),
                "current_evidence_source_count": row.get("current_evidence_source_count", "0"),
                "current_evidence_sources": row.get("current_evidence_sources", ""),
                "current_corpus_frequency": row.get("current_corpus_frequency", "0"),
                "review_decision": "pending",
                "review_notes": "",
            }
        )
    return output


def manifest(queue: list[dict[str, str]], batch_size: int) -> dict[str, object]:
    tier_counts = Counter(row["tier"] for row in queue)
    batches: dict[str, list[str]] = defaultdict(list)
    for row in queue:
        batch_id = row["batch_id"]
        if batch_id not in batches[row["tier"]]:
            batches[row["tier"]].append(batch_id)
    return {
        "records": len(queue),
        "batch_size": batch_size,
        "tier_counts": dict(sorted(tier_counts.items(), key=lambda item: TIER_ORDER[item[0]])),
        "tier_batches": {tier: ids for tier, ids in sorted(batches.items(), key=lambda item: TIER_ORDER[item[0]])},
        "review_order": list(TIER_ORDER),
        "decision_values": ["approve", "revise", "reject", "defer", "pending"],
        "policy": (
            "Queue order is evidence priority, not verification. Every row remains pending editorial review; "
            "absence of current evidence does not establish archaic status."
        ),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create deterministic evidence-ranked modern Khasi review queues.")
    parser.add_argument("--overlay", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()

    rows = read_rows(args.overlay)
    queue = build_queue(rows, args.batch_size)
    if len(queue) != len(rows):
        raise SystemExit("review queue lost records")
    if len({row["source_record_id"] for row in queue}) != len(queue):
        raise SystemExit("review queue contains duplicate source records")
    if any(row["review_decision"] != "pending" for row in queue):
        raise SystemExit("generated review decisions must start pending")

    write_csv(args.output, queue)
    data = manifest(queue, args.batch_size)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
