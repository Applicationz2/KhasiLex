from pathlib import Path
import csv
import unicodedata

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from api.corpus import corpus_stats, filter_entries
from api.multilingual import resolve_equivalent, is_bcp47_like
from linguistics.phrase_matcher import match_phrases
from linguistics.tokenizer import tokenize, detect_adjacent_reduplication

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/master/khasi_lexicon.csv"

app = FastAPI(
    title="KhasiLex API",
    version="0.4.0",
    description="Professional Khasi lexicon, authoritative corpus, phrase, reduplication, spell-checking and NLP API",
)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def load_entries():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "KhasiLex",
        "version": "0.4.0",
        "language": "kha",
        "script": "Latn",
    }


@app.get("/api/v1/words/{word}")
def get_word(word: str):
    """Development lookup. May return pending/reviewed entries."""
    target = normalize(word).casefold()
    for entry in load_entries():
        if normalize(entry["headword"]).casefold() == target:
            return entry
    raise HTTPException(status_code=404, detail="Lexical entry not found")


@app.get("/api/v1/authoritative/words/{word}")
def get_authoritative_word(word: str):
    """Production-safe lookup: only human-verified Khasi entries are returned."""
    target = normalize(word).casefold()
    for entry in load_entries():
        if entry.get("verification_status") != "verified":
            continue
        if normalize(entry["headword"]).casefold() == target:
            return entry
    raise HTTPException(status_code=404, detail="No verified lexical entry found")


@app.get("/api/v1/corpus/stats")
def get_corpus_stats():
    return corpus_stats()


@app.get("/api/v1/corpus/entries")
def get_corpus_entries(
    status: str = Query(default="verified"),
    entry_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
):
    try:
        results = filter_entries(status=status, entry_type=entry_type, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "status": status,
        "entry_type": entry_type,
        "count": len(results),
        "results": results,
    }


@app.get("/api/v1/reduplications")
def reduplications(q: str = ""):
    target = normalize(q).casefold()
    entries = [e for e in load_entries() if e.get("entry_type") == "reduplication"]
    if target:
        entries = [e for e in entries if target in normalize(e["headword"]).casefold()]
    return {"count": len(entries), "results": entries}


@app.get("/api/v1/search")
def search(q: str = Query(min_length=1), limit: int = Query(default=20, ge=1, le=100)):
    query = normalize(q).casefold()
    results = []
    for entry in load_entries():
        fields = [
            entry.get(k, "")
            for k in (
                "headword",
                "lemma",
                "base_form",
                "definition_kha",
                "definition_en",
                "synonyms",
                "variants",
            )
        ]
        if any(query in normalize(v).casefold() for v in fields):
            results.append(entry)
            if len(results) >= limit:
                break
    return {"query": q, "count": len(results), "results": results}


class TextRequest(BaseModel):
    text: str


@app.post("/api/v1/analyze")
def analyze(req: TextRequest):
    return {
        "language": "kha",
        "normalized": normalize(req.text),
        "tokens": tokenize(req.text),
        "reduplications": detect_adjacent_reduplication(req.text),
        "lexicalized_phrase_matches": match_phrases(req.text),
    }


@app.post("/api/v1/normalize")
def normalize_api(req: TextRequest):
    return {"original": req.text, "normalized": normalize(req.text)}


class ResolveRequest(BaseModel):
    source_language: str
    text: str
    context: str = ""
    require_verified: bool = True


@app.post("/api/v2/resolve-to-khasi")
def resolve_to_khasi(req: ResolveRequest):
    return resolve_equivalent(req.source_language, req.text, req.context, req.require_verified)


@app.get("/api/v2/language-tag/check")
def language_tag_check(tag: str):
    return {"tag": tag, "accepted_syntax": is_bcp47_like(tag)}


@app.get("/api/v2/capabilities")
def capabilities():
    return {
        "language": "kha",
        "version": "0.4.0",
        "architecture": "sense/concept based multilingual lexicon with authoritative corpus gates",
        "accepts": "BCP47-style source language tags",
        "features": [
            "word lookup",
            "verified-only production lookup",
            "corpus quality statistics",
            "multiword expressions",
            "reduplication",
            "sense disambiguation hooks",
            "grammar profiles",
            "pronunciation schema",
            "multilingual equivalents",
        ],
        "safety_policy": "No translation is guessed and no unreviewed entry is presented as authoritative.",
    }
