# KhasiLex AI-native multilingual architecture

## Purpose

KhasiLex is an authoritative Khasi lexical platform with AI-assisted multilingual interoperability. Khasi remains the authoritative linguistic core. AI may propose, rank, disambiguate, align, or translate, but AI output is never authoritative merely because a model produced it.

KhasiLex does not claim guaranteed translation for every human language. It is designed to support any language for which sufficient linguistic identification, data, models, or reviewed translation resources are available, including progressive support for low-resource, historical, classical, endangered, and specialist languages.

## Three-layer architecture

### 1. Authoritative Khasi lexical core

Human-verified Khasi lexical data is the primary source of truth. A professional lexical record should be able to represent:

- canonical headword and source variants;
- Unicode-normalized form;
- part of speech and grammatical profile;
- Khasi definition;
- English gloss/equivalent where appropriate;
- explicit sense identifiers;
- morphology;
- semantic domain;
- synonyms and antonyms;
- natural examples;
- idioms and compounds;
- dialect/register;
- etymology or historical form where evidence supports it;
- pronunciation/IPA and media when reviewed;
- source, provenance and licence;
- reviewer, review date and revision history;
- verification state and confidence.

The master lexicon must never be silently rewritten by an AI provider.

### 2. AI linguistic engine

AI-facing capabilities may include:

- contextual word-sense disambiguation;
- morphological and grammatical analysis;
- semantic search and embeddings;
- spelling and orthographic suggestions;
- idiom and multiword-expression recognition;
- transliteration;
- pronunciation assistance;
- candidate example generation;
- OCR-assisted historical ingestion;
- candidate translation generation;
- provider/model comparison;
- low-resource fallback routing.

AI-generated material must remain in a candidate or advisory state until a competent human reviewer explicitly approves it.

### 3. Multilingual translation gateway

KhasiLex uses stable sense/concept identifiers so languages can align through reviewed semantic representations rather than requiring a separate hard-coded Khasi pair for every language.

Conceptual route:

```
source language
   -> detected/declared BCP-47 language tag
   -> source expression / sense candidates
   -> semantic concept + context
   -> KhasiLex reviewed sense/concept layer
   -> target-language equivalent candidates
```

A direct source-target pair is preferred when high-quality reviewed data exists. A controlled pivot route may be used when direct data is unavailable, but the route and confidence must be exposed to the caller.

## Authority boundary

KhasiLex separates evidence and authority.

### Authoritative

A result may be labelled authoritative only when it is grounded in human-reviewed KhasiLex data whose source/licence/provenance requirements are satisfied.

### AI-assisted

A result generated, inferred, ranked, or translated by an AI provider must carry provenance describing the provider/model or processing route and must not be labelled authoritative unless the underlying lexical decision was separately human verified.

## Confidence classes

The public/API model should distinguish at least:

- `verified` — human-reviewed authoritative lexical mapping;
- `high_confidence_ai_assisted` — AI-assisted output strongly grounded in verified lexical material;
- `ai_assisted` — model-generated or model-ranked candidate;
- `low_resource` — result relies on sparse or indirect language resources;
- `historical_or_uncertain` — historical, damaged, ambiguous, or otherwise uncertain evidence;
- `needs_human_review` — no professional claim should be made without review.

Numeric confidence may accompany these classes but must never replace the authority label.

## Translation response provenance

A translation result should be able to report:

- source language tag;
- target language tag;
- source text;
- normalized source text;
- resolved concept/sense identifiers;
- direct or pivot route;
- candidate provider/model if AI is used;
- evidence sources;
- lexical verification state;
- confidence class and numeric score when available;
- warnings for ambiguity, low-resource routing, historical material, or specialist domains.

## High-risk domains

For Scripture, theology, law, medicine, safety-critical material, historical texts, poetry, and specialist terminology, a plausible AI translation must not be treated as professionally verified without domain-appropriate human review.

## G1 architectural gate

Technical Alpha at 1,000 verified entries requires all of the following in addition to entry count:

1. authoritative Khasi data remains separated from AI candidate data;
2. verified-only production lookup remains enforced;
3. multilingual sense/concept identifiers remain stable enough for integration testing;
4. BCP-47-style language-tag handling is available;
5. AI output cannot automatically promote itself to `verified`;
6. translation/resolution exposes ambiguity instead of guessing;
7. provenance/licence metadata remains part of the release contract;
8. an explicit capability statement avoids universal-translation guarantees;
9. release-readiness automation checks the architecture gate.

Passing 1,000 entries without these safeguards does not constitute Technical Alpha readiness.
