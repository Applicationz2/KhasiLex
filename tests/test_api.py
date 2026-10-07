import os

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["version"] == "0.4.0"


def test_ready():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"
    assert r.json()["entries_loaded"] >= 12


def test_word_lookup():
    r = client.get("/api/v1/words/ïing")
    assert r.status_code == 200
    assert r.json()["headword"] == "ïing"


def test_authoritative_lookup_rejects_pending_seed():
    r = client.get("/api/v1/authoritative/words/bam")
    assert r.status_code == 404


def test_corpus_stats_expose_review_target():
    r = client.get("/api/v1/corpus/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["version"] == "0.4.0"
    assert data["total_entries"] >= 12
    assert data["verification"]["verified"] >= 100
    assert data["verification"]["pending"] >= 1
    assert sum(data["verification"].values()) == data["total_entries"]
    assert data["next_target"]["name"] == "technical-alpha"
    assert data["next_target"]["required"] == 1000


def test_public_corpus_defaults_to_verified_only():
    r = client.get("/api/v1/corpus/entries")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "verified"
    assert data["count"] >= 10
    assert all(row["verification_status"] == "verified" for row in data["results"])
    headwords = {row["headword"] for row in data["results"]}
    assert "briew" in headwords
    assert "ïing" in headwords
    assert "bam" not in headwords


def test_corpus_filter_rejects_invalid_status():
    r = client.get("/api/v1/corpus/entries", params={"status": "automatic"})
    assert r.status_code == 400


def test_normalize():
    r = client.post("/api/v1/normalize", json={"text": " ïing "})
    assert r.status_code == 200
    assert r.json()["normalized"] == "ïing"


def test_reduplication_detection():
    r = client.post("/api/v1/analyze", json={"text": "kloi kloi"})
    assert r.status_code == 200
    data = r.json()
    assert len(data["reduplications"]) == 1
    assert data["reduplications"][0]["repeat_count"] == 2


def test_threefold_repetition():
    r = client.post("/api/v1/analyze", json={"text": "wut wut wut"})
    assert r.status_code == 200
    red = r.json()["reduplications"][0]
    assert red["repeat_count"] == 3
    assert red["pattern"] == "X X X"


def test_bcp47_language_tag():
    r = client.get("/api/v2/language-tag/check", params={"tag": "zh-Hant"})
    assert r.status_code == 200
    assert r.json()["accepted_syntax"] is True


def test_resolver_refuses_unverified_by_default():
    r = client.post("/api/v2/resolve-to-khasi", json={
        "source_language": "en",
        "text": "water",
        "context": "",
        "require_verified": True,
    })
    assert r.status_code == 200
    assert r.json()["status"] == "not_found"


def test_resolver_can_surface_candidate_in_dev_mode():
    r = client.post("/api/v2/resolve-to-khasi", json={
        "source_language": "en",
        "text": "water",
        "context": "",
        "require_verified": False,
    })
    assert r.status_code == 200
    assert r.json()["status"] in {"resolved", "concept_found_no_verified_khasi"}


def test_production_word_lookup_cannot_leak_pending(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.get("/api/v1/words/bam")
    assert r.status_code == 404
    assert r.json()["detail"] == "No verified lexical entry found"


def test_production_search_cannot_leak_pending(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.get("/api/v1/search", params={"q": "wut wut"})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_production_corpus_rejects_nonverified_status(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.get("/api/v1/corpus/entries", params={"status": "pending"})
    assert r.status_code == 403


def test_production_reduplication_catalog_hides_pending(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.get("/api/v1/reduplications")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_production_analysis_keeps_structural_reduplication_but_hides_pending_phrase(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.post("/api/v1/analyze", json={"text": "kloi kloi"})
    assert r.status_code == 200
    assert len(r.json()["reduplications"]) == 1
    assert r.json()["lexicalized_phrase_matches"] == []


def test_production_resolver_rejects_unverified_override(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.post("/api/v2/resolve-to-khasi", json={
        "source_language": "en",
        "text": "water",
        "require_verified": False,
    })
    assert r.status_code == 403


def test_security_headers_and_request_id(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "no-referrer"
    assert r.headers["x-request-id"]


def test_production_rejects_oversized_declared_body(monkeypatch):
    monkeypatch.setenv("KHASILEX_ENV", "production")
    r = client.post(
        "/api/v1/normalize",
        headers={"content-length": "70000"},
        content=b'{"text":"x"}',
    )
    assert r.status_code == 413


def test_homograph_lookup_can_select_part_of_speech():
    noun = client.get(
        "/api/v1/authoritative/words/phira",
        params={"part_of_speech": "noun"},
    )
    verb = client.get(
        "/api/v1/authoritative/words/phira",
        params={"part_of_speech": "verb"},
    )
    assert noun.status_code == 200
    assert noun.json()["headword"] == "phira"
    assert noun.json()["part_of_speech"] == "noun"
    assert verb.status_code == 200
    assert verb.json()["headword"] == "phira"
    assert verb.json()["part_of_speech"] == "verb"
    assert noun.json()["id"] != verb.json()["id"]


def test_homograph_lookup_rejects_unknown_part_of_speech():
    r = client.get(
        "/api/v1/authoritative/words/phira",
        params={"part_of_speech": "adjective"},
    )
    assert r.status_code == 404
