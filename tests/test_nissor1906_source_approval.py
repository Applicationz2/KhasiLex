from scripts.evaluate_nissor1906_source_approval import evaluate


def test_source_wide_owner_approval_resolves_review_queue_only():
    report = evaluate()

    assert report["source_id"] == "nissor-1906-kha-en"
    assert report["decision"] == "approve_inclusion"
    assert report["effective_stage"] == "lexical_review"
    assert report["approved_review_queue_records"] == 3816
    assert report["suspicious_ocr_records_pending"] == 35
    assert report["verified_records_created_by_this_decision"] == 0
