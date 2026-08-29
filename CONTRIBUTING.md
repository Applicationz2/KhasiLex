# Contributing to KhasiLex

KhasiLex is intended to become a professional, globally interoperable Khasi lexical resource. Contributions must preserve linguistic accuracy, provenance, and Unicode integrity.

## Lexical contribution rules

1. Add new entries to the master lexicon.
2. Use UTF-8 and Unicode NFC.
3. Preserve Khasi diacritics such as `ï` and `Ï`.
4. Do not normalize `ï` to `i`.
5. Record source and licence whenever possible.
6. Keep AI-generated lexical content as `pending` until human review.
7. Use separate senses for genuinely different meanings.
8. Treat reduplication and multiword expressions as first-class entries.
9. Do not import copyrighted dictionary content unless redistribution is permitted.
10. Run validation and tests before opening a pull request.

## Review states

`pending -> reviewed -> verified`

Production releases should rely on verified data only.
