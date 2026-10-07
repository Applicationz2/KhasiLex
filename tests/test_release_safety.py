from scripts.export_word_dic import build_words
from scripts.release_readiness import evaluate


def test_word_export_defaults_to_verified_only():
    words = build_words()
    assert "briew" in words
    assert "ïing" in words
    assert "bam" in words


def test_development_export_can_include_unverified():
    words = build_words(include_unverified=True)
    assert "ïing" in words
    assert "bam" in words


def test_review_pilot_is_ready_but_larger_release_gates_remain_closed():
    review_pilot = evaluate("review-pilot")
    assert review_pilot["ready"] is True
    assert review_pilot["verified_entries"] >= 100
    assert review_pilot["required_verified_entries"] == 100
    assert review_pilot["remaining_verified_entries"] == 0
    assert review_pilot["data_license_status"] == "approved"
    assert review_pilot["data_license_id"] == "CC-BY-SA-4.0"

    technical_alpha = evaluate("technical-alpha")
    assert technical_alpha["ready"] is False
    assert technical_alpha["required_verified_entries"] == 1000
    assert technical_alpha["verified_entries"] < technical_alpha["required_verified_entries"]
    assert technical_alpha["remaining_verified_entries"] > 0
    assert technical_alpha["required_architecture_gate"] == "ai-native-multilingual-g1"
    assert technical_alpha["architecture_ready"] is True

    public_beta = evaluate("public-beta")
    quality_gate = evaluate("extended-beta-quality-gate")
    professional_core = evaluate("professional-core")
    assert public_beta["ready"] is False
    assert quality_gate["ready"] is False
    assert quality_gate["required_verified_entries"] == 10000
    assert professional_core["ready"] is False
