from scripts.structure_nissor_1906_corpus import (
    DEFAULT_APPROVAL,
    DEFAULT_RESOLUTIONS,
    DEFAULT_REVIEW,
    DEFAULT_SUSPICIOUS,
    build_rows,
)
from scripts.validate_nissor_1906_ocr_resolutions import validate


def test_all_35_ocr_suspects_are_resolved():
    report = validate()
    assert report["suspicious_records"] == 35
    assert report["resolved_records"] == 35
    assert report["unresolved_records"] == 0
    assert report["all_suspicious_records_resolved"] is True
    assert report["errors"] == []


def test_structured_layer_covers_every_best_headword_pos_candidate():
    rows = build_rows(DEFAULT_REVIEW, DEFAULT_SUSPICIOUS, DEFAULT_RESOLUTIONS, DEFAULT_APPROVAL)
    assert len(rows) == 3851
    assert len({row["source_record_id"] for row in rows}) == 3851
    assert all(row["review_stage"] == "lexical_review" for row in rows)
    assert all(row["requires_modern_review"] == "yes" for row in rows)
    assert all(row["current_use_status"] == "unassessed" for row in rows)
    assert all(row["modern_standard_status"] == "unassessed" for row in rows)


def test_known_ocr_damage_is_replaced_by_proofread_historical_forms():
    rows = build_rows(DEFAULT_REVIEW, DEFAULT_SUSPICIOUS, DEFAULT_RESOLUTIONS, DEFAULT_APPROVAL)
    heads = {row["historical_headword"] for row in rows}
    assert "Waiñ" in heads
    assert "Yn sa" in heads
    assert "Boitha" in heads
    assert "Ba'n ia" in heads
    assert "Tyrsain" in heads
    assert "ʼñiangblen" in heads
    assert "ʼñiangbading" in heads

    damaged = {"VWain", "Boit ha", "Ba'n la", "CTyrsain", "'fiiangblen", "'fiiangbading"}
    assert heads.isdisjoint(damaged)


def test_structured_layer_preserves_history_without_claiming_modern_verification():
    rows = build_rows(DEFAULT_REVIEW, DEFAULT_SUSPICIOUS, DEFAULT_RESOLUTIONS, DEFAULT_APPROVAL)
    wai = next(row for row in rows if row["historical_headword"] == "Waiñ")
    assert wai["historical_article"] == "ka"
    assert wai["historical_usage_status"] == "attested_1906"
    assert wai["definition_kha"] == ""
    assert wai["modern_standard_status"] == "unassessed"
