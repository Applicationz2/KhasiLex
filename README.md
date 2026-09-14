# KhasiLex v0.4 — Authoritative Khasi Corpus Foundation

KhasiLex is an open, AI-ready Khasi lexical platform for professional dictionary development, grammar, reduplication, spell-checking, multilingual translation, NLP and AI integration.

Language code: `kha`

## v0.4 objective

v0.4 moves KhasiLex from a technical prototype toward an **authoritative, human-reviewed Khasi lexical corpus**. The software remains deployable, but only entries marked `verified` after the editorial quality gates should be presented as authoritative dictionary content.

The first corpus targets are:

- **100 verified entries** — review-pilot milestone
- **1,000 verified entries** — technical alpha corpus
- **5,000 verified entries** — public-beta corpus
- **25,000 verified entries** — professional core target

Accuracy and provenance take priority over raw word count.

## Nissor Singh 1906 full historical corpus

KhasiLex systematically processes the complete public-domain **U Nissor Singh, Khasi-English Dictionary (1906)** from the canonical Internet Archive/Wikimedia source.

Current reproducible extraction and resolution:

- **3,853** structurally recognized historical records
- **3,848** unique normalized headwords
- **3,851** unique headword / part-of-speech pairs
- **3,816** normal editorial-review candidates
- **35/35** OCR/anomaly candidates explicitly resolved against the proofread transcription and source scan
- **3,851** structured best headword/POS records for modern review
- **39** deterministic review batches retained for traceability

The project owner has approved every genuine Nissor 1906 headword for **historical lexical inclusion**. That source-wide decision establishes `lexical_review` status for genuine headwords; it does **not** automatically certify historical spelling, meaning, register, borrowing status or present-day usage as verified modern Standard Khasi.

Corpus files:

- `data/sources/nissor-1906/khasienglishdict00singrich_djvu.txt` — preserved raw OCR snapshot
- `data/historical/nissor-1906/entries.csv` — complete structurally recognized historical extraction
- `data/historical/nissor-1906/review_queue.csv` — normal editorial queue
- `data/historical/nissor-1906/suspicious_queue.csv` — original OCR/anomaly quarantine
- `data/historical/nissor-1906/ocr_resolutions.csv` — explicit resolutions for all 35 suspicious records
- `data/historical/nissor-1906/review_plan.csv` — deterministic full-corpus batch plan
- `data/review/nissor1906_source_approval.csv` — source-wide owner inclusion decision
- `quality/nissor1906_ingest_report.json` — source hash, counts and parser diagnostics

See `docs/NISSOR_1906_FULL_INGEST.md` and `docs/NISSOR_1906_OCR_AND_STRUCTURED_LAYER.md`.

## Automated modern-evidence pass

KhasiLex now evaluates the 3,851 structured historical records against contemporary Khasi evidence instead of manually reviewing ten words at a time.

The evidence pass can use:

- the **Khasi Named Entity Recognition Corpus 1.0.0 (2026)** for exact usage, frequency and orthographic-variant evidence;
- current registered Meghalaya Government Khasi publications for occurrence/spelling evidence;
- the existing English Wiktionary Khasi review batch for modern headword/POS comparison.

The automation can assign evidence-ranked states such as:

- `strong_candidate` — current exact attestation plus agreeing modern lexicographic/POS evidence;
- `candidate_current_attested` — exact current usage evidence;
- `lexicographic_candidate` — modern lexicographic evidence but current use still unassessed;
- `orthographic_variant_candidate` — e.g. an evidence-only `ï/i` or `ñ/n` relationship requiring review;
- `historical_only_unassessed` — no modern evidence yet attached.

It never changes a row to final `verified` automatically.

`python scripts/build_all.py` generates these reproducible derivatives under `build/`:

- `nissor1906_structured.csv`
- `nissor1906_modern_evidence.csv`
- `nissor1906_modern_evidence_report.json`
- `nissor1906_sense_candidates.csv`

For a full contemporary-corpus pass, use `scripts/extract_current_corpus_evidence.py` on the Khasi NER JSONL files and feed the generated evidence into `scripts/enrich_nissor_modern.py`.

See `docs/NISSOR_1906_MODERN_EVIDENCE_PASS.md`.

## First real 100-entry review corpus

The first source-attested contemporary review batch remains available at:

`data/review/batches/v0.4-pilot-001.csv`

It contains exactly **100 real Khasi lexical candidates** balanced across:

- 50 nouns
- 25 verbs
- 13 adjectives
- 4 adverbs
- 8 pronouns

A separate worksheet for competent Khasi human review is available at:

`data/review/batches/v0.4-pilot-001-human-review.csv`

Source attestation and part-of-speech evidence are recorded, but canonical spelling, Khasi definitions, sense separation, example sentences, dialect/register and final grammatical decisions still require competent linguistic review before `verified` status.

Run the batch quality gate with:

```bash
python scripts/audit_review_batch.py
```

See `docs/v0.4-first-100-review-corpus.md`.

## Core capabilities

- Microsoft Word custom dictionary export
- Hunspell dictionary export foundation
- UTF-8 / Unicode NFC-safe Khasi text handling
- Khasi `ï` / `Ï` and `ñ` preservation
- FastAPI lexical API
- authoritative verified-only API endpoints
- corpus quality metrics and readiness targets
- word, phrase, compound, idiom and reduplication entry types
- full adjacent reduplication detection (`X X`, `X X X`, ...)
- multiword lexical matching
- sense/concept multilingual architecture
- BCP-47-style source-language identifiers
- safe candidate-staging workflow
- provenance, licensing and human review gates
- complete public-domain historical-dictionary ingestion pipeline
- layout-aware OCR extraction and complete anomaly-resolution ledger
- structured 3,851-record historical-to-modern review layer
- contemporary-corpus frequency and exact-form evidence extraction
- conservative diacritic/orthographic variant detection
- modern headword/POS evidence ranking
- review-only historical sense candidate generation
- Docker deployment
- automated CI across Python 3.11, 3.12 and 3.13

## Quick start

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts\build_all.py
pytest -q
uvicorn api.main:app --reload
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/build_all.py
pytest -q
uvicorn api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Corpus workflow

Candidate data must not be written directly into the authoritative master lexicon without review.

1. Collect candidate evidence from an approved source.
2. Preserve source, licence and provenance metadata.
3. Stage candidates or evidence separately from authoritative master data.
4. Review spelling, senses, grammar, variants, current/historical status, provenance and licence.
5. Move approved material through the editorial gates toward `verified`.
6. Record review actions in `data/review/review_log.csv`.
7. Run validation, evidence and corpus audit gates.

For ordinary candidate imports:

```bash
python scripts/stage_candidates.py path/to/candidates.csv
python scripts/validate.py
python scripts/corpus_audit.py
```

For the historical-modern pipeline:

```bash
python scripts/build_all.py
```

For a full contemporary JSONL corpus:

```bash
python scripts/extract_current_corpus_evidence.py path/to/train.jsonl \
  --structured build/nissor1906_structured.csv \
  --source-id khasi-ner-2026 \
  --output build/current_evidence.csv
```

## Authoritative API

Development lookup may include pending entries:

`GET /api/v1/words/{word}`

Production-safe verified-only lookup:

`GET /api/v1/authoritative/words/{word}`

Corpus statistics:

`GET /api/v1/corpus/stats`

Filtered corpus entries (defaults to verified):

`GET /api/v1/corpus/entries`

Global-language sense resolution:

`POST /api/v2/resolve-to-khasi`

## Reduplication

KhasiLex treats repeated Khasi constructions as possible lexical or grammatical units rather than automatically as typing errors. Examples currently used for structural testing include `biang biang`, `wut wut`, and `kloi kloi`.

The starter examples remain review material until their meanings and grammatical functions are linguistically approved. Historical `[Imit.]` strings from the 1906 dictionary are not automatically promoted as headwords merely because they contain repeated or paired forms.

## Microsoft Word

Generate the Word custom dictionary with:

```bash
python scripts/export_word_dic.py
```

Then in Word use **File → Options → Proofing → Custom Dictionaries → Add** and select `dictionaries/microsoft-word/Khasi.dic`.

The Word `.dic` is a spell-check word list. Rich definitions, grammar, sense data and multilingual information remain in KhasiLex.

## Docker

```bash
docker compose up --build
```

The API is exposed on port `8000`.

## Editorial policy

See:

- `docs/v0.4-editorial-policy.md`
- `docs/v0.4-first-100-review-corpus.md`
- `docs/NISSOR_1906_FULL_INGEST.md`
- `docs/NISSOR_1906_OCR_AND_STRUCTURED_LAYER.md`
- `docs/NISSOR_1906_MODERN_EVIDENCE_PASS.md`
- `governance/EDITORIAL_WORKFLOW.md`
- `governance/REVIEWER_ROLES.md`
- `ROADMAP.md`

No AI-generated, copied, OCR-damaged, historical-only or linguistically uncertain material may be marked authoritative merely to increase coverage.

## Licensing and provenance

Do not copy copyrighted Khasi dictionaries or corpora unless their licence permits the intended reuse and redistribution. Production entries must retain source and licence information.

The Nissor Singh 1906 corpus is maintained as a public-domain historical evidence layer with the exact source snapshot and SHA-256 recorded for reproducibility. The Khasi NER corpus is CC BY-SA 4.0; derived evidence must preserve its attribution and ShareAlike obligations where applicable. Current Meghalaya Government publications are used only as occurrence/spelling references unless a separate reuse licence is established.

See `THIRD_PARTY_DATA.md`.

## Current status

**v0.4 is under active corpus modernisation and review.** The full Nissor Singh 1906 historical source has been ingested, all 35 quarantined OCR records have explicit resolutions, and 3,851 structured best headword/POS records are ready for evidence-ranked modern review. The technical platform can now process contemporary corpus evidence at scale; final authoritative dictionary growth still requires competent Khasi editorial verification.
