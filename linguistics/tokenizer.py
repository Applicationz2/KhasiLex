from __future__ import annotations
import re
import unicodedata

WORD_RE = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*", re.UNICODE)


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def normalize_token(text: str) -> str:
    return nfc(text).casefold()


def tokenize(text: str):
    """Return Unicode-safe Khasi word tokens and character offsets."""
    text = nfc(text)
    return [
        {"text": m.group(0), "start": m.start(), "end": m.end(), "normalized": normalize_token(m.group(0))}
        for m in WORD_RE.finditer(text)
    ]


def detect_adjacent_reduplication(text: str):
    """Detect exact adjacent full reduplication such as X X or X X X."""
    tokens = tokenize(text)
    found = []
    i = 0
    while i < len(tokens) - 1:
        a, b = tokens[i], tokens[i + 1]
        if a["normalized"] == b["normalized"]:
            j = i + 1
            while j + 1 < len(tokens) and tokens[j + 1]["normalized"] == a["normalized"]:
                j += 1
            group = tokens[i:j + 1]
            found.append({
                "surface": " ".join(t["text"] for t in group),
                "base_form": a["text"],
                "normalized_base": a["normalized"],
                "repeat_count": len(group),
                "type": "full_reduplication_candidate",
                "pattern": " ".join(["X"] * len(group)),
                "start": group[0]["start"],
                "end": group[-1]["end"],
                "tokens": [t["text"] for t in group],
            })
            i = j + 1
        else:
            i += 1
    return found
