from __future__ import annotations
import csv
import unicodedata
from pathlib import Path
from .tokenizer import tokenize

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/master/khasi_lexicon.csv"


def norm(text: str) -> str:
    return unicodedata.normalize("NFC", text or "").casefold().strip()


def load_multiword_entries():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return [
            row for row in csv.DictReader(f)
            if row.get("entry_type") in {"phrase", "reduplication", "compound", "idiom"}
            or " " in (row.get("headword") or "").strip()
        ]


def match_phrases(text: str):
    """Longest exact token-sequence matching for lexicalized Khasi multiword entries."""
    tokens = tokenize(text)
    entries = load_multiword_entries()
    index = {}
    for entry in entries:
        key = tuple(norm(t["text"]) for t in tokenize(entry["headword"]))
        if key:
            index[key] = entry

    matches = []
    max_len = max((len(k) for k in index), default=0)
    i = 0
    while i < len(tokens):
        hit = None
        for size in range(min(max_len, len(tokens) - i), 1, -1):
            key = tuple(t["normalized"] for t in tokens[i:i + size])
            if key in index:
                hit = (size, index[key])
                break
        if hit:
            size, entry = hit
            group = tokens[i:i + size]
            matches.append({
                "surface": text[group[0]["start"]:group[-1]["end"]],
                "headword": entry["headword"],
                "entry_id": entry["id"],
                "entry_type": entry.get("entry_type", ""),
                "verification_status": entry.get("verification_status", ""),
                "start": group[0]["start"],
                "end": group[-1]["end"],
            })
            i += size
        else:
            i += 1
    return matches
