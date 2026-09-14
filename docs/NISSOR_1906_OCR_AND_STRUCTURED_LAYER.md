# Nissor Singh 1906 — OCR resolution and structured historical layer

## Purpose

The raw 1906 OCR is immutable historical evidence. KhasiLex does not silently rewrite it. A separate resolution layer records corrections made by checking the OCR-suspicious queue against the proofread Wikisource transcription and the public-domain scan of U Nissor Singh's *Khasi-English Dictionary* (1906).

The project owner has approved every genuine headword attested in this dictionary for inclusion in the KhasiLex historical lexicon. This establishes lexical attestation at the `lexical_review` stage. It does not automatically make a 1906 spelling, meaning, borrowing, register or usage a verified modern Standard Khasi form.

## OCR resolution result

All **35** records in `data/historical/nissor-1906/suspicious_queue.csv` now have exactly one resolution in:

`data/historical/nissor-1906/ocr_resolutions.csv`

Resolution types are deliberately explicit:

- `confirmed` — OCR headword was already substantively correct.
- `corrected_ocr` — damaged letters, spacing or diacritics were repaired from the proofread source/scan.
- `article_split` — `u`, `ka`, or another grammatical marker was incorrectly absorbed into the OCR headword.
- `wrong_headword_match` — OCR attached a gloss to the wrong apparent headword; the proofread source identifies the real headword.

Important examples include:

- `'fiiangblen` → `ʼñiangblen`
- `'fiiangbading` → `ʼñiangbading`
- `CTyrsain` → `Tyrsain`
- `VWain` → `Waiñ`
- `XJm-biah` → `Um-biah`
- `XJm-jung` → `Um-jung`
- `Ba'n la` → `Ba'n ia`
- `Boit ha` with the rudder gloss → `Boitha`
- `Kyngkew-u-Basa u` → `Ryngkew-u-Basa` with article `u`
- `Jaid-ior-ior` → `Iáid-ior-ior`
- `Yn sa` is confirmed as a genuine phrase.

The resolution gate is:

```bash
python scripts/validate_nissor_1906_ocr_resolutions.py
```

It fails if any suspicious record is unresolved, duplicated, unknown, not NFC, lacks provenance, or uses an unsupported resolution class.

## Structured historical lexicon

`structure_nissor_1906_corpus.py` builds a **derived, modern-review-ready layer** from the normal review queue plus the 35 resolved OCR records.

Example:

```bash
python scripts/structure_nissor_1906_corpus.py --output build/nissor1906_structured.csv
```

The current best-per-headword/POS corpus contains **3,851 structured historical lexical records**: 3,816 normal review candidates plus 35 scan-confirmed OCR resolutions.

Each structured record contains:

- stable structured ID and source record ID;
- language/script (`kha`, `Latn`);
- Nissor 1906 provenance and page approximation;
- corrected historical headword;
- grammatical article where recovered;
- historical and normalized POS;
- lexical structure (word, hyphenated, multiword);
- stable initial sense ID;
- exact historical English gloss;
- Khasi definition field reserved for newly authored KhasiLex definitions;
- historical-use status (`attested_1906`);
- present-day/current-use status;
- modern-standard status;
- borrowing status;
- variant status and `variant_of` relation;
- semantic-splitting flag;
- editorial stage;
- explicit modern-review requirement.

## Sense policy

The converter does **not** pretend that punctuation in an old dictionary is a reliable modern sense inventory. A record whose historical gloss appears to contain multiple functions/senses is tagged `needs_semantic_split`. Human/linguistic review can then create separate modern KhasiLex senses and concepts.

The historical gloss is retained verbatim as provenance. KhasiLex should write its own Khasi definitions and reviewed English definitions rather than silently treating the 1906 prose as a modern definition.

## Historical form vs modern spelling

Historical display spelling is preserved separately. Diacritics such as the 1906 acute/circumflex marks are **not automatically stripped or converted into a modern canonical spelling**. Likewise, meaningful Khasi letters such as `ï`, `Ï`, and `ñ` must never be destroyed by generic ASCII normalization.

Present-day spelling remains `unassessed` until evidence supports it.

## Current-use labels

Initial structured rows intentionally use:

- `historical_usage_status=attested_1906`
- `current_use_status=unassessed`
- `modern_standard_status=unassessed`
- `borrowing_status=unassessed`
- `variant_status=unassessed`
- `review_stage=lexical_review`
- `requires_modern_review=yes`

Later evidence can move individual senses/forms to labels such as `current`, `historical`, `archaic`, `regional`, `loanword`, or `obsolete`, but those labels require evidence rather than automatic guessing.

## Sources used for OCR confirmation

Primary historical evidence:

- U Nissor Singh, *Khasi-English Dictionary* (Shillong, 1906), public-domain scan hosted by Wikimedia Commons/Internet Archive.
- Proofread Wikisource transcription of the same 1906 dictionary, checked against the scan for the suspicious records.

The proofread transcription is an aid to reading the scan, not a replacement for source provenance.
