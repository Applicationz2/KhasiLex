from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "data" / "modern_evidence" / "current_attestations_seed.csv"
DEFAULT_WIKTIONARY = ROOT / "data" / "review" / "batches" / "v0.4-pilot-001.csv"
DEFAULT_HISTORICAL_ENTRIES = ROOT / "data" / "historical" / "nissor-1906" / "entries.csv"

FIELDS = [
    "structured_id",
    "source_record_id",
    "historical_headword",
    "historical_part_of_speech",
    "modern_canonical_candidate",
    "canonical_evidence_level",
    "modern_part_of_speech_candidate",
    "pos_evidence_status",
    "current_use_status",
    "diachronic_status_candidate",
    "current_evidence_source_count",
    "current_evidence_sources",
    "current_evidence_urls",
    "current_corpus_frequency",
    "lexicographic_evidence_sources",
    "modern_standard_status",
    "variant_status",
    "variant_candidate",
    "historical_source_marker",
    "historical_borrowing_signal",
    "borrowing_status",
    "sense_split_status",
    "historical_usage_status",
    "review_priority",
    "review_stage",
    "requires_human_review",
    "verified",
]


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def key(text: str) -> str:
    return nfc(text).casefold()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_current_evidence(paths: list[Path]) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    exact: dict[str, list[dict[str, str]]] = defaultdict(list)
    variants: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in paths:
        if not path.exists():
            continue
        for row in read_csv(path):
            headword = nfc(row.get("headword", ""))
            if not headword:
                continue
            match_type = row.get("match_type") or "exact"
            if match_type == "exact":
                exact[key(headword)].append(row)
            else:
                variants[key(headword)].append(row)
    return exact, variants


def load_wiktionary(path: Path) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    if not path.exists():
        return result
    for row in read_csv(path):
        headword = nfc(row.get("headword", ""))
        if headword:
            result[key(headword)].append(row)
    return result


def load_historical_signals(path: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    if not path.exists():
        return result
    for row in read_csv(path):
        record_id = row.get("record_id", "")
        if not record_id:
            continue
        result[record_id] = {
            "source_marker": row.get("source_marker", ""),
            "source_marker_interpretation": row.get("source_marker_interpretation", ""),
        }
    return result


def aggregate_current(rows: list[dict[str, str]]) -> tuple[list[str], list[str], int]:
    sources = sorted({row.get("source_id", "") for row in rows if row.get("source_id")})
    urls = sorted({row.get("source_url", "") for row in rows if row.get("source_url")})
    frequency = 0
    for row in rows:
        value = row.get("frequency") or row.get("minimum_occurrences") or "0"
        try:
            frequency += int(value)
        except ValueError:
            pass
    return sources, urls, frequency


def pos_decision(historical_pos: str, wiki_rows: list[dict[str, str]]) -> tuple[str, str]:
    poses = sorted({row.get("part_of_speech", "").strip() for row in wiki_rows if row.get("part_of_speech", "").strip()})
    if not poses:
        return "", "unassessed"
    if historical_pos in poses:
        return historical_pos, "matched_historical_and_modern_lexicographic"
    if len(poses) == 1:
        return poses[0], "conflict_requires_review"
    return ";".join(poses), "ambiguous_multiple_modern_pos"


def enrich_row(
    row: dict[str, str],
    current_exact: list[dict[str, str]],
    current_variants: list[dict[str, str]],
    wiki_rows: list[dict[str, str]],
    historical_signal: dict[str, str] | None = None,
) -> dict[str, str]:
    headword = nfc(row["historical_headword"])
    historical_pos = row.get("normalized_part_of_speech") or row.get("historical_part_of_speech", "")
    sources, urls, frequency = aggregate_current(current_exact)
    wiki_sources = sorted({item.get("source_id", "") for item in wiki_rows if item.get("source_id")})
    modern_pos, pos_status = pos_decision(historical_pos, wiki_rows)
    historical_signal = historical_signal or {}

    modern_canonical = ""
    canonical_level = "unassessed"
    current_status = "historical_only_unassessed"
    diachronic_status = "historical_attested_current_unassessed"
    modern_standard = "unassessed"
    variant_status = "unassessed"
    variant_candidate = ""
    priority = "5"

    if current_exact:
        modern_canonical = headword
        current_status = "current_attested"
        diachronic_status = "historical_and_current"
        canonical_level = "current_exact_attestation"
        modern_standard = "candidate_current_attested"
        priority = "2"
        if wiki_rows:
            canonical_level = "current_plus_modern_lexicographic"
            modern_standard = (
                "strong_candidate" if pos_status == "matched_historical_and_modern_lexicographic"
                else "candidate_pos_review_required"
            )
            priority = "1" if modern_standard == "strong_candidate" else "2"
    elif wiki_rows:
        modern_canonical = headword
        canonical_level = "modern_lexicographic_only"
        current_status = "current_use_unassessed"
        diachronic_status = "historical_plus_modern_lexicographic"
        modern_standard = "lexicographic_candidate"
        priority = "3"
    elif current_variants:
        variant_surfaces = sorted({item.get("current_surface", "") for item in current_variants if item.get("current_surface")})
        current_status = "current_variant_attested_candidate"
        diachronic_status = "historical_with_current_variant_candidate"
        variant_status = "orthographic_variant_candidate"
        variant_candidate = ";".join(variant_surfaces)
        priority = "4"

    marker = historical_signal.get("source_marker", "")
    borrowing_signal = historical_signal.get("source_marker_interpretation", "")
    borrowing_status = (
        "historical_source_marked_loan_or_foreign"
        if borrowing_signal == "source-marked-loan-or-foreign"
        else "unassessed"
    )

    return {
        "structured_id": row["structured_id"],
        "source_record_id": row["source_record_id"],
        "historical_headword": headword,
        "historical_part_of_speech": historical_pos,
        "modern_canonical_candidate": modern_canonical,
        "canonical_evidence_level": canonical_level,
        "modern_part_of_speech_candidate": modern_pos,
        "pos_evidence_status": pos_status,
        "current_use_status": current_status,
        "diachronic_status_candidate": diachronic_status,
        "current_evidence_source_count": str(len(sources)),
        "current_evidence_sources": ";".join(sources),
        "current_evidence_urls": ";".join(urls),
        "current_corpus_frequency": str(frequency),
        "lexicographic_evidence_sources": ";".join(wiki_sources),
        "modern_standard_status": modern_standard,
        "variant_status": variant_status,
        "variant_candidate": variant_candidate,
        "historical_source_marker": marker,
        "historical_borrowing_signal": borrowing_signal,
        "borrowing_status": borrowing_status,
        "sense_split_status": row.get("sense_split_status", "unassessed"),
        "historical_usage_status": row.get("historical_usage_status", "attested_1906"),
        "review_priority": priority,
        "review_stage": "modern_evidence_review",
        "requires_human_review": "yes",
        "verified": "no",
    }


def build_overlay(
    structured_path: Path,
    current_paths: list[Path],
    wiktionary_path: Path,
    historical_entries_path: Path = DEFAULT_HISTORICAL_ENTRIES,
) -> list[dict[str, str]]:
    structured = read_csv(structured_path)
    current_exact, current_variants = load_current_evidence(current_paths)
    wiki = load_wiktionary(wiktionary_path)
    historical_signals = load_historical_signals(historical_entries_path)

    output = []
    for row in structured:
        headword_key = key(row.get("historical_headword", ""))
        output.append(
            enrich_row(
                row,
                current_exact.get(headword_key, []),
                current_variants.get(headword_key, []),
                wiki.get(headword_key, []),
                historical_signals.get(row.get("source_record_id", ""), {}),
            )
        )
    return output


def write_overlay(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def report(rows: list[dict[str, str]]) -> dict[str, object]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["modern_standard_status"]] += 1
    return {
        "records": len(rows),
        "modern_standard_status_counts": dict(sorted(counts.items())),
        "current_attested_records": sum(row["current_use_status"] == "current_attested" for row in rows),
        "strong_candidates": sum(row["modern_standard_status"] == "strong_candidate" for row in rows),
        "pos_conflicts": sum(row["pos_evidence_status"] == "conflict_requires_review" for row in rows),
        "historical_borrowing_signals": sum(
            row["borrowing_status"] == "historical_source_marked_loan_or_foreign" for row in rows
        ),
        "verified_records_created": sum(row["verified"] == "yes" for row in rows),
        "policy": (
            "Evidence ranking only. Absence of current evidence never proves archaic status, and historical loan markers "
            "are signals for review rather than final etymological classifications. No row becomes verified without explicit human editorial verification."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a conservative modern-evidence overlay for Nissor 1906 structured records.")
    parser.add_argument("--structured", required=True, type=Path)
    parser.add_argument("--current-evidence", action="append", type=Path, default=[])
    parser.add_argument("--wiktionary", type=Path, default=DEFAULT_WIKTIONARY)
    parser.add_argument("--historical-entries", type=Path, default=DEFAULT_HISTORICAL_ENTRIES)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    current_paths = [DEFAULT_SEED, *args.current_evidence]
    rows = build_overlay(args.structured, current_paths, args.wiktionary, args.historical_entries)
    write_overlay(args.output, rows)
    result = report(rows)
    if result["verified_records_created"]:
        raise SystemExit("Modern evidence pass must never create verified rows")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
