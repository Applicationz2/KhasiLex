from scripts.export_word_dic import build_words
from scripts.release_readiness import evaluate


def test_word_export_defaults_to_verified_only():
    words = build_words()
    assert "briew" in words
    assert "ïing" not in words
    assert "biang" not in words


def test_development_export_can_include_unverified():
    words = build_words(include_unverified=True)
    assert "ïing" in words


def test_current_repository_is_not_prematurely_release_ready():
    report = evaluate("review-pilot")
    assert report["ready"] is False
    assert report["verified_entries"] >= 10
    assert report["verified_entries"] < report["required_verified_entries"]
    assert report["required_verified_entries"] == 100
    assert report["data_license_status"] == "approved"
    assert report["data_license_id"] == "CC-BY-SA-4.0"
