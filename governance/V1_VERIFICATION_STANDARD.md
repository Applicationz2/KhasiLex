# KhasiLex v1.0 Final Verification Standard

This standard governs promotion of Khasi lexical data to `verified` and, later, `published`.

## Principle

Evidence strength and publication authority are different things. Historical attestation, modern corpus attestation, lexicographic comparison, editorial review, and final verification are separate stages.

No AI system, corpus match, historical dictionary, machine translation system, or bulk approval may promote an entry to `verified` by itself.

## Required fields for a v1.0 verified lexical entry

Before promotion, the final-review record must contain:

- canonical Khasi spelling in Unicode NFC;
- part of speech / grammatical classification;
- Khasi definition written or explicitly approved by a human Khasi reviewer;
- reviewed English meaning/gloss;
- explicit sense decision: single sense or separated sense structure;
- natural Khasi example sentence;
- English example or translation when the English layer is published;
- register classification;
- dialect/standard-variety classification;
- source/provenance review;
- licence/reuse review;
- named human reviewer;
- ISO review date;
- final decision `verify`.

Where a word is polysemous, unrelated senses must not be collapsed into one record.

## Orthography

Khasi diacritics are significant. NFC normalization is required. Characters such as `ï`, `Ï`, and `ñ` must never be stripped silently.

Variant spellings must be represented explicitly rather than overwriting source forms.

## Reduplication and multiword expressions

Legitimate Khasi reduplication such as `biang biang`, `wut wut`, and `kloi kloi` must be represented as lexical/grammatical constructions, not rejected as accidental duplicate words. Meaning and grammatical function must still be human verified.

## Historical evidence

Nissor 1906 forms and glosses are evidence, not automatic modern definitions. Historical POS, spelling, register and borrowing labels are preserved as provenance even when a modern analysis differs.

Absence from the current licensed corpus does not prove that a word is archaic or obsolete.

## Standard cross-check set for pilot entries 21–100

For entries 21–100 of the v1.0 verification pilot, reviewers should use the following registered historical references as part of the standard corroboration set when relevant:

- **U. Nissor Singh, *English-Khasi Dictionary* (1920)** — use for English-to-Khasi lexical equivalents, historical definition comparison and reverse sense checking.
- **U. Nissor Singh, *Hints on the Study of the Khasi Language*** — use for grammar, part-of-speech and historical grammatical classification corroboration.

These references are corroborating evidence only. They do not override modern Khasi usage, current corpus evidence or competent human Khasi review, and they never authorize automatic promotion to `verified`.

The 1920 dictionary may be used according to its registered public-domain source status. *Hints* remains reference-only for extraction/copying unless the exact edition and reuse rights are separately confirmed; grammatical facts may be consulted and independently recorded with provenance.

## Review roles

KhasiLex distinguishes lexical, grammar, translation, provenance and technical review. One qualified human may fill more than one role during the pilot, but disputed or high-impact entries should receive independent review where practical.

AI may prepare candidate material but may not fill the final human-review authority field on its own.

## Pilot release gate

The first v1.0 verification pilot is exactly 100 entries. A row remains non-authoritative until its final decision is `verify` and all required fields pass the verification validator.

Corpus thresholds remain:

- 100 verified entries — review pilot;
- 1,000 verified entries — technical alpha;
- 5,000 verified entries — public beta;
- 25,000 verified entries — professional-core target.

These are quality gates, not permission to manufacture or infer linguistic content.
