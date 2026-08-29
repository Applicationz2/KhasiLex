from pathlib import Path
import csv
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/master/khasi_lexicon.csv"
OUT = ROOT / "dictionaries/microsoft-word/Khasi.dic"
OUT.parent.mkdir(parents=True, exist_ok=True)

words = set()
with SRC.open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        candidates = []
        for field in ("headword", "variants", "inflections", "base_form"):
            value = row.get(field) or ""
            parts = value.split("|") if field in {"variants", "inflections"} else [value]
            candidates.extend(parts)
        for part in candidates:
            part = unicodedata.normalize("NFC", part.strip())
            if part and " " not in part:
                words.add(part)

OUT.write_text("\n".join(sorted(words, key=str.casefold)) + "\n", encoding="utf-8")
print(f"Wrote {len(words)} single-token words to {OUT}")
