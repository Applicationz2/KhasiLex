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
AI_GATE = ROOT / "quality/ai_architecture_gate.json"

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


def _ai_gate() -> dict:
    if not AI_GATE.exists():
        return {"gate_id": None, "required_controls": {}}
    return json.loads(AI_GATE.read_text(encoding="utf-8"))


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

    architecture_gate = targets[target].get("required_architecture_gate")
    architecture_ready = True
    architecture_errors: list[str] = []
    if architecture_gate:
        gate = _ai_gate()
        if gate.get("gate_id") != architecture_gate:
            architecture_ready = False
            architecture_errors.append(
                f"{target}: required architecture gate {architecture_gate} is missing or mismatched"
            )
        controls = gate.get("required_controls") or {}
        failed_controls = [name for name, enabled in controls.items() if enabled is not True]
        if failed_controls:
            architecture_ready = False
            architecture_errors.append(
                f"{target}: architecture controls not enabled: {', '.join(sorted(failed_controls))}"
            )
        required_confidence = {
            "verified",
            "high_confidence_ai_assisted",
            "ai_assisted",
            "low_resource",
            "historical_or_uncertain",
            "needs_human_review",
        }
        present_confidence = set(gate.get("confidence_classes") or [])
        missing_confidence = sorted(required_confidence - present_confidence)
        if missing_confidence:
            architecture_ready = False
            architecture_errors.append(
                f"{target}: missing confidence classes: {', '.join(missing_confidence)}"
            )
        errors.extend(architecture_errors)

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
        "required_architecture_gate": architecture_gate,
        "architecture_ready": architecture_ready,
        "architecture_errors": architecture_errors,
        "errors": errors,
        "ready": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate KhasiLex release readiness.")
    parser.add_argument(
        "--target",
        choices=("review-pilot", "technical-alpha", "public-beta", "extended-beta-quality-gate", "professional-core"),
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
