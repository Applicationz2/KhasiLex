from __future__ import annotations

from pathlib import Path
import argparse
import csv
import json
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "data/master/khasi_lexicon.csv"
TARGETS = ROOT / "quality/corpus_targets.json"
LICENSE_DECISION = ROOT / "governance/DATA_LICENSE_DECISION.json"

V1_REQUIRED = (
    "headword",
    "part_of_speech",
    "definition_kha",
    "definition_en",
    "example_kha",
    "register",
    "dialect",
    "source",
    "license",
    "reviewer",
    "last_reviewed",
)


def _read_rows() -> list[dict[str, str]]:
    with LEXICON.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _targets() -> dict:
    return json.loads(TARGETS.read_text(encoding="utf-8"))


def _license_decision() -> dict:
    if not LICENSE_DECISION.exists():
        return {"status": "missing", "license_id": None}
    return json.loads(LICENSE_DECISION.read_text(encoding="utf-8"))


def evaluate(target: str) -> dict:
    targets = _targets().get("milestones", {})
    if target not in targets:
        raise ValueError(f"unknown release target: {target}")

    required_count = int(targets[target]["verified_entries"])
    rows = _read_rows()
    verified = [row for row in rows if row.get("verification_status") == "verified"]
    errors: list[str] = []

    for row in verified:
        entry_id = row.get("id") or "<unknown>"
        for field in V1_REQUIRED:
            if not (row.get(field) or "").strip():
                errors.append(f"{entry_id}: verified entry missing v1 field {field}")
        for field in ("headword", "definition_kha", "example_kha"):
            value = (row.get(field) or "").strip()
            if value and unicodedata.normalize("NFC", value) != value:
                errors.append(f"{entry_id}: {field} is not Unicode NFC")

    licence = _license_decision()
    licence_ready = (
        licence.get("status") == "approved"
        and bool((licence.get("license_id") or "").strip())
    )
    if not licence_ready:
        errors.append("KhasiLex-authored linguistic-data licence has not been explicitly approved")

    if len(verified) < required_count:
        errors.append(
            f"{target}: requires {required_count} verified entries; found {len(verified)}"
        )

    return {
        "schema_version": "1.0",
        "target": target,
        "required_verified_entries": required_count,
        "verified_entries": len(verified),
        "remaining_verified_entries": max(0, required_count - len(verified)),
        "data_license_status": licence.get("status"),
        "data_license_id": licence.get("license_id"),
        "errors": errors,
        "ready": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate KhasiLex release readiness.")
    parser.add_argument(
        "--target",
        choices=("review-pilot", "technical-alpha", "public-beta", "professional-core"),
        default="professional-core",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when the requested target is not release-ready.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = evaluate(args.target)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")

    if args.strict and not report["ready"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
