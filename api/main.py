from pathlib import Path
import csv
import os
import unicodedata

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from api.corpus import corpus_stats, filter_entries
from api.multilingual import resolve_equivalent, is_bcp47_like
from api.runtime import docs_enabled, environment, is_production, production_guard
from linguistics.phrase_matcher import match_phrases
from linguistics.tokenizer import tokenize, detect_adjacent_reduplication

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/master/khasi_lexicon.csv"

app = FastAPI(
    title="KhasiLex API",
    version="0.4.0",
    description="Professional Khasi lexicon, authoritative corpus, phrase, reduplication, spell-checking and NLP API",
    docs_url="/docs" if docs_enabled() else None,
    redoc_url="/redoc" if docs_enabled() else None,
    openapi_url="/openapi.json" if docs_enabled() else None,
)

app.middleware("http")(production_guard)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def load_entries():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def public_entries():
    rows = load_entries()
    if is_production():
        return [row for row in rows if row.get("verification_status") == "verified"]
    return rows


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "KhasiLex",
        "version": "0.4.0",
        "language": "kha",
        "script": "Latn",
        "environment": environment(),
    }


@app.get("/ready")
def readiness():
    try:
        rows = load_entries()
    except (OSError, csv.Error, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail="Lexicon data unavailable") from exc
    return {
        "status": "ready",
        "service": "KhasiLex",
        "entries_loaded": len(rows),
        "authoritative_entries": sum(
            1 for row in rows if row.get("verification_status") == "verified"
        ),
    }


def _matches_word(entry: dict[str, str], word: str, part_of_speech: str | None) -> bool:
    if normalize(entry.get("headword", "")).casefold() != normalize(word).casefold():
        return False
    if part_of_speech is None:
        return True
    return normalize(entry.get("part_of_speech", "")).casefold() == normalize(part_of_speech).casefold()


@app.get("/api/v1/words/{word}")
def get_word(
    word: str,
    part_of_speech: str | None = Query(default=None, max_length=64),
):
    """Development lookup; in production it becomes verified-only.

    Homographs may coexist as separate lexical rows. Supply part_of_speech to
    select a specific row while preserving the legacy first-match behaviour
    when no POS filter is provided.
    """
    for entry in public_entries():
        if _matches_word(entry, word, part_of_speech):
            return entry
    if is_production():
        raise HTTPException(status_code=404, detail="No verified lexical entry found")
    raise HTTPException(status_code=404, detail="Lexical entry not found")


@app.get("/api/v1/authoritative/words/{word}")
def get_authoritative_word(
    word: str,
    part_of_speech: str | None = Query(default=None, max_length=64),
):
    """Production-safe lookup: only human-verified Khasi entries are returned."""
    for entry in load_entries():
        if entry.get("verification_status") != "verified":
            continue
        if _matches_word(entry, word, part_of_speech):
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
    if is_production() and status != "verified":
        raise HTTPException(
            status_code=403,
            detail="Production corpus access is restricted to verified entries",
        )
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
def reduplications(q: str = Query(default="", max_length=128)):
    target = normalize(q).casefold()
    entries = [e for e in public_entries() if e.get("entry_type") == "reduplication"]
    if target:
        entries = [e for e in entries if target in normalize(e["headword"]).casefold()]
    return {"count": len(entries), "results": entries}


@app.get("/api/v1/search")
def search(
    q: str = Query(min_length=1, max_length=128),
    limit: int = Query(default=20, ge=1, le=100),
):
    query = normalize(q).casefold()
    results = []
    for entry in public_entries():
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
    text: str = Field(min_length=1, max_length=20000)


@app.post("/api/v1/analyze")
def analyze(req: TextRequest):
    phrase_matches = match_phrases(req.text)
    if is_production():
        phrase_matches = [
            match for match in phrase_matches
            if match.get("verification_status") == "verified"
        ]
    return {
        "language": "kha",
        "normalized": normalize(req.text),
        "tokens": tokenize(req.text),
        "reduplications": detect_adjacent_reduplication(req.text),
        "lexicalized_phrase_matches": phrase_matches,
    }


@app.post("/api/v1/normalize")
def normalize_api(req: TextRequest):
    return {"original": req.text, "normalized": normalize(req.text)}


class ResolveRequest(BaseModel):
    source_language: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=5000)
    context: str = Field(default="", max_length=10000)
    require_verified: bool = True


@app.post("/api/v2/resolve-to-khasi")
def resolve_to_khasi(req: ResolveRequest):
    if is_production() and not req.require_verified:
        raise HTTPException(
            status_code=403,
            detail="Production resolution requires verified Khasi data",
        )
    return resolve_equivalent(
        req.source_language,
        req.text,
        req.context,
        True if is_production() else req.require_verified,
    )


@app.get("/api/v2/language-tag/check")
def language_tag_check(tag: str = Query(min_length=1, max_length=64)):
    return {"tag": tag, "accepted_syntax": is_bcp47_like(tag)}


@app.get("/api/v2/capabilities")
def capabilities():
    return {
        "language": "kha",
        "version": "0.4.0",
        "environment": environment(),
        "authoritative_default": is_production(),
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
