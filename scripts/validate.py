from __future__ import annotations

from datetime import date
from pathlib import Path
import csv
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/master/khasi_lexicon.csv"

REQUIRED = {
    "id", "headword", "normalized", "language", "verification_status",
    "translation_status", "entry_type", "lemma", "token_count", "script",
    "bcp47", "source", "license", "reviewer", "last_reviewed",
    "part_of_speech", "definition_kha",
}
VALID_ENTRY_TYPES = {"word", "phrase", "reduplication", "compound", "idiom"}
VALID_REVIEW = {"pending", "reviewed", "verified"}
VALID_TRANSLATION = {"pending", "reviewed", "verified", "not_applicable"}


def is_blank(row, key):
    return not (row.get(key) or "").strip()


def valid_review_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        return False, "must use YYYY-MM-DD"
    if parsed > date.today():
        return False, "cannot be in the future"
    return True, ""


def main():
    errors = []
    seen_ids = set()
    seen_words = set()
    count = 0

    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED - fields
        if missing:
            errors.append(f"Missing columns: {sorted(missing)}")

        for line_no, row in enumerate(reader, start=2):
            count += 1
            word = (row.get("headword") or "").strip()
            entry_id = (row.get("id") or "").strip()
            status = (row.get("verification_status") or "").strip()
            translation_status = (row.get("translation_status") or "").strip()
            entry_type = (row.get("entry_type") or "").strip()

            if not entry_id:
                errors.append(f"Line {line_no}: missing id")
            elif entry_id in seen_ids:
                errors.append(f"Line {line_no}: duplicate id {entry_id}")
            else:
                seen_ids.add(entry_id)

            if not word:
                errors.append(f"Line {line_no}: missing headword")
            else:
                key = unicodedata.normalize("NFC", word).casefold()
                if key in seen_words:
                    errors.append(f"Line {line_no}: duplicate headword {word}")
                seen_words.add(key)

            if row.get("language") != "kha":
                errors.append(f"Line {line_no}: language should be kha")
            if row.get("bcp47") not in {"kha", "kha-IN"}:
                errors.append(f"Line {line_no}: invalid Khasi language tag")
            if row.get("script") != "Latn":
                errors.append(f"Line {line_no}: script should be Latn")
            if row.get("normalized") != unicodedata.normalize("NFC", word):
                errors.append(f"Line {line_no}: normalized form is not NFC")
            if status not in VALID_REVIEW:
                errors.append(f"Line {line_no}: invalid verification_status")
            if translation_status not in VALID_TRANSLATION:
                errors.append(f"Line {line_no}: invalid translation_status")
            if entry_type not in VALID_ENTRY_TYPES:
                errors.append(f"Line {line_no}: invalid entry_type")

            actual_tokens = len(word.split()) if word else 0
            try:
                declared = int(row.get("token_count") or 0)
            except ValueError:
                declared = -1
            if actual_tokens != declared:
                errors.append(f"Line {line_no}: token_count mismatch")

            if entry_type == "word" and actual_tokens != 1:
                errors.append(f"Line {line_no}: word entries must contain exactly one token")

            if entry_type == "reduplication":
                if actual_tokens < 2:
                    errors.append(f"Line {line_no}: reduplication must contain at least two tokens")
                for field in ("base_form", "reduplication_type", "reduplication_pattern"):
                    if is_blank(row, field):
                        errors.append(f"Line {line_no}: reduplication missing {field}")

            if status in {"reviewed", "verified"}:
                for field in ("source", "license", "reviewer", "last_reviewed"):
                    if is_blank(row, field):
                        errors.append(f"Line {line_no}: {status} entry missing {field}")
                if not is_blank(row, "last_reviewed"):
                    ok, reason = valid_review_date(row.get("last_reviewed"))
                    if not ok:
                        errors.append(f"Line {line_no}: last_reviewed {reason}")

            if status == "verified":
                for field in ("part_of_speech", "definition_kha"):
                    if is_blank(row, field):
                        errors.append(f"Line {line_no}: verified entry missing {field}")
                if row.get("source") == "starter seed" or row.get("license") == "CC0-example":
                    errors.append(f"Line {line_no}: illustrative seed data cannot be marked verified")
                if entry_type == "reduplication" and is_blank(row, "grammatical_function"):
                    errors.append(f"Line {line_no}: verified reduplication missing grammatical_function")

            if translation_status == "verified" and is_blank(row, "definition_en"):
                errors.append(f"Line {line_no}: verified translation requires definition_en")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print("-", error)
        sys.exit(1)

    print(f"VALIDATION PASSED: {count} lexical entries")


if __name__ == "__main__":
    main()
