# KhasiLex Corpus Source Policy

KhasiLex distinguishes **evidence sources** from the **authoritative dictionary corpus**.

## Source classes

### Text corpus

A text corpus can establish that a spelling or construction occurs in real Khasi usage and can provide frequency/context evidence. It does **not**, by itself, prove:

- normative spelling;
- dictionary meaning;
- part of speech;
- grammatical function;
- synonymy/antonymy;
- appropriateness across registers or dialects.

Corpus-derived words therefore enter KhasiLex as `pending` candidates.

### Lexicographic resource

An open dictionary or lexical resource may supply candidate headwords, grammatical information, definitions or examples subject to its licence. KhasiLex records the exact source and, where relevant, page/revision information.

If source text is copied or adapted, the source licence must be honoured. A reviewer may instead use the resource as evidence and independently write a KhasiLex definition.

### Human contribution

A contributor may propose original Khasi lexical information. The contribution must be licensed for KhasiLex use and still pass editorial review.

## Source registry

Every approved external source must appear in `data/sources/source_registry.csv` before automated extraction or import.

The registry records:

- stable source ID;
- title and source type;
- canonical location;
- source version/revision;
- licence;
- attribution obligations;
- ShareAlike obligations;
- approved uses;
- definition-import policy;
- approval state.

Tools must refuse sources not marked `approved`.

## Licence separation

KhasiLex software and third-party lexical/corpus data are not assumed to share one licence.

Source-derived candidate records retain source and licence metadata. When a source requires attribution or ShareAlike, downstream exports containing copied/adapted source material must comply with those terms.

A permissively licensed software repository does not erase the licence of third-party data stored or processed by it.

## Current approved sources

### Khasi Named Entity Recognition Corpus (2026)

Registered as `khasi-ner-2026`.

Approved for candidate spelling extraction, token-frequency analysis and corpus research. Dictionary definitions must not be inferred automatically from corpus occurrences.

### English Wiktionary Khasi entries

Registered as `enwiktionary-kha`.

Approved as a candidate headword and lexicographic comparison source. Copied/adapted entry text requires source attribution and compatible ShareAlike treatment. For the core KhasiLex corpus, independent Khasi definitions are preferred unless there is a deliberate CC-BY-SA data release path.

## Prohibited shortcuts

KhasiLex must not:

- scrape a copyrighted dictionary and mark the result as original;
- convert corpus frequency directly into `verified` status;
- infer a definition solely from an AI model without human review;
- remove source/licence metadata from derived candidate records;
- mix incompatible source licences into a release without an explicit licensing decision.

## Review principle

A source provides **evidence**. KhasiLex verification is an editorial judgement supported by evidence, not an automatic consequence of source presence.
