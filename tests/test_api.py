from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["version"] == "0.3.0"


def test_word_lookup():
    r = client.get("/api/v1/words/ïing")
    assert r.status_code == 200
    assert r.json()["headword"] == "ïing"


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
