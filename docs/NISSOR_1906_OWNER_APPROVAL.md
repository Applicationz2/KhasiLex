# Nissor Singh 1906 — Source-wide owner approval

On 2026-09-14, the KhasiLex project owner approved **all genuine headwords attested in U Nissor Singh's 1906 Khasi-English Dictionary for inclusion in the KhasiLex historical lexicon**.

## Effective scope

The decision applies to records in:

`data/historical/nissor-1906/review_queue.csv`

Those records receive an effective editorial stage of:

`lexical_review`

The source extraction itself remains immutable historical evidence and therefore continues to store `verification_status=pending`. The effective review decision is represented separately in:

`data/review/nissor1906_source_approval.csv`

This separation preserves provenance and makes the editorial decision auditable without rewriting the historical extraction.

## What the approval means

The approval establishes that the dictionary headword may be retained as a KhasiLex historical lexical entry and that its attestation in Nissor Singh 1906 is accepted as valid lexical evidence.

It does **not**, by itself, assert that every 1906 spelling, definition, grammatical label, borrowing analysis, register label, or usage note is the preferred form in present-day Standard Khasi.

Historical, archaic, dialectal, borrowed, obsolete and specialist entries should be retained with appropriate labels rather than deleted merely because they are uncommon today.

## OCR exclusion

Records in:

`data/historical/nissor-1906/suspicious_queue.csv`

are not covered by the source-wide approval until the printed source image confirms the headword. These rows can contain OCR substitutions, shifted articles, broken characters, or other recognition errors. Once a suspicious row is confirmed against the scan as a genuine dictionary headword, it inherits the same inclusion approval.

## Verification remains a higher gate

This decision does not automatically create `verified` modern dictionary entries. Final verification can still require modern spelling review, grammar review, sense separation, translation review, register/dialect labeling, and technical validation according to KhasiLex governance.

Run:

```bash
python scripts/evaluate_nissor1906_source_approval.py
```

to validate the decision against the current historical review and suspicious queues and regenerate the approval report.
