# Nissor 1906 Modern Evidence Pass

## Purpose

This pass converts the approved historical Nissor Singh 1906 lexicon into a progressively modernised review layer without pretending that corpus frequency, historical glosses, AI output or one external dictionary can establish authoritative modern Khasi by themselves.

The immutable historical evidence remains separate from all modern decisions.

## Inputs

1. The 3,851 structured Nissor 1906 best headword/POS records produced by `scripts/structure_nissor_1906_corpus.py`.
2. Contemporary occurrence evidence from approved current Khasi sources.
3. The v0.4 English Wiktionary Khasi review batch as modern lexicographic/POS evidence.
4. Optional full-corpus evidence extracted from the 2026 Khasi NER corpus with `scripts/extract_current_corpus_evidence.py`.

## Current evidence tiers

### Tier A — current + modern lexicographic agreement

An exact historical headword is attested in a current Khasi source and the same form is independently present in the modern lexicographic batch. If the historical POS also matches the modern lexicographic POS, the record becomes a `strong_candidate`.

This is still not `verified`.

### Tier B — current exact attestation

The exact historical form occurs in current Khasi material but modern lexicographic support is absent or not yet imported. The entry receives `current_use_status=current_attested` and `modern_standard_status=candidate_current_attested`.

### Tier C — modern lexicographic evidence only

The historical form appears in the contemporary lexicographic source but has no current-corpus occurrence evidence yet. The entry becomes a `lexicographic_candidate`; current use remains unassessed.

### Tier D — diacritic/orthographic variant candidate

The current corpus contains a form matching only after the evidence-only `ï -> i` / `ñ -> n` fold. KhasiLex records it as an orthographic variant candidate. It does not silently replace the historical or canonical spelling.

### Tier E — historical only

No current evidence has yet been attached. The record remains historically attested and modern status remains unassessed. Absence of current evidence is never treated as proof that a form is archaic.

## Current source seed

`data/modern_evidence/current_attestations_seed.csv` starts the evidence layer using:

- the 2026 Khasi Named Entity Recognition Corpus public dataset examples;
- current Meghalaya Government Khasi publications registered in `data/sources/source_registry.csv`.

Government publications are used only to establish current lexical occurrence/spelling evidence. Their prose is not bulk copied and they are not treated as reusable definition sources.

## Full 2026 corpus ingestion

The published Khasi NER corpus contains about 3.08 million tokens in 13,431 documents. After obtaining `train.jsonl` and `dev.jsonl`, first generate the structured Nissor layer:

```bash
python scripts/structure_nissor_1906_corpus.py --output build/nissor1906_structured.csv
```

Then extract exact and orthographic-variant evidence:

```bash
python scripts/extract_current_corpus_evidence.py data/train.jsonl \
  --structured build/nissor1906_structured.csv \
  --source-id khasi-ner-2026 \
  --output build/khasi_ner_train_evidence.csv

python scripts/extract_current_corpus_evidence.py data/dev.jsonl \
  --structured build/nissor1906_structured.csv \
  --source-id khasi-ner-2026 \
  --output build/khasi_ner_dev_evidence.csv
```

Build the overlay with both evidence files:

```bash
python scripts/enrich_nissor_modern.py \
  --structured build/nissor1906_structured.csv \
  --current-evidence build/khasi_ner_train_evidence.csv \
  --current-evidence build/khasi_ner_dev_evidence.csv \
  --output build/nissor1906_modern_evidence.csv \
  --report build/nissor1906_modern_evidence_report.json
```

## POS handling

Historical POS is never silently overwritten.

- matching historical + modern lexicographic POS: `matched_historical_and_modern_lexicographic`;
- one conflicting modern POS: `conflict_requires_review`;
- multiple modern POS labels: `ambiguous_multiple_modern_pos`;
- no modern grammatical evidence: `unassessed`.

This is important for cases where one spelling represents multiple historical or modern senses.

## Sense separation

`scripts/generate_nissor_sense_candidates.py` turns punctuation-signalled historical gloss segments into **review-only sense candidates**. A semicolon or em dash can indicate a separate meaning, a POS change, an example or a usage note, so generated segments are never treated as approved senses automatically.

```bash
python scripts/generate_nissor_sense_candidates.py \
  --structured build/nissor1906_structured.csv \
  --output build/nissor1906_sense_candidates.csv
```

Every generated row is `unreviewed_draft` and requires human semantic review.

## Variants

Khasi digital text sometimes omits `ï` and `ñ`. The current corpus extractor therefore has an evidence-only diacritic fold. A folded match creates a variant candidate; it never normalises one form into another automatically.

Later passes can add additional safely defined variant relations, but only with explicit provenance and review.

## Borrowing status

The 1906 extraction preserves the source's historical foreign/loan markers. The modern overlay exposes these as `historical_source_marked_loan_or_foreign` evidence signals. This is not a final etymological decision: current naturalisation, source language and borrowing history still require review before assigning a modern `loanword`, `naturalised`, `native`, or related label.

## Evidence-ranked review queue

`scripts/generate_modern_review_queue.py` converts the overlay into deterministic review batches of up to 100 records. Each of the 3,851 source records appears exactly once and starts with `review_decision=pending`.

Review order is:

1. `tier1_strong_candidate` — current exact evidence plus agreeing modern lexicographic/POS evidence;
2. `tier2_current_attested` — current exact evidence without full independent POS agreement;
3. `tier3_pos_conflict` — modern and historical grammatical evidence conflicts or is multi-POS;
4. `tier4_variant_candidate` — current orthographic/diacritic variant evidence;
5. `tier5_lexicographic_only` — modern lexicographic evidence but no attached current-corpus evidence;
6. `tier6_historical_only` — historical attestation with present-day status still unassessed.

Within each tier, records with more independent current sources and higher corpus frequency are reviewed first. Easier single-gloss records sort ahead of records already flagged for semantic splitting.

```bash
python scripts/generate_modern_review_queue.py \
  --overlay build/nissor1906_modern_evidence.csv \
  --output build/nissor1906_modern_review_queue.csv \
  --manifest build/nissor1906_modern_review_manifest.json \
  --batch-size 100
```

The review columns allow `approve`, `revise`, `reject`, `defer`, or `pending`. Generating the queue itself makes no editorial decision.

## Verification boundary

The automated pass may assign evidence and review priorities. It may not assign final `verified` status.

All generated overlay rows contain:

- `review_stage=modern_evidence_review`;
- `requires_human_review=yes`;
- `verified=no`.

This is an invariant enforced by tests and build logic.

## Build integration

`python scripts/build_all.py` now generates, under the ignored `build/` directory:

- `nissor1906_structured.csv`;
- `nissor1906_modern_evidence.csv`;
- `nissor1906_modern_evidence_report.json`;
- `nissor1906_sense_candidates.csv`;
- `nissor1906_modern_review_queue.csv`;
- `nissor1906_modern_review_manifest.json`.

The manual `KhasiLex Modern Evidence Pass` GitHub workflow additionally processes the full Khasi NER train/dev corpus and uploads the corpus evidence, ranked queue and manifests as temporary artifacts. It does not commit or verify the generated data automatically.

The committed source and review files remain the auditable inputs; generated overlays and queues are reproducible derivatives.
