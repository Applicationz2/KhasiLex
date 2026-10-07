from __future__ import annotations

from pathlib import Path
import argparse
import csv
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/master/khasi_lexicon.csv"
OUT = ROOT / "dictionaries/microsoft-word/Khasi.dic"


def build_words(include_unverified: bool = False, src: Path = SRC) -> list[str]:
    words: set[str] = set()
    with src.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if not include_unverified and row.get("verification_status") != "verified":
                continue
            candidates: list[str] = []
            for field in ("headword", "variants", "inflections", "base_form"):
                value = row.get(field) or ""
                parts = value.split("|") if field in {"variants", "inflections"} else [value]
                candidates.extend(parts)
            for part in candidates:
                part = unicodedata.normalize("NFC", part.strip())
                if part and " " not in part:
                    words.add(part)
    return sorted(words, key=str.casefold)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a Microsoft Word Khasi word list. Verified-only by default."
    )
    parser.add_argument(
        "--include-unverified",
        action="store_true",
        help="Development-only: include pending/reviewed lexical forms.",
    )
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()

    words = build_words(include_unverified=args.include_unverified)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(words) + ("\n" if words else ""), encoding="utf-8")
    mode = "all review states" if args.include_unverified else "verified-only"
    print(f"Wrote {len(words)} single-token words ({mode}) to {args.output}")


if __name__ == "__main__":
    main()
