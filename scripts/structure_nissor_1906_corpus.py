from __future__ import annotations

import argparse
import csv
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW = ROOT / "data" / "historical" / "nissor-1906" / "review_queue.csv"
DEFAULT_SUSPICIOUS = ROOT / "data" / "historical" / "nissor-1906" / "suspicious_queue.csv"
DEFAULT_RESOLUTIONS = ROOT / "data" / "historical" / "nissor-1906" / "ocr_resolutions.csv"
DEFAULT_APPROVAL = ROOT / "data" / "review" / "nissor1906_source_approval.csv"

FIELDS = [
    "structured_id",
    "source_record_id",
    "language",
    "script",
    "source_id",
    "source_year",
    "source_page_approx",
    "historical_headword",
    "historical_article",
    "historical_part_of_speech",
    "normalized_part_of_speech",
    "lexeme_structure",
    "sense_id",
    "sense_number",
    "historical_gloss_en",
    "definition_kha",
    "historical_usage_status",
    "current_use_status",
    "modern_standard_status",
    "borrowing_status",
    "variant_status",
    "variant_of",
    "sense_split_status",
    "review_stage",
    "requires_modern_review",
    "provenance_note",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_approval(path: Path) -> dict[str, str]:
    rows = read_rows(path)
    if len(rows) != 1:
        raise SystemExit("Expected one Nissor source-wide approval decision")
    row = rows[0]
    if row.get("source_id") != "nissor-1906-kha-en" or row.get("decision") != "approve_inclusion":
        raise SystemExit("Nissor source-wide approval is missing or invalid")
    if row.get("effective_stage") != "lexical_review":
        raise SystemExit("Nissor source-wide approval must resolve to lexical_review")
    return row


def lexeme_structure(headword: str, historical_pos: str) -> str:
    if historical_pos == "phrase" or " " in headword.strip():
        return "multiword"
    if "-" in headword:
        return "hyphenated"
    return "word"


def sense_split_status(gloss: str) -> str:
    markers = (";", "—", " - ")
    return "needs_semantic_split" if any(marker in gloss for marker in markers) else "single_historical_gloss"


def make_structured_row(
    row: dict[str, str],
    *,
    resolved_headword: str | None = None,
    article: str = "",
    resolved_pos: str | None = None,
    provenance: str,
) -> dict[str, str]:
    rid = row["record_id"]
    numeric = rid.rsplit("-", 1)[-1]
    headword = unicodedata.normalize("NFC", resolved_headword or row["headword_candidate"])
    pos = resolved_pos or row["part_of_speech"]
    gloss = row.get("historical_gloss_raw", "").strip()
    page = row.get("source_page_approx", "")
    return {
        "structured_id": f"n1906-entry-{numeric}",
        "source_record_id": rid,
        "language": "kha",
        "script": "Latn",
        "source_id": "nissor-1906-kha-en",
        "source_year": "1906",
        "source_page_approx": page,
        "historical_headword": headword,
        "historical_article": article,
        "historical_part_of_speech": pos,
        "normalized_part_of_speech": pos,
        "lexeme_structure": lexeme_structure(headword, pos),
        "sense_id": f"n1906-sense-{numeric}-1",
        "sense_number": "1",
        "historical_gloss_en": gloss,
        "definition_kha": "",
        "historical_usage_status": "attested_1906",
        "current_use_status": "unassessed",
        "modern_standard_status": "unassessed",
        "borrowing_status": "unassessed",
        "variant_status": "unassessed",
        "variant_of": "",
        "sense_split_status": sense_split_status(gloss),
        "review_stage": "lexical_review",
        "requires_modern_review": "yes",
        "provenance_note": provenance,
    }


def build_rows(
    review_path: Path,
    suspicious_path: Path,
    resolutions_path: Path,
    approval_path: Path,
) -> list[dict[str, str]]:
    load_approval(approval_path)
    normal = read_rows(review_path)
    suspicious = read_rows(suspicious_path)
    resolutions = {row["record_id"]: row for row in read_rows(resolutions_path)}

    suspicious_ids = {row["record_id"] for row in suspicious}
    if suspicious_ids != set(resolutions):
        missing = sorted(suspicious_ids - set(resolutions))
        extra = sorted(set(resolutions) - suspicious_ids)
        raise SystemExit(f"OCR resolution mismatch; missing={missing}, extra={extra}")

    output: list[dict[str, str]] = []
    seen: set[str] = set()

    for row in normal:
        rid = row["record_id"]
        if rid in seen:
            raise SystemExit(f"Duplicate source record: {rid}")
        seen.add(rid)
        output.append(
            make_structured_row(
                row,
                provenance="Nissor Singh 1906; layout-aware OCR extraction; source-wide owner inclusion approval.",
            )
        )

    for row in suspicious:
        rid = row["record_id"]
        if rid in seen:
            raise SystemExit(f"Source record occurs in both normal and suspicious queues: {rid}")
        seen.add(rid)
        resolution = resolutions[rid]
        output.append(
            make_structured_row(
                row,
                resolved_headword=resolution["resolved_historical_headword"],
                article=resolution.get("historical_article", ""),
                resolved_pos=resolution.get("historical_pos") or row["part_of_speech"],
                provenance=(
                    "Nissor Singh 1906; OCR corrected against proofread Wikisource transcription "
                    "and public-domain scan; source-wide owner inclusion approval."
                ),
            )
        )

    output.sort(key=lambda item: (item["historical_headword"].casefold(), item["historical_part_of_speech"], item["source_record_id"]))
    return output


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the structured modern-review layer for Nissor Singh 1906.")
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--suspicious", type=Path, default=DEFAULT_SUSPICIOUS)
    parser.add_argument("--resolutions", type=Path, default=DEFAULT_RESOLUTIONS)
    parser.add_argument("--approval", type=Path, default=DEFAULT_APPROVAL)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = build_rows(args.review, args.suspicious, args.resolutions, args.approval)
    write_rows(args.output, rows)
    unresolved = sum(row["current_use_status"] == "unassessed" for row in rows)
    split_needed = sum(row["sense_split_status"] == "needs_semantic_split" for row in rows)
    print(
        f"NISSOR STRUCTURED LAYER: {len(rows)} approved historical lexemes; "
        f"{unresolved} require modern-use review; {split_needed} require semantic sense splitting."
    )


if __name__ == "__main__":
    main()
