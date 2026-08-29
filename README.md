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

KhasiLex now systematically processes the complete public-domain **U Nissor Singh, Khasi-English Dictionary (1906)** from the canonical Internet Archive OCR snapshot.

Current reproducible extraction:

- **3,853** structurally recognized historical records
- **3,848** unique normalized headwords
- **3,851** unique headword / part-of-speech pairs
- **3,816** normal editorial-review candidates
- **35** suspicious/OCR-anomaly candidates quarantined for scan inspection
- **39** deterministic review batches of up to 100 candidates

All historical records remain `pending` and require modern Khasi human review. Historical spelling, definitions, POS labels and senses are evidence, not automatic modern lexical authority.

Corpus files:

- `data/sources/nissor-1906/khasienglishdict00singrich_djvu.txt` — preserved raw OCR snapshot
- `data/historical/nissor-1906/entries.csv` — complete structurally recognized historical extraction
- `data/historical/nissor-1906/review_queue.csv` — normal editorial queue
- `data/historical/nissor-1906/suspicious_queue.csv` — OCR/anomaly quarantine
- `data/historical/nissor-1906/review_plan.csv` — deterministic full-corpus batch plan
- `quality/nissor1906_ingest_report.json` — source hash, counts and parser diagnostics

See `docs/NISSOR_1906_FULL_INGEST.md` for the ingestion and review policy.

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

These entries are intentionally still `pending`. Source attestation and part-of-speech evidence are recorded, but canonical spelling, Khasi definitions, sense separation, example sentences, dialect/register and final grammatical decisions still require human linguistic review.

Run the batch quality gate with:

```bash
python scripts/audit_review_batch.py
```

See `docs/v0.4-first-100-review-corpus.md` for the review protocol and identified ambiguity/spelling cases.

## Core capabilities

- Microsoft Word custom dictionary export
- Hunspell dictionary export foundation
- UTF-8 / Unicode NFC-safe Khasi text handling
- Khasi `ï` / `Ï` preservation
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
- layout-aware OCR extraction and anomaly quarantine
- deterministic 100-entry historical review planning
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
3. Stage candidates as `pending`.
4. Review spelling, sense, grammar, provenance and licence.
5. Move approved material through `pending` → `reviewed` → `verified`.
6. Record review actions in `data/review/review_log.csv`.
7. Run the validation and corpus audit gates.

For ordinary candidate imports:

```bash
python scripts/stage_candidates.py path/to/candidates.csv
python scripts/validate.py
python scripts/corpus_audit.py
```

For the 1906 historical corpus, use the generated `review_plan.csv` and inspect the original scan whenever OCR or historical usage is uncertain.

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

The starter examples remain `pending`: their meanings and grammatical functions must be linguistically reviewed rather than guessed. Historical `[Imit.]` strings from the 1906 dictionary are not automatically promoted as headwords merely because they contain repeated or paired forms.

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
- `governance/EDITORIAL_WORKFLOW.md`
- `governance/REVIEWER_ROLES.md`
- `ROADMAP.md`

No AI-generated, copied, OCR-damaged, historical-only or linguistically uncertain material may be marked authoritative merely to increase coverage.

## Licensing and provenance

Do not copy copyrighted Khasi dictionaries or corpora unless their licence permits the intended reuse and redistribution. Production entries must retain source and licence information.

The Nissor Singh 1906 corpus is maintained as a public-domain historical evidence layer with the exact source snapshot and SHA-256 recorded for reproducibility.

## Current status

**v0.4 is under active corpus review.** The full Nissor Singh 1906 historical source has been systematically ingested and partitioned for review, alongside the original 100-entry source-attested pilot. The technical platform is deployable; the authoritative public dictionary grows only as competent Khasi reviewers move entries through `pending` → `reviewed` → `verified`.