from __future__ import annotations

from datetime import date
from pathlib import Path
import csv
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "data/review/batches/v1.0-pilot-001-final-review.csv"

ALLOWED_DECISIONS = {"pending", "verify", "revise", "reject", "defer"}
REQUIRED_FOR_VERIFY = (
    "canonical_spelling",
    "part_of_speech_decision",
    "definition_kha",
    "definition_en",
    "sense_notes",
    "example_kha",
    "example_en",
    "dialect",
    "register",
    "source_provenance_reviewed",
    "license_reviewed",
    "lexical_reviewer",
    "grammar_reviewer",
    "translation_reviewer",
    "provenance_reviewer",
    "review_date",
)

def blank(row: dict[str, str], key: str) -> bool:
    return not (row.get(key) or "").strip()

def main() -> None:
    errors: list[str] = []
    with BATCH.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != 100:
        errors.append(f"pilot must contain exactly 100 rows, found {len(rows)}")

    ids: set[str] = set()
    for line_no, row in enumerate(rows, start=2):
        cid = (row.get("candidate_id") or "").strip()
        headword = (row.get("headword") or "").strip()
        decision = (row.get("decision") or "").strip()

        if not cid:
            errors.append(f"line {line_no}: missing candidate_id")
        elif cid in ids:
            errors.append(f"line {line_no}: duplicate candidate_id {cid}")
        else:
            ids.add(cid)

        if not headword:
            errors.append(f"line {line_no}: missing headword")
        elif unicodedata.normalize("NFC", headword) != headword:
            errors.append(f"line {line_no}: headword is not NFC")

        if decision not in ALLOWED_DECISIONS:
            errors.append(f"line {line_no}: invalid decision {decision!r}")

        for field in ("canonical_spelling", "definition_kha", "example_kha"):
            value = (row.get(field) or "").strip()
            if value and unicodedata.normalize("NFC", value) != value:
                errors.append(f"line {line_no}: {field} is not NFC")

        if decision == "verify":
            for field in REQUIRED_FOR_VERIFY:
                if blank(row, field):
                    errors.append(f"line {line_no}: verify decision missing {field}")

            review_date = (row.get("review_date") or "").strip()
            if review_date:
                try:
                    parsed = date.fromisoformat(review_date)
                    if parsed > date.today():
                        errors.append(f"line {line_no}: review_date cannot be in the future")
                except ValueError:
                    errors.append(f"line {line_no}: review_date must use YYYY-MM-DD")

            if (row.get("sense_notes") or "").strip().lower() in {"", "pending", "unreviewed"}:
                errors.append(f"line {line_no}: verify decision requires an explicit sense decision")

    if errors:
        print("V1 PILOT VALIDATION FAILED")
        for error in errors:
            print("-", error)
        sys.exit(1)

    verified = sum(1 for row in rows if (row.get("decision") or "").strip() == "verify")
    print(f"V1 PILOT VALIDATION PASSED: {len(rows)} rows, {verified} verified")

if __name__ == "__main__":
    main()
