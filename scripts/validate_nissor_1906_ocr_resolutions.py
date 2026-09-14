from __future__ import annotations

import csv
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUSPICIOUS = ROOT / "data" / "historical" / "nissor-1906" / "suspicious_queue.csv"
RESOLUTIONS = ROOT / "data" / "historical" / "nissor-1906" / "ocr_resolutions.csv"
REPORT = ROOT / "quality" / "nissor1906_ocr_resolution_report.json"

ALLOWED_TYPES = {
    "confirmed",
    "corrected_ocr",
    "article_split",
    "wrong_headword_match",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate() -> dict[str, object]:
    suspicious = read_rows(SUSPICIOUS)
    resolutions = read_rows(RESOLUTIONS)

    suspicious_ids = [row["record_id"] for row in suspicious]
    resolution_ids = [row["record_id"] for row in resolutions]

    errors: list[str] = []
    if len(suspicious) != 35:
        errors.append(f"Expected 35 suspicious records, found {len(suspicious)}")
    if len(resolutions) != 35:
        errors.append(f"Expected 35 OCR resolutions, found {len(resolutions)}")
    if len(set(resolution_ids)) != len(resolution_ids):
        errors.append("Duplicate record_id in OCR resolutions")

    missing = sorted(set(suspicious_ids) - set(resolution_ids))
    extra = sorted(set(resolution_ids) - set(suspicious_ids))
    if missing:
        errors.append(f"Missing resolutions: {missing}")
    if extra:
        errors.append(f"Unknown resolution ids: {extra}")

    for row in resolutions:
        rid = row.get("record_id", "")
        resolved = row.get("resolved_historical_headword", "")
        if not resolved:
            errors.append(f"{rid}: empty resolved_historical_headword")
        elif unicodedata.normalize("NFC", resolved) != resolved:
            errors.append(f"{rid}: resolved headword is not NFC")
        if row.get("resolution_type") not in ALLOWED_TYPES:
            errors.append(f"{rid}: unsupported resolution_type {row.get('resolution_type')!r}")
        if not row.get("proofread_source"):
            errors.append(f"{rid}: missing proofread source")
        if not row.get("reviewer"):
            errors.append(f"{rid}: missing reviewer")
        review_date = row.get("review_date", "")
        if len(review_date) != 10 or review_date[4:5] != "-" or review_date[7:8] != "-":
            errors.append(f"{rid}: review_date must be YYYY-MM-DD")

    type_counts: dict[str, int] = {}
    for row in resolutions:
        kind = row["resolution_type"]
        type_counts[kind] = type_counts.get(kind, 0) + 1

    report: dict[str, object] = {
        "source_id": "nissor-1906-kha-en",
        "suspicious_records": len(suspicious),
        "resolved_records": len(resolutions),
        "unresolved_records": len(missing),
        "resolution_type_counts": dict(sorted(type_counts.items())),
        "all_suspicious_records_resolved": not errors and len(resolutions) == 35,
        "errors": errors,
        "policy": (
            "OCR resolutions are a derived correction layer. The immutable raw OCR extraction "
            "is retained; corrected historical headwords are based on the proofread Wikisource "
            "transcription checked against the public-domain 1906 scan."
        ),
    }
    return report


def main() -> None:
    report = validate()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report["errors"]:
        for error in report["errors"]:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("NISSOR 1906 OCR RESOLUTIONS VALID: 35/35 suspicious records resolved.")


if __name__ == "__main__":
    main()
