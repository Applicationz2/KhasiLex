# Batch 003 — 20-entry evidence disposition audit (2026-11-20)

This is a **complete record-by-record audit**, not a claim that every lexical sense has been independently verified. Source: `data/review/batches/g1-batch-003-candidates.json` at branch head prior to this report. Original 1906 headwords/glosses are source-specific. All promotion flags remain false.

| ID | Historical headword | Historical 1906 gloss (abbreviated) | 1920 matrix status | Modern evidence matrix | Decision |
|---|---|---|---|---|---|
| g1-hist-003-001 | Áb! | the imitation of the cry of a crow | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-002 | *Abir | red powder used in the Holi festival | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-003 | Ak! | ejaculation of disgust at an unpleasant smell | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-004 | Aku! | expressing disgust at a bad smell | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-005 | *Adda | a stage for changing horses or dak-runners | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-006 | Angret | a dare-devil (from Hindustani Angrez) | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-007 | Ahor | a marshy place; swamp | page_image_verified | independent_dictionary_evidence_not_contemporary_usage | defer; no promotion |
| g1-hist-003-008 | Ai-bai-siew | to give money for buying things at a time, e.g. on a market day | page_image_verified_related_form_only | not_verified | defer; no promotion |
| g1-hist-003-009 | Ai-'baibat | to pay ready money | page_image_verified_related_form_only | not_verified | defer; no promotion |
| g1-hist-003-010 | Ai-bud-nám | to slander; defame | page_image_verified | not_verified | defer; no promotion |
| g1-hist-003-011 | Ai-khawdûh | to leave uncared for; to be outcast | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-012 | Ai-khusnám | to confer honour for meritorious conduct | page_image_verified | not_verified | defer; no promotion |
| g1-hist-003-013 | Ai-ksew | to put a dog on the scent | page_image_verified | not_verified | defer; no promotion |
| g1-hist-003-014 | Ai-huspai | to indulge | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-015 | Ai-lait-lân | to let loose; give one their own inclination | page_image_verified_related_form_only | not_verified | defer; no promotion |
| g1-hist-003-016 | Ai-mon | to give one their own will | page_image_verified | not_verified | defer; no promotion |
| g1-hist-003-017 | A-iu | what | page_image_verified | independent_dictionary_evidence_not_contemporary_usage | defer; no promotion |
| g1-hist-003-018 | Along | a lock-up; Hajut | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-019 | Ama or Amai! | exclamation upon narrow escape | not_yet_established | not_verified | defer; no promotion |
| g1-hist-003-020 | Amrang | harsh tone; empty words | not_yet_established | not_verified | defer; no promotion |

## Audit counts

- 20/20 historical candidates have recorded original-1906 facsimile checks in the existing candidate file.
- 6/20 record `page_image_verified` in the 1920 matrix (Ahor, Ai-bud-nám, Ai-khusnám, Ai-ksew, Ai-mon, A-iu).
- 3/20 record `page_image_verified_related_form_only` (Ai-bai-siew, Ai-'baibat, Ai-lait-lân).
- 11/20 record `not_yet_established`.
- 2/20 record independent *dictionary* evidence but explicitly **not contemporary contextual usage** (Ahor, A-iu).
- 0/20 independently verified contemporary contextual sense matches recorded; 0 promoted.

## Verification policy and remaining blockers

1. The same 1906 source's internal cross-references do not count as independent authorial evidence.
2. The 1920 reverse dictionary is associated with the same authorial tradition and is cross-edition corroboration, not automatically independent authorship.
3. Related English glosses or related Khasi forms must not be treated as exact-headword matches.
4. The 1968 Ka Dienshonhi and 1973 Bars entry pages remain uninspected for the unresolved target senses; bibliographic identification is not entry verification.
5. For each unresolved candidate, obtain an inspectable independent edition/page/entry, exact form, POS, sense, contextual usage and licence assessment. If unavailable, mark historical-only/deferred; do not invent attestations.
6. No merge, stable lexical IDs, promotion, or production publication without project-owner review at an exact head SHA and required CI checks.

This report completes the **audit pass** of all 20 candidate records, but **does not close** the independent-evidence research gate.
