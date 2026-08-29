from __future__ import annotations

from pathlib import Path
import argparse
import csv
import json
import unicodedata
import sys

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/master/khasi_lexicon.csv"
DEFAULT_OUT = ROOT / "data/pending/staged_candidates.jsonl"

REQUIRED_INPUT = {"headword", "entry_type", "source", "license"}
VALID_TYPES = {"word", "phrase", "reduplication", "compound", "idiom"}


def nfc(value):
    return unicodedata.normalize("NFC", (value or "").strip())


def master_keys():
    with MASTER.open(encoding="utf-8", newline="") as f:
        return {
            nfc(row.get("headword")).casefold()
            for row in csv.DictReader(f)
            if nfc(row.get("headword"))
        }


def main():
    parser = argparse.ArgumentParser(description="Stage Khasi lexical candidates without modifying the authoritative master lexicon.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    existing = master_keys()
    staged_seen = set()
    accepted = []
    rejected = []

    with args.input_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED_INPUT - set(reader.fieldnames or [])
        if missing:
            print(f"Missing required columns: {sorted(missing)}")
            sys.exit(2)

        for line_no, row in enumerate(reader, start=2):
            headword = nfc(row.get("headword"))
            key = headword.casefold()
            entry_type = (row.get("entry_type") or "word").strip()
            reasons = []

            if not headword:
                reasons.append("missing headword")
            if entry_type not in VALID_TYPES:
                reasons.append("invalid entry_type")
            if not nfc(row.get("source")):
                reasons.append("missing source")
            if not nfc(row.get("license")):
                reasons.append("missing license")
            if key in existing:
                reasons.append("headword already exists in master lexicon")
            if key in staged_seen:
                reasons.append("duplicate candidate in import file")

            if entry_type == "reduplication":
                if not nfc(row.get("base_form")):
                    reasons.append("reduplication missing base_form")
                if not nfc(row.get("reduplication_type")):
                    reasons.append("reduplication missing reduplication_type")

            if reasons:
                rejected.append({"line": line_no, "headword": headword, "reasons": reasons})
                continue

            staged_seen.add(key)
            record = {k: nfc(v) for k, v in row.items() if k is not None}
            record.update({
                "headword": headword,
                "normalized": headword,
                "language": "kha",
                "script": "Latn",
                "bcp47": "kha",
                "verification_status": "pending",
                "translation_status": "pending",
                "token_count": str(len(headword.split())),
                "staging_status": "awaiting_editorial_review",
            })
            accepted.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for record in accepted:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(json.dumps({
        "accepted": len(accepted),
        "rejected": len(rejected),
        "output": str(args.output),
        "rejections": rejected,
    }, ensure_ascii=False, indent=2))

    if rejected:
        sys.exit(1)


if __name__ == "__main__":
    main()
