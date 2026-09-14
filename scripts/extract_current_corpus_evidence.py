from __future__ import annotations

import argparse
import csv
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from linguistics.tokenizer import tokenize

REGISTRY = ROOT / "data" / "sources" / "source_registry.csv"

FIELDS = [
    "headword",
    "normalized",
    "match_type",
    "current_surface",
    "source_id",
    "frequency",
    "document_frequency",
    "source_url",
    "license",
    "contexts",
]


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def key(text: str) -> str:
    return nfc(text).casefold()


def diacritic_fold(text: str) -> str:
    # Khasi digital text frequently drops ï/ñ. This fold is evidence-only and
    # must never silently replace the canonical spelling.
    value = key(text).replace("ï", "i").replace("ñ", "n")
    return value.replace("ʼ", "'").replace("’", "'")


def source_record(source_id: str) -> dict[str, str]:
    with REGISTRY.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("source_id") == source_id:
                if row.get("status") != "approved":
                    raise ValueError(f"source {source_id!r} is not approved")
                return row
    raise ValueError(f"source {source_id!r} is not registered")


def read_targets(path: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    exact: dict[str, set[str]] = defaultdict(set)
    folded: dict[str, set[str]] = defaultdict(set)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            headword = nfc(row.get("historical_headword", ""))
            if not headword:
                continue
            exact[key(headword)].add(headword)
            folded[diacritic_fold(headword)].add(headword)
    return exact, folded


def iter_documents(path: Path, text_field: str):
    with path.open(encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at line {line_no}: {exc}") from exc
            text = obj.get(text_field)
            if isinstance(text, str) and text.strip():
                yield text


def extract(
    corpus_path: Path,
    structured_path: Path,
    source_id: str,
    text_field: str = "text",
) -> list[dict[str, str]]:
    source = source_record(source_id)
    exact_targets, folded_targets = read_targets(structured_path)

    counts: Counter[tuple[str, str, str]] = Counter()
    docs: dict[tuple[str, str, str], set[int]] = defaultdict(set)
    surfaces: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    contexts: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    for doc_no, text in enumerate(iter_documents(corpus_path, text_field), start=1):
        for token in tokenize(text):
            surface = nfc(token["text"])
            if not surface:
                continue
            exact_key = key(surface)
            matches = exact_targets.get(exact_key, set())
            match_type = "exact"
            if not matches:
                folded_key = diacritic_fold(surface)
                matches = folded_targets.get(folded_key, set())
                if not matches:
                    continue
                match_type = (
                    "diacritic_variant_candidate" if len(matches) == 1
                    else "ambiguous_diacritic_variant"
                )

            for headword in sorted(matches):
                evidence_key = (headword, match_type, exact_key)
                counts[evidence_key] += 1
                docs[evidence_key].add(doc_no)
                surfaces[evidence_key][surface] += 1
                if len(contexts[evidence_key]) < 3:
                    left = max(0, token["start"] - 50)
                    right = min(len(text), token["end"] + 50)
                    contexts[evidence_key].append(" ".join(text[left:right].split()))

    rows: list[dict[str, str]] = []
    for evidence_key, frequency in counts.most_common():
        headword, match_type, _ = evidence_key
        surface = surfaces[evidence_key].most_common(1)[0][0]
        rows.append(
            {
                "headword": headword,
                "normalized": key(headword),
                "match_type": match_type,
                "current_surface": surface,
                "source_id": source_id,
                "frequency": str(frequency),
                "document_frequency": str(len(docs[evidence_key])),
                "source_url": source.get("canonical_url", ""),
                "license": source.get("license", ""),
                "contexts": " || ".join(contexts[evidence_key]),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract modern-use evidence for Nissor 1906 headwords from an approved Khasi JSONL corpus."
    )
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--structured", required=True, type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        rows = extract(args.corpus, args.structured, args.source_id, args.text_field)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    exact = sum(row["match_type"] == "exact" for row in rows)
    variants = sum(row["match_type"] != "exact" for row in rows)
    print(
        json.dumps(
            {
                "source_id": args.source_id,
                "evidence_rows": len(rows),
                "exact_rows": exact,
                "variant_candidate_rows": variants,
                "policy": "Corpus frequency establishes occurrence evidence only; it never verifies meaning or canonical spelling by itself.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
