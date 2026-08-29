# KhasiLex v0.3 Global Professional Lexical Platform

KhasiLex is an open, AI-ready Khasi lexical platform designed to support:

- Microsoft Word custom dictionaries
- Hunspell spell checking
- Khasi-English lexical lookup
- Unicode-safe normalization
- CSV / JSONL master lexicon management
- SQLite storage
- FastAPI REST API integration
- Future NLP, RAG, embeddings, translation, morphology, and AI-platform integration

Language code: `kha`

## Project architecture

The master lexicon is the authoritative source. Microsoft Word, Hunspell,
JSONL, SQLite, and API resources are generated from the master lexicon.

## Quick start

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Validate the master lexicon

```bash
python scripts/validate.py
```

### 3. Generate exports

```bash
python scripts/export_word_dic.py
python scripts/export_jsonl.py
python scripts/export_hunspell.py
python scripts/build_database.py
```

### 4. Run the API

```bash
uvicorn api.main:app --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## Docker

```bash
docker compose up --build
```

Then open:

`http://localhost:8000/docs`

## Microsoft Word installation

The generated Word dictionary is:

`dictionaries/microsoft-word/Khasi.dic`

In Microsoft Word:

File -> Options -> Proofing -> Custom Dictionaries -> Add

Select `Khasi.dic`.

Note: Microsoft Word custom dictionaries are word-acceptance lists. Definitions,
grammar, morphology, and AI features remain in the KhasiLex master database/API.

## Data model

Each lexical entry can contain:

- id
- headword
- normalized
- language
- part_of_speech
- definition_kha
- definition_en
- variants
- inflections
- synonyms
- antonyms
- example_kha
- example_en
- domain
- frequency
- source
- license
- verification_status
- notes

## Licensing and provenance

Do not copy a copyrighted Khasi dictionary into KhasiLex unless its licence permits
redistribution and derivative use.

Every imported entry should retain provenance information using the `source`,
`license`, and `verification_status` fields.

## Roadmap

1. KhasiLex Core
2. Microsoft Word spell-check dictionary
3. Rich linguistic dictionary
4. Khasi Hunspell rules
5. KhasiLex API
6. Microsoft Word Add-in
7. NLP / RAG / AI integration
8. Khasi tokenizer and morphological analyzer
9. Semantic search / embeddings
10. Translation and grammar assistance

## Professional Khasi features

KhasiLex supports first-class multiword and reduplicative entries. Repeated Khasi forms such as `biang biang`, `wut wut`, and `kloi kloi` are not automatically treated as duplicate-word errors. The NLP layer detects and preserves repeated constructions, while the lexical database stores their linguistic analysis separately.

Google/global-ready exports can be generated for glossary, sentence-pair, TMX, JSONL and linked-data workflows.

## Global multilingual layer

KhasiLex v0.3 adds a language-neutral concept/sense architecture. It can ingest equivalents from any BCP-47-tagged language while keeping Khasi as the authoritative target lexicon.

Important: the platform is technically capable of accepting global-language data, but correctness depends on reviewed lexical mappings. The starter package does not pretend to contain verified translations for every world language.

New data layers include:

- concepts
- senses
- multilingual equivalents
- grammar profiles
- pronunciation / IPA
- surface forms
- semantic relations
- multilingual examples
- language metadata

New API:

- `POST /api/v2/resolve-to-khasi`
- `GET /api/v2/language-tag/check`
- `GET /api/v2/capabilities`

The resolver refuses to guess when a reviewed translation is absent.

## Current status

This repository is the deployable technical foundation for a professional Khasi dictionary and global Khasi language technology platform. Lexical data must be expanded and expert-reviewed before being considered authoritative.
