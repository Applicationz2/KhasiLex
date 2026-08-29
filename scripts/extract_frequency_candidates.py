from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import argparse
import csv
import json
import sys
import unicodedata

from linguistics.tokenizer import tokenize

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/sources/source_registry.csv"
MASTER = ROOT / "data/master/khasi_lexicon.csv"

OUTPUT_FIELDS = [
    "headword", "entry_type", "part_of_speech", "definition_kha", "definition_en",
    "base_form", "reduplication_type", "reduplication_pattern", "grammatical_function",
    "variants", "synonyms", "antonyms", "example_kha", "example_en", "domain",
    "frequency", "source", "source_evidence", "license", "notes",
]


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def source_record(source_id: str):
    with REGISTRY.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("source_id") == source_id:
                if row.get("status") != "approved":
                    raise ValueError(f"source {source_id!r} is not approved")
                return row
    raise ValueError(f"source {source_id!r} is not registered")


def existing_master_keys():
    with MASTER.open(encoding="utf-8", newline="") as f:
        return {
            nfc(row.get("headword", "")).casefold()
            for row in csv.DictReader(f)
            if nfc(row.get("headword", ""))
        }


def iter_text(input_path: Path, fmt: str, text_fields: list[str]):
    if fmt == "txt":
        yield input_path.read_text(encoding="utf-8-sig")
        return

    if fmt == "jsonl":
        fields = text_fields or ["text"]
        with input_path.open(encoding="utf-8-sig") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL at line {line_no}: {exc}") from exc
                for field in fields:
                    value = obj.get(field)
                    if isinstance(value, str) and value.strip():
                        yield value
        return

    if fmt == "csv":
        fields = text_fields or ["text"]
        with input_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for field in fields:
                    value = row.get(field)
                    if value and value.strip():
                        yield value
        return

    raise ValueError(f"unsupported format: {fmt}")


def guess_format(path: Path):
    suffix = path.suffix.lower()
    if suffix in {".txt", ".text"}:
        return "txt"
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    raise ValueError("cannot infer input format; use --format")


def main():
    parser = argparse.ArgumentParser(
        description="Extract frequency-ranked Khasi lexical candidates from an approved corpus source."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--format", choices=["auto", "txt", "jsonl", "csv"], default="auto")
    parser.add_argument("--text-field", action="append", default=[])
    parser.add_argument("--min-frequency", type=int, default=2)
    parser.add_argument("--min-length", type=int, default=1)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--include-existing", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "data/pending/frequency_candidates.csv")
    args = parser.parse_args()

    if args.min_frequency < 1 or args.min_length < 1 or args.limit < 1:
        parser.error("--min-frequency, --min-length and --limit must be positive")

    try:
        source = source_record(args.source_id)
        fmt = guess_format(args.input) if args.format == "auto" else args.format
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    counts = Counter()
    surfaces = defaultdict(Counter)
    contexts = defaultdict(list)

    try:
        for text in iter_text(args.input, fmt, args.text_field):
            tokens = tokenize(text)
            for token in tokens:
                surface = nfc(token["text"])
                if len(surface) < args.min_length:
                    continue
                key = surface.casefold()
                counts[key] += 1
                surfaces[key][surface] += 1
                if len(contexts[key]) < 3:
                    left = max(0, token["start"] - 60)
                    right = min(len(text), token["end"] + 60)
                    contexts[key].append(" ".join(text[left:right].split()))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    existing = existing_master_keys()
    candidates = []
    for key, frequency in counts.most_common():
        if frequency < args.min_frequency:
            continue
        if not args.include_existing and key in existing:
            continue

        # Preserve the most frequent observed NFC surface form. Editors decide the canonical form.
        surface = surfaces[key].most_common(1)[0][0]
        evidence = " || ".join(contexts[key])
        candidates.append({
            "headword": surface,
            "entry_type": "word",
            "part_of_speech": "",
            "definition_kha": "",
            "definition_en": "",
            "base_form": surface,
            "reduplication_type": "",
            "reduplication_pattern": "",
            "grammatical_function": "",
            "variants": "",
            "synonyms": "",
            "antonyms": "",
            "example_kha": "",
            "example_en": "",
            "domain": "corpus_candidate",
            "frequency": str(frequency),
            "source": args.source_id,
            "source_evidence": evidence,
            "license": source.get("license", ""),
            "notes": "Frequency-derived candidate only; canonical spelling, sense and grammar require human review.",
        })
        if len(candidates) >= args.limit:
            break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(candidates)

    report = {
        "source_id": args.source_id,
        "source_title": source.get("title"),
        "source_license": source.get("license"),
        "input_format": fmt,
        "unique_tokens_observed": len(counts),
        "candidates_written": len(candidates),
        "min_frequency": args.min_frequency,
        "excluded_existing_master": not args.include_existing,
        "output": str(args.output),
        "verification_status": "pending",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
