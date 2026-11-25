from __future__ import annotations
import unicodedata



def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def normalize_token(text: str) -> str:
    return nfc(text).casefold()


def tokenize(text: str):
    """Return original surface tokens and original Python character offsets.

    Letters and attached combining marks are retained; apostrophes and ASCII
    hyphens are internal connectors only when followed by a letter.
    """
    tokens = []
    i = 0
    while i < len(text):
        if not unicodedata.category(text[i]).startswith("L"):
            i += 1
            continue
        start = i
        i += 1
        while i < len(text):
            category = unicodedata.category(text[i])
            if category.startswith(("L", "M")):
                i += 1
            elif (text[i] in "'’-"
                  and i + 1 < len(text)
                  and unicodedata.category(text[i + 1]).startswith("L")):
                i += 1
            else:
                break
        surface = text[start:i]
        tokens.append({"text": surface, "start": start, "end": i,
                       "normalized": normalize_token(surface)})
    return tokens


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
