from pathlib import Path
import csv
import unicodedata
import sys

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/master/khasi_lexicon.csv"
REQUIRED = {"id", "headword", "normalized", "language", "verification_status", "entry_type", "lemma", "token_count", "script", "bcp47"}
VALID_ENTRY_TYPES = {"word", "phrase", "reduplication", "compound", "idiom"}
VALID_REVIEW = {"pending", "reviewed", "verified"}


def main():
    errors = []
    seen_ids = set()
    seen_words = set()
    count = 0

    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            errors.append(f"Missing columns: {sorted(missing)}")

        for line_no, row in enumerate(reader, start=2):
            count += 1
            word = (row.get("headword") or "").strip()
            entry_id = (row.get("id") or "").strip()
            if not entry_id:
                errors.append(f"Line {line_no}: missing id")
            elif entry_id in seen_ids:
                errors.append(f"Line {line_no}: duplicate id {entry_id}")
            seen_ids.add(entry_id)

            key = unicodedata.normalize("NFC", word).casefold()
            if not word:
                errors.append(f"Line {line_no}: missing headword")
            elif key in seen_words:
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
            if row.get("verification_status") not in VALID_REVIEW:
                errors.append(f"Line {line_no}: invalid verification_status")
            if row.get("entry_type") not in VALID_ENTRY_TYPES:
                errors.append(f"Line {line_no}: invalid entry_type")

            actual_tokens = len(word.split())
            try:
                declared = int(row.get("token_count") or 0)
            except ValueError:
                declared = -1
            if actual_tokens != declared:
                errors.append(f"Line {line_no}: token_count mismatch")

            if row.get("entry_type") == "reduplication":
                if actual_tokens < 2 or not row.get("base_form") or not row.get("reduplication_type"):
                    errors.append(f"Line {line_no}: incomplete reduplication metadata")

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print("-", error)
        sys.exit(1)

    print(f"VALIDATION PASSED: {count} lexical entries")


if __name__ == "__main__":
    main()
