from __future__ import annotations
from pathlib import Path
import csv
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/multilingual"

BCP47_RE = re.compile(
    r"^(?P<language>[A-Za-z]{2,8})"
    r"(?:-(?P<script>[A-Za-z]{4}))?"
    r"(?:-(?P<region>[A-Za-z]{2}|\d{3}))?"
    r"(?:-[A-Za-z0-9]{1,8})*$"
)


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def fold(text: str) -> str:
    return nfc(text).casefold()


def is_bcp47_like(tag: str) -> bool:
    return bool(BCP47_RE.match((tag or "").strip()))


def read_csv(name: str):
    with (DATA / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def resolve_equivalent(source_language: str, text: str, context: str = "", require_verified: bool = True):
    if not is_bcp47_like(source_language):
        return {"status": "invalid_language_tag", "source_language": source_language}

    equivalents = read_csv("equivalents.csv")
    concepts = {r["concept_id"]: r for r in read_csv("concepts.csv")}
    senses = {r["sense_id"]: r for r in read_csv("senses.csv")}

    matches = []
    for row in equivalents:
        if fold(row["language_tag"]) == fold(source_language) and fold(row["lemma"]) == fold(text):
            if require_verified and row.get("verification_status") != "verified":
                continue
            matches.append({
                "source_equivalent": row,
                "sense": senses.get(row["sense_id"], {}),
                "concept": concepts.get(row["concept_id"], {}),
            })

    if not matches:
        return {
            "status": "not_found",
            "source_language": source_language,
            "text": text,
            "require_verified": require_verified,
            "message": "No reviewed sense mapping is available. Do not guess a Khasi translation.",
        }

    concept_ids = {m["source_equivalent"]["concept_id"] for m in matches}
    if len(concept_ids) > 1:
        return {
            "status": "ambiguous",
            "source_language": source_language,
            "text": text,
            "context": context,
            "candidates": matches,
            "message": "Multiple senses match. Context/sense disambiguation is required.",
        }

    concept_id = next(iter(concept_ids))
    khasi = [
        row for row in equivalents
        if row["concept_id"] == concept_id
        and row["language_tag"] == "kha"
        and (not require_verified or row.get("verification_status") == "verified")
    ]

    return {
        "status": "resolved" if khasi else "concept_found_no_verified_khasi",
        "source_language": source_language,
        "text": text,
        "context": context,
        "concept_id": concept_id,
        "khasi_equivalents": khasi,
        "sense": matches[0]["sense"],
        "concept": matches[0]["concept"],
    }
