from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import csv
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/sources/source_registry.csv"

REQUIRED = {
    "source_id", "title", "source_type", "canonical_url", "license",
    "attribution_required", "share_alike", "approved_use",
    "definition_import_policy", "status",
}
VALID_STATUS = {"approved", "pending", "disabled"}
YES_NO = {"yes", "no"}


def main():
    errors = []
    seen = set()

    with REGISTRY.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED - fields
        if missing:
            errors.append(f"Missing source-registry columns: {sorted(missing)}")

        for line_no, row in enumerate(reader, start=2):
            source_id = (row.get("source_id") or "").strip()
            if not source_id:
                errors.append(f"Line {line_no}: missing source_id")
            elif source_id in seen:
                errors.append(f"Line {line_no}: duplicate source_id {source_id}")
            seen.add(source_id)

            for field in ("title", "source_type", "canonical_url", "license", "approved_use", "definition_import_policy"):
                if not (row.get(field) or "").strip():
                    errors.append(f"Line {line_no}: missing {field}")

            parsed = urlparse((row.get("canonical_url") or "").strip())
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                errors.append(f"Line {line_no}: canonical_url must be an http(s) URL")

            if row.get("status") not in VALID_STATUS:
                errors.append(f"Line {line_no}: invalid source status")
            if row.get("attribution_required") not in YES_NO:
                errors.append(f"Line {line_no}: attribution_required must be yes/no")
            if row.get("share_alike") not in YES_NO:
                errors.append(f"Line {line_no}: share_alike must be yes/no")

            if row.get("status") == "approved" and not (row.get("license") or "").strip():
                errors.append(f"Line {line_no}: approved source requires licence metadata")

    if errors:
        print("SOURCE REGISTRY VALIDATION FAILED")
        for error in errors:
            print("-", error)
        sys.exit(1)

    print(f"SOURCE REGISTRY VALIDATION PASSED: {len(seen)} sources")


if __name__ == "__main__":
    main()
