# Nissor Singh 1906 Full-Dictionary Ingestion

KhasiLex v0.4 uses U Nissor Singh's **Khasi-English Dictionary (1906)** as a historical lexical evidence source.

Canonical digital source:

- Internet Archive item: `khasienglishdict00singrich`
- OCR text: `https://archive.org/download/khasienglishdict00singrich/khasienglishdict00singrich_djvu.txt`
- Scan/PDF: Wikimedia Commons / Internet Archive
- Publication: Shillong, Eastern Bengal and Assam Secretariat Press, 1906
- Khasi variety: the author's preface identifies the Cherra/Cherrapunji dialect as the principal standard used by the dictionary
- Rights status used by KhasiLex: public-domain historical work

## Why the full book is not copied directly into the authoritative lexicon

A 1906 dictionary is valuable evidence, but it is not automatically a modern normative dictionary.

The source contains:

- historical spellings;
- historical grammatical labels;
- loanword markers;
- obsolete or changed senses;
- OCR errors from the digitized scan;
- multi-sense entries that need sense separation;
- phrases, compounds and imitative/reduplicative constructions;
- forms whose modern Khasi status must be checked.

Therefore the complete extraction is stored in a **historical candidate layer** and every record remains `pending`.

## Reproducible ingestion workflow

The GitHub Actions workflow `.github/workflows/ingest-nissor-1906.yml`:

1. downloads the canonical Internet Archive OCR text;
2. checks that the source is plausibly complete;
3. stores the raw OCR snapshot in the repository;
4. runs `scripts/import_nissor_1906.py`;
5. creates `data/historical/nissor-1906/entries.csv`;
6. creates a de-duplicated headword/POS `review_queue.csv`;
7. writes `quality/nissor1906_ingest_report.json`, including the source SHA-256;
8. validates the generated corpus;
9. runs the normal KhasiLex build and tests;
10. runs a Docker regression build;
11. commits the reproducible generated snapshot back to the feature branch.

## Generated historical entry fields

The historical corpus preserves:

- raw OCR headword;
- normalized candidate form;
- entry type;
- normalized and raw part-of-speech evidence;
- source gender/article label where detectable;
- historical foreign/loan marker where detectable;
- historical English gloss text;
- source line and approximate scanned page;
- OCR-confidence score;
- duplicate headword/POS count;
- whether the headword already exists in the master lexicon;
- review priority;
- mandatory human-review flag;
- `pending` verification status.

## Confidence is not linguistic authority

`ocr_confidence` measures how structurally plausible the OCR extraction is. It does **not** mean that a spelling, definition, grammar analysis, dialect classification or current usage has been verified.

High-confidence records are simply better candidates to review first.

## Review process

The recommended sequence is:

`historical extraction -> OCR/source-image check -> modern spelling check -> POS/grammar review -> sense split -> Khasi definition -> English gloss review -> example review -> provenance confirmation -> reviewed -> verified`

Only the final reviewed records should be promoted into `data/master/khasi_lexicon.csv`.

## Historical spelling policy

Do not silently erase historical variants. When the 1906 form differs from the modern accepted form:

- preserve the 1906 form as historical evidence;
- add the modern canonical headword separately during human review;
- link historical and modern forms as variants where appropriate;
- record dialect/register/obsolete status when known.

## Reduplication, imitative forms and compounds

The source explicitly includes imitative word-collocations and many compounds. KhasiLex preserves these as candidates rather than treating repeated words or hyphenated forms as spelling mistakes.

## Supply-chain reproducibility

The first successful full ingest records the SHA-256 of the raw Internet Archive OCR snapshot. Future refreshes should compare against the recorded hash so changes in the external OCR source are visible and reviewable.
