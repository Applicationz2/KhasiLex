from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVAL = ROOT / "data" / "review" / "nissor1906_source_approval.csv"
REVIEW_QUEUE = ROOT / "data" / "historical" / "nissor-1906" / "review_queue.csv"
SUSPICIOUS_QUEUE = ROOT / "data" / "historical" / "nissor-1906" / "suspicious_queue.csv"
REPORT = ROOT / "quality" / "nissor1906_source_approval_report.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def evaluate() -> dict[str, object]:
    approvals = read_rows(APPROVAL)
    if len(approvals) != 1:
        raise SystemExit("Expected exactly one active Nissor 1906 source-wide approval row.")

    approval = approvals[0]
    required = {
        "source_id": "nissor-1906-kha-en",
        "decision": "approve_inclusion",
        "applies_to": "review_queue",
        "effective_stage": "lexical_review",
    }
    for field, expected in required.items():
        if approval.get(field) != expected:
            raise SystemExit(f"Invalid approval {field}: expected {expected!r}.")

    review_rows = read_rows(REVIEW_QUEUE)
    suspicious_rows = read_rows(SUSPICIOUS_QUEUE)

    if not review_rows:
        raise SystemExit("Nissor 1906 review queue is empty.")
    if any(row.get("verification_status") != "pending" for row in review_rows):
        raise SystemExit("Historical source rows must remain pending in the extraction layer.")
    if any(row.get("human_review_required") != "yes" for row in review_rows):
        raise SystemExit("Every historical source row must retain human-review-required=yes.")

    normal_ids = {row["record_id"] for row in review_rows}
    suspicious_ids = {row["record_id"] for row in suspicious_rows}
    overlap = normal_ids & suspicious_ids
    if overlap:
        raise SystemExit(f"Review and suspicious queues overlap: {sorted(overlap)[:5]}")

    report: dict[str, object] = {
        "decision_id": approval["decision_id"],
        "source_id": approval["source_id"],
        "reviewer": approval["reviewer"],
        "review_date": approval["review_date"],
        "decision": approval["decision"],
        "effective_stage": approval["effective_stage"],
        "approved_review_queue_records": len(review_rows),
        "suspicious_ocr_records_pending": len(suspicious_rows),
        "effective_status_counts": {
            "lexical_review": len(review_rows),
            "pending_ocr_confirmation": len(suspicious_rows),
        },
        "verified_records_created_by_this_decision": 0,
        "policy": (
            "Source-wide approval establishes inclusion/lexical attestation for genuine "
            "Nissor 1906 headwords. It does not automatically verify modern spelling, "
            "sense, register, borrowing status, examples, or present-day standard usage."
        ),
    }
    return report


def main() -> None:
    report = evaluate()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "Nissor 1906 source-wide approval valid: "
        f"{report['approved_review_queue_records']} lexical-review records; "
        f"{report['suspicious_ocr_records_pending']} OCR-suspicious records remain pending."
    )


if __name__ == "__main__":
    main()
