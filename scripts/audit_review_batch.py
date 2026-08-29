from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import csv
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BATCH = ROOT / "data/review/batches/v0.4-pilot-001.csv"
SOURCE_REGISTRY = ROOT / "data/sources/source_registry.csv"
MASTER = ROOT / "data/master/khasi_lexicon.csv"

EXPECTED_POS = {
    "noun": 50,
    "verb": 25,
    "adjective": 13,
    "adverb": 4,
    "pronoun": 8,
}

CATEGORY_BY_POS = {
    "noun": "Category:Khasi_nouns",
    "verb": "Category:Khasi_verbs",
    "adjective": "Category:Khasi_adjectives",
    "adverb": "Category:Khasi_adverbs",
    "pronoun": "Category:Khasi_pronouns",
}

REQUIRED_FIELDS = {
    "candidate_id",
    "headword",
    "normalized",
    "language",
    "part_of_speech",
    "source_id",
    "source_category",
    "license",
    "attestation_status",
    "existing_master",
    "verification_status",
    "human_review_required",
    "review_priority",
}


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", (value or "").strip())


def approved_sources() -> dict[str, dict[str, str]]:
    with SOURCE_REGISTRY.open(encoding="utf-8", newline="") as f:
        return {
            row["source_id"]: row
            for row in csv.DictReader(f)
            if row.get("status") == "approved"
        }


def master_headwords() -> set[str]:
    with MASTER.open(encoding="utf-8", newline="") as f:
        return {
            nfc(row.get("headword", "")).casefold()
            for row in csv.DictReader(f)
            if nfc(row.get("headword", ""))
        }


def audit(path: Path, expect_count: int = 100) -> list[str]:
    errors: list[str] = []
    sources = approved_sources()
    master = master_headwords()

    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_FIELDS - fields)
        if missing:
            return [f"missing required columns: {', '.join(missing)}"]
        rows = list(reader)

    if len(rows) != expect_count:
        errors.append(f"expected {expect_count} rows, found {len(rows)}")

    ids = [row["candidate_id"].strip() for row in rows]
    dup_ids = [key for key, count in Counter(ids).items() if count > 1]
    if dup_ids:
        errors.append(f"duplicate candidate IDs: {', '.join(sorted(dup_ids))}")

    pos_counts = Counter(row["part_of_speech"].strip() for row in rows)
    if dict(pos_counts) != EXPECTED_POS:
        errors.append(f"unexpected POS distribution: {dict(pos_counts)}; expected {EXPECTED_POS}")

    for line_no, row in enumerate(rows, start=2):
        cid = row["candidate_id"].strip() or f"line {line_no}"
        headword = row["headword"].strip()
        normalized = row["normalized"].strip()
        pos = row["part_of_speech"].strip()
        source_id = row["source_id"].strip()

        if not headword:
            errors.append(f"{cid}: empty headword")
            continue

        if normalized != nfc(headword):
            errors.append(f"{cid}: normalized form is not NFC(headword)")

        if row["language"].strip() != "kha":
            errors.append(f"{cid}: language must be kha")

        if pos not in EXPECTED_POS:
            errors.append(f"{cid}: unsupported pilot POS {pos!r}")
        elif row["source_category"].strip() != CATEGORY_BY_POS[pos]:
            errors.append(f"{cid}: source category does not match POS")

        source = sources.get(source_id)
        if source is None:
            errors.append(f"{cid}: source {source_id!r} is not approved")
        elif row["license"].strip() != source.get("license", "").strip():
            errors.append(f"{cid}: licence does not match source registry")

        if row["attestation_status"].strip() != "source_attested":
            errors.append(f"{cid}: attestation_status must be source_attested")

        if row["verification_status"].strip() != "pending":
            errors.append(f"{cid}: first-100 source batch must remain pending until Khasi human review")

        if row["human_review_required"].strip().lower() != "yes":
            errors.append(f"{cid}: human_review_required must be yes")

        expected_existing = "yes" if nfc(headword).casefold() in master else "no"
        if row["existing_master"].strip().lower() != expected_existing:
            errors.append(
                f"{cid}: existing_master={row['existing_master']!r}; expected {expected_existing!r}"
            )

        if row["review_priority"].strip() not in {"1", "2", "3"}:
            errors.append(f"{cid}: review_priority must be 1, 2 or 3")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a KhasiLex v0.4 human-review batch.")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--expect-count", type=int, default=100)
    args = parser.parse_args()

    errors = audit(args.path, args.expect_count)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Review batch audit passed: {args.path} ({args.expect_count} entries)")
    print(f"Expected POS distribution: {EXPECTED_POS}")


if __name__ == "__main__":
    main()
