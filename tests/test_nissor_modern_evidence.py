import csv
import json

from scripts.enrich_nissor_modern import DEFAULT_SEED, DEFAULT_WIKTIONARY, build_overlay
from scripts.extract_current_corpus_evidence import extract
from scripts.generate_modern_review_queue import build_queue, classify, manifest
from scripts.generate_nissor_sense_candidates import split_gloss
from scripts.structure_nissor_1906_corpus import (
    DEFAULT_APPROVAL,
    DEFAULT_RESOLUTIONS,
    DEFAULT_REVIEW,
    DEFAULT_SUSPICIOUS,
    FIELDS as STRUCTURED_FIELDS,
    build_rows,
)
from scripts.validate_modern_evidence import validate as validate_modern_evidence


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def production_overlay(tmp_path):
    structured_rows = build_rows(DEFAULT_REVIEW, DEFAULT_SUSPICIOUS, DEFAULT_RESOLUTIONS, DEFAULT_APPROVAL)
    structured = tmp_path / "structured.csv"
    write_csv(structured, STRUCTURED_FIELDS, structured_rows)
    return build_overlay(structured, [DEFAULT_SEED], DEFAULT_WIKTIONARY)


def test_current_evidence_seed_is_registered_and_clean():
    assert validate_modern_evidence() == []


def test_production_overlay_covers_all_structured_records_without_auto_verification(tmp_path):
    overlay = production_overlay(tmp_path)
    assert len(overlay) == 3851
    assert all(row["verified"] == "no" for row in overlay)
    assert all(row["requires_human_review"] == "yes" for row in overlay)
    assert any(row["current_use_status"] == "current_attested" for row in overlay)
    assert not any("archaic" in row["diachronic_status_candidate"] for row in overlay)

    balang = [row for row in overlay if row["historical_headword"].casefold() == "balang"]
    assert balang
    assert any(row["modern_canonical_candidate"].casefold() == "balang" for row in balang)
    assert any(row["current_use_status"] == "current_attested" for row in balang)
    assert any(row["diachronic_status_candidate"] == "historical_and_current" for row in balang)


def test_ranked_review_queue_is_complete_deterministic_and_pending(tmp_path):
    overlay = production_overlay(tmp_path)
    queue = build_queue(overlay, batch_size=100)
    assert len(queue) == 3851
    assert len({row["source_record_id"] for row in queue}) == 3851
    assert all(row["review_decision"] == "pending" for row in queue)
    assert all(1 <= int(row["batch_position"]) <= 100 for row in queue)
    assert [int(row["global_rank"]) for row in queue] == list(range(1, 3852))

    tiers = [row["tier"] for row in queue]
    tier_numbers = [int(tier.removeprefix("tier").split("_", 1)[0]) for tier in tiers]
    assert tier_numbers == sorted(tier_numbers)

    data = manifest(queue, 100)
    assert data["records"] == 3851
    assert sum(data["tier_counts"].values()) == 3851
    assert data["decision_values"] == ["approve", "revise", "reject", "defer", "pending"]


def test_review_queue_prioritises_conflict_before_variant_and_history():
    rows = [
        {
            "modern_standard_status": "unassessed",
            "current_use_status": "historical_only_unassessed",
            "pos_evidence_status": "unassessed",
            "variant_status": "unassessed",
        },
        {
            "modern_standard_status": "unassessed",
            "current_use_status": "current_variant_attested_candidate",
            "pos_evidence_status": "unassessed",
            "variant_status": "orthographic_variant_candidate",
        },
        {
            "modern_standard_status": "candidate_pos_review_required",
            "current_use_status": "current_attested",
            "pos_evidence_status": "conflict_requires_review",
            "variant_status": "unassessed",
        },
    ]
    assert classify(rows[0]) == "tier6_historical_only"
    assert classify(rows[1]) == "tier4_variant_candidate"
    assert classify(rows[2]) == "tier3_pos_conflict"


def test_current_corpus_extractor_distinguishes_exact_from_diacritic_variant(tmp_path):
    structured = tmp_path / "structured.csv"
    write_csv(
        structured,
        ["historical_headword"],
        [{"historical_headword": "ïing"}, {"historical_headword": "shnong"}],
    )
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text(
        json.dumps({"text": "ïing shnong iing"}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    rows = extract(corpus, structured, "khasi-ner-2026")
    iing = [row for row in rows if row["headword"] == "ïing"]
    assert {row["match_type"] for row in iing} == {"exact", "diacritic_variant_candidate"}
    assert any(row["current_surface"] == "iing" for row in iing)
    assert any(row["headword"] == "shnong" and row["match_type"] == "exact" for row in rows)


def test_sense_splitter_creates_review_candidates_not_claimed_senses():
    segments = split_gloss("one meaning; another meaning — usage extension", "needs_semantic_split")
    assert [text for text, _ in segments] == ["one meaning", "another meaning", "usage extension"]
    assert segments[0][1] == "initial_segment"
    assert segments[1][1] == "semicolon"
    assert segments[2][1] == "em_dash"


def test_sense_splitter_preserves_unsplit_gloss_when_not_flagged():
    value = "one meaning; punctuation in an example"
    assert split_gloss(value, "single_historical_gloss") == [(value, "no_automatic_split")]
