from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "data/master/khasi_lexicon.csv"
TARGETS = ROOT / "quality/corpus_targets.json"
REPORT = ROOT / "quality/corpus_report.json"

VERIFIED_REQUIRED = (
    "part_of_speech",
    "definition_kha",
    "source",
    "license",
    "reviewer",
    "last_reviewed",
)


def _read_rows():
    with LEXICON.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_targets():
    if not TARGETS.exists():
        return {}
    return json.loads(TARGETS.read_text(encoding="utf-8"))


def _blank(row, key):
    return not (row.get(key) or "").strip()


def main():
    rows = _read_rows()
    targets = _read_targets()
    errors = []
    warnings = []

    status_counts = Counter((r.get("verification_status") or "missing") for r in rows)
    type_counts = Counter((r.get("entry_type") or "missing") for r in rows)
    pos_counts = Counter((r.get("part_of_speech") or "unclassified") for r in rows)

    verified = [r for r in rows if r.get("verification_status") == "verified"]
    reviewed = [r for r in rows if r.get("verification_status") == "reviewed"]
    pending = [r for r in rows if r.get("verification_status") == "pending"]

    for row in verified:
        entry_id = row.get("id") or "<unknown>"
        for field in VERIFIED_REQUIRED:
            if _blank(row, field):
                errors.append(f"{entry_id}: verified entry missing {field}")

        if row.get("source") == "starter seed" or row.get("license") == "CC0-example":
            errors.append(f"{entry_id}: illustrative seed metadata cannot be published as verified")

        if row.get("translation_status") == "verified" and _blank(row, "definition_en"):
            errors.append(f"{entry_id}: verified translation requires definition_en")

        if row.get("entry_type") == "reduplication":
            for field in ("base_form", "reduplication_type", "reduplication_pattern", "grammatical_function"):
                if _blank(row, field):
                    errors.append(f"{entry_id}: verified reduplication missing {field}")

        try:
            y, m, d = map(int, (row.get("last_reviewed") or "").split("-"))
            reviewed_on = date(y, m, d)
            if reviewed_on > date.today():
                errors.append(f"{entry_id}: last_reviewed is in the future")
        except Exception:
            errors.append(f"{entry_id}: last_reviewed must use YYYY-MM-DD")

    if not verified:
        warnings.append("No entries are verified yet; v0.4 remains corpus-foundation stage.")

    milestones = targets.get("milestones", {})
    next_target = None
    for name, spec in milestones.items():
        required = int(spec.get("verified_entries", 0))
        if len(verified) < required:
            next_target = {
                "name": name,
                "verified_entries_required": required,
                "remaining": required - len(verified),
            }
            break

    report = {
        "schema_version": "0.4",
        "total_entries": len(rows),
        "verification": dict(status_counts),
        "entry_types": dict(type_counts),
        "parts_of_speech": dict(pos_counts),
        "verified_entries": len(verified),
        "reviewed_entries": len(reviewed),
        "pending_entries": len(pending),
        "verified_percent": round((len(verified) / len(rows) * 100), 2) if rows else 0.0,
        "next_target": next_target,
        "errors": errors,
        "warnings": warnings,
        "production_ready": not errors and bool(verified),
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
