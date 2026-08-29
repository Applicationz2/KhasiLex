from __future__ import annotations

import csv
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "data/historical/nissor-1906/entries.csv"
REVIEW = ROOT / "data/historical/nissor-1906/review_queue.csv"
RAW = ROOT / "data/sources/nissor-1906/khasienglishdict00singrich_djvu.txt"
REPORT = ROOT / "quality/nissor1906_ingest_report.json"

MIN_RECORDS = 500
MIN_UNIQUE_HEADWORDS = 400
MIN_INITIALS = 10


def fail(errors: list[str]) -> None:
    print("NISSOR 1906 CORPUS VALIDATION FAILED")
    for error in errors:
        print("-", error)
    raise SystemExit(1)


def main() -> None:
    if not ENTRIES.exists():
        print("NISSOR 1906 CORPUS VALIDATION SKIPPED: generated full corpus not present yet")
        return

    errors: list[str] = []
    required = {
        "record_id", "headword_raw", "headword_candidate", "normalized",
        "language", "entry_type", "part_of_speech", "historical_gloss_raw",
        "source_id", "source_year", "source_url", "ocr_confidence",
        "review_priority", "verification_status", "human_review_required",
    }

    with ENTRIES.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            errors.append(f"missing entries columns: {sorted(missing)}")
        rows = list(reader)

    if len(rows) < MIN_RECORDS:
        errors.append(f"expected at least {MIN_RECORDS} extracted records, found {len(rows)}")

    ids = [row.get("record_id", "") for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("record_id values are not unique")

    unique = {row.get("normalized", "") for row in rows if row.get("normalized")}
    if len(unique) < MIN_UNIQUE_HEADWORDS:
        errors.append(f"expected at least {MIN_UNIQUE_HEADWORDS} unique headwords, found {len(unique)}")

    initials = {head[:1] for head in unique if head}
    if len(initials) < MIN_INITIALS:
        errors.append(f"alphabet coverage too narrow: only {len(initials)} initial characters")

    for line_no, row in enumerate(rows, start=2):
        if row.get("source_id") != "nissor-1906-kha-en":
            errors.append(f"line {line_no}: incorrect source_id")
        if row.get("source_year") != "1906":
            errors.append(f"line {line_no}: incorrect source_year")
        if row.get("verification_status") != "pending":
            errors.append(f"line {line_no}: historical ingest must remain pending")
        if row.get("human_review_required") != "yes":
            errors.append(f"line {line_no}: human_review_required must be yes")
        normalized = row.get("normalized", "")
        if normalized != unicodedata.normalize("NFC", normalized):
            errors.append(f"line {line_no}: normalized headword is not NFC")
        try:
            confidence = float(row.get("ocr_confidence", ""))
            if not 0 <= confidence <= 1:
                raise ValueError
        except ValueError:
            errors.append(f"line {line_no}: invalid ocr_confidence")
        if row.get("review_priority") not in {"1", "2", "3"}:
            errors.append(f"line {line_no}: invalid review_priority")

    review_rows: list[dict[str, str]] = []
    if not REVIEW.exists():
        errors.append("review_queue.csv is missing")
    else:
        with REVIEW.open(encoding="utf-8", newline="") as handle:
            review_rows = list(csv.DictReader(handle))
        if not review_rows:
            errors.append("review_queue.csv is empty")
        review_keys = [
            (row.get("normalized", ""), row.get("part_of_speech", ""))
            for row in review_rows
        ]
        if len(review_keys) != len(set(review_keys)):
            errors.append("review_queue contains duplicate headword/POS pairs")
        for line_no, row in enumerate(review_rows, start=2):
            try:
                confidence = float(row.get("ocr_confidence", ""))
            except ValueError:
                errors.append(f"review line {line_no}: invalid ocr_confidence")
                continue
            if confidence < 0.75:
                errors.append(f"review line {line_no}: low-confidence record leaked into review queue")

    if not RAW.exists():
        errors.append("raw public-domain OCR snapshot is missing")

    if not REPORT.exists():
        errors.append("ingest report is missing")
    else:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        if report.get("records_extracted") != len(rows):
            errors.append("report records_extracted does not match entries.csv")
        if report.get("unique_headwords") != len(unique):
            errors.append("report unique_headwords does not match entries.csv")
        if report.get("pending_records") != len(rows):
            errors.append("report must show every extracted record as pending")
        if report.get("review_queue_records") != len(review_rows):
            errors.append("report review_queue_records does not match review_queue.csv")
        if RAW.exists():
            digest = hashlib.sha256(RAW.read_bytes()).hexdigest()
            if report.get("source_sha256") != digest:
                errors.append("raw OCR SHA-256 does not match ingest report")

    if errors:
        fail(errors)

    print(
        f"NISSOR 1906 CORPUS VALIDATION PASSED: {len(rows)} records, "
        f"{len(unique)} unique headwords, {len(review_rows)} review-queue records"
    )


if __name__ == "__main__":
    main()
