from pathlib import Path

from scripts.import_nissor_1906 import extract_candidates

FIXTURE = Path(__file__).parent / "fixtures" / "nissor_1906_sample.txt"


def test_extracts_known_nissor_1906_entries():
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


def test_rejects_obvious_prose_false_positive():
    text = "A normal sentence ends here. I Ab ! int. not a real headword. Bakla, v. to err."
    rows = extract_candidates(text)
    heads = {row.headword_candidate for row in rows}
    assert "i ab" not in heads
    assert "bakla" in heads
