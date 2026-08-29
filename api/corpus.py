from __future__ import annotations

from collections import Counter
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "data/master/khasi_lexicon.csv"
TARGETS = ROOT / "quality/corpus_targets.json"

VALID_STATUS = {"pending", "reviewed", "verified"}
VALID_TYPES = {"word", "phrase", "reduplication", "compound", "idiom"}


def load_entries():
    with LEXICON.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_targets():
    if not TARGETS.exists():
        return {}
    return json.loads(TARGETS.read_text(encoding="utf-8"))


def corpus_stats():
    rows = load_entries()
    statuses = Counter(r.get("verification_status") or "missing" for r in rows)
    types = Counter(r.get("entry_type") or "missing" for r in rows)
    verified = int(statuses.get("verified", 0))

    next_target = None
    for name, spec in load_targets().get("milestones", {}).items():
        required = int(spec.get("verified_entries", 0))
        if verified < required:
            next_target = {
                "name": name,
                "required": required,
                "remaining": required - verified,
            }
            break

    return {
        "version": "0.4.0",
        "language": "kha",
        "total_entries": len(rows),
        "verification": dict(statuses),
        "entry_types": dict(types),
        "verified_percent": round((verified / len(rows) * 100), 2) if rows else 0.0,
        "next_target": next_target,
        "public_data_policy": "Only human-reviewed verified entries should be treated as authoritative.",
    }


def filter_entries(status="verified", entry_type=None, limit=100):
    if status not in VALID_STATUS:
        raise ValueError("invalid verification status")
    if entry_type is not None and entry_type not in VALID_TYPES:
        raise ValueError("invalid entry type")

    results = []
    for row in load_entries():
        if row.get("verification_status") != status:
            continue
        if entry_type and row.get("entry_type") != entry_type:
            continue
        results.append(row)
        if len(results) >= limit:
            break
    return results
