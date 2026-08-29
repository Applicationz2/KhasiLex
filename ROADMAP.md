# KhasiLex Roadmap

KhasiLex is being developed as a professional Khasi lexical, grammar, translation, spell-checking, and AI-language infrastructure platform.

## v0.3 — Technical foundation

Status: implemented.

- UTF-8 / Unicode NFC handling
- Khasi `kha` language metadata
- Microsoft Word dictionary export
- Hunspell export foundation
- FastAPI lexical API
- Khasi reduplication detection
- Multiword lexical matching
- Sense/concept multilingual model
- BCP-47-style language-tag handling
- Docker deployment
- Automated tests and CI
- Provenance and human-verification workflow

## v0.4 — Authoritative lexical corpus foundation

Priority: highest.

- establish Khasi editorial board/reviewer workflow;
- define normative headword and variant policy;
- collect and verify high-frequency Khasi vocabulary;
- split polysemous words into explicit senses;
- expand parts of speech and semantic domains;
- add verified synonyms and antonyms;
- add natural Khasi example sentences;
- expand reduplicative and multiword constructions;
- record source/licence provenance for every production entry;
- create quality metrics and corpus coverage reports.

Target: first substantial verified core lexicon rather than a large unreviewed word dump.

## v0.5 — Professional Khasi grammar and morphology

- grammatical-gender and agreement descriptions;
- noun-phrase grammar;
- pronoun paradigms;
- verb valency/transitivity;
- tense/aspect/modality descriptions;
- negation;
- derivational morphology;
- compounding;
- full and partial reduplication;
- syntax and clause structures;
- dialect/register annotations;
- expert-reviewed Hunspell affix/morphology rules.

## v0.6 — Pronunciation and lexical media

- IPA for verified entries;
- syllabification and stress metadata where relevant;
- reviewed audio pronunciation recordings;
- speaker/dialect metadata;
- pronunciation API.

## v0.7 — Global multilingual translation layer

- verified English ↔ Khasi concept mappings;
- Hindi, Bengali and other major Indian languages;
- Chinese, French, Portuguese, Spanish, Hebrew, Greek, Arabic and other world languages;
- context-sensitive sense disambiguation;
- aligned multilingual example sentences;
- TMX/TBX/TEI/OntoLex-compatible release exports;
- translation-memory and glossary packages.

The architecture supports any BCP-47-tagged language; language coverage is data-driven rather than hard-coded.

## v0.8 — AI and NLP integration

- Khasi tokenizer improvements;
- morphological analysis;
- grammatical generation;
- semantic search and embeddings;
- RAG-ready lexical service;
- controlled AI candidate generation with mandatory human verification;
- evaluation datasets for spelling, grammar and translation.

## v0.9 — Desktop, Office and browser integrations

- improved Microsoft Word integration;
- LibreOffice/Hunspell packaging;
- browser/editor spell-check integration where supported;
- public dictionary web interface;
- SDK packages for applications.

## v1.0 — Professional public Khasi dictionary platform

Release criteria:

- substantial expert-reviewed Khasi lexicon;
- documented editorial policy;
- stable sense and concept identifiers;
- reviewed grammar model;
- pronunciation coverage;
- multilingual translation coverage;
- reproducible releases and quality reports;
- public API and documented integration model;
- sustainable contribution and governance process.

## Guiding rule

Accuracy outranks raw entry count. KhasiLex must never mark machine-generated, copied, or linguistically uncertain material as authoritative merely to increase apparent coverage.
