from pathlib import Path

from scripts.import_nissor_1906 import extract_candidates, lexical_initial

FIXTURE = Path(__file__).parent / "fixtures" / "nissor_1906_sample.txt"


def test_extracts_known_line_start_entries():
    rows = extract_candidates(FIXTURE.read_text(encoding="utf-8"))
    found = {(row.headword_candidate, row.part_of_speech) for row in rows}

    expected = {
        ("bakla", "verb"),
        ("bad", "conjunction"),
        ("bang", "adjective"),
        ("bahkhala", "verb"),
        ("'baibam", "noun"),
        ("'baibat", "noun"),
        ("'baikhrong", "noun"),
        ("'bainong", "noun"),
        ("'bai-seng", "noun"),
        ("balei", "adverb"),
        ("bam", "verb"),
        ("bambriew", "adjective"),
        ("bam-khuti", "verb"),
        ("bamram", "verb"),
        ("bamsap", "verb"),
        ("ban", "verb"),
        ("banse", "verb"),
    }

    assert expected <= found
    assert all(row.verification_status == "pending" for row in rows)
    assert all(row.human_review_required == "yes" for row in rows)
    assert all(row.source_id == "nissor-1906-kha-en" for row in rows)


def test_inline_definition_text_is_not_promoted_to_headword():
    text = (
        "KHASI-ENGLISH DICTIONARY. A\n"
        "Baisiew, ka, n. money. [Imit. 'baisiew-'bai-tda.] Bait, v. to sharpen.\n"
        "Bakla, v. to err.\n"
    )
    rows = extract_candidates(text)
    heads = {row.headword_candidate for row in rows}
    assert "'baisiew-'bai-tda" not in heads
    assert "bait" not in heads
    assert "baisiew" in heads
    assert "bakla" in heads


def test_apostrophe_does_not_hide_non_khasi_initial():
    assert lexical_initial("'fiiang") == "f"
    text = "KHASI-ENGLISH DICTIONARY. A\n'Fiiangbading, ka, n. an OCR-suspect form.\n"
    rows = extract_candidates(text)
    assert len(rows) == 1
    assert float(rows[0].ocr_confidence) < 0.75


def test_short_trailing_token_is_downgraded():
    text = "KHASI-ENGLISH DICTIONARY. A\n'Bat-iambait ii, ka, n. suspicious shifted article.\n"
    rows = extract_candidates(text)
    assert len(rows) == 1
    assert float(rows[0].ocr_confidence) < 0.75
