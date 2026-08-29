# Editorial Workflow

Production KhasiLex data follows a controlled workflow:

`pending -> lexical_review -> grammar_review -> translation_review -> verified -> published`

## Required reviewers

For high-confidence public releases, use independent review roles where practical:

- Khasi lexical editor
- Khasi grammar reviewer
- translation-language reviewer
- technical/data reviewer

## No silent AI publication

AI may suggest definitions, senses, examples, grammatical analyses or foreign equivalents, but AI-generated content remains `pending` until reviewed.

## Sense splitting

If one headword has multiple meanings, create separate `sense_id` and `concept_id` records. Never collapse unrelated senses into one translation row.
