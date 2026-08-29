from pathlib import Path
import csv
import unicodedata
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from linguistics.tokenizer import tokenize, detect_adjacent_reduplication
from linguistics.phrase_matcher import match_phrases
from api.multilingual import resolve_equivalent, is_bcp47_like

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data/master/khasi_lexicon.csv"

app = FastAPI(
    title="KhasiLex API",
    version="0.3.0",
    description="Professional Khasi lexicon, phrase, reduplication, spell-checking and NLP API",
)


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").strip())


def load_entries():
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@app.get("/health")
def health():
    return {"status": "ok", "service": "KhasiLex", "version": "0.3.0", "language": "kha", "script": "Latn"}


@app.get("/api/v1/words/{word}")
def get_word(word: str):
    target = normalize(word).casefold()
    for entry in load_entries():
        if normalize(entry["headword"]).casefold() == target:
            return entry
    raise HTTPException(status_code=404, detail="Lexical entry not found")


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
        fields = [entry.get(k, "") for k in ("headword", "lemma", "base_form", "definition_kha", "definition_en", "synonyms", "variants")]
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
        "architecture": "sense/concept based multilingual lexicon",
        "accepts": "BCP47-style source language tags",
        "features": ["word lookup", "multiword expressions", "reduplication", "sense disambiguation hooks", "grammar profiles", "pronunciation schema", "multilingual equivalents"],
        "safety_policy": "No translation is guessed when a reviewed mapping is absent.",
    }
