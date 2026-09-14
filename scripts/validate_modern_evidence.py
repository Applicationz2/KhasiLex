from __future__ import annotations

import csv
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "sources" / "source_registry.csv"
SEED = ROOT / "data" / "modern_evidence" / "current_attestations_seed.csv"

REQUIRED = {
    "headword",
    "source_id",
    "evidence_type",
    "source_url",
    "source_date_or_version",
    "minimum_occurrences",
    "attestation_scope",
    "license",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate() -> list[str]:
    errors: list[str] = []
    registry_rows = read_rows(REGISTRY)
    registry = {row.get("source_id", ""): row for row in registry_rows}
    rows = read_rows(SEED)

    if not rows:
        errors.append("modern evidence seed is empty")
        return errors

    if not REQUIRED <= set(rows[0]):
        errors.append(f"modern evidence seed missing columns: {sorted(REQUIRED - set(rows[0]))}")
        return errors

    seen: set[tuple[str, str]] = set()
    for line_no, row in enumerate(rows, start=2):
        headword = (row.get("headword") or "").strip()
        source_id = (row.get("source_id") or "").strip()
        if not headword:
            errors.append(f"line {line_no}: missing headword")
            continue
        if unicodedata.normalize("NFC", headword) != headword:
            errors.append(f"line {line_no}: headword is not NFC: {headword!r}")

        source = registry.get(source_id)
        if not source:
            errors.append(f"line {line_no}: unregistered source_id {source_id!r}")
        elif source.get("status") != "approved":
            errors.append(f"line {line_no}: source {source_id!r} is not approved")
        elif row.get("license") != source.get("license"):
            errors.append(
                f"line {line_no}: licence mismatch for {source_id!r}: "
                f"{row.get('license')!r} != {source.get('license')!r}"
            )

        try:
            minimum = int(row.get("minimum_occurrences") or "0")
            if minimum < 1:
                raise ValueError
        except ValueError:
            errors.append(f"line {line_no}: minimum_occurrences must be a positive integer")

        identity = (headword.casefold(), source_id)
        if identity in seen:
            errors.append(f"line {line_no}: duplicate headword/source evidence: {identity}")
        seen.add(identity)

        if row.get("attestation_scope") not in {
            "exact lexical occurrence",
            "exact lexical occurrence in published corpus sample",
        }:
            errors.append(f"line {line_no}: unsupported attestation_scope {row.get('attestation_scope')!r}")

    return errors


def main() -> None:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Modern evidence seed validation passed.")


if __name__ == "__main__":
    main()
