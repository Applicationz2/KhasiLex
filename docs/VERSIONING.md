# Versioning and Release Policy

KhasiLex separates **software versioning** from **lexical-data maturity**.

## Semantic versions

Software/API releases use semantic versions such as `0.5.0` or `1.0.0`.

A version number does not override the lexical-quality gates.

## Lexical release targets

- `review-pilot`: 100 verified entries
- `technical-alpha`: 1,000 verified entries
- `public-beta`: 5,000 verified entries
- `professional-core`: 25,000 verified entries

A professional `1.0.0` release must satisfy the `professional-core` gate.

## Stable v1.0 prerequisites

Before a v1.0 tag/release:

1. the professional-core verified-entry count is met;
2. every published entry satisfies the v1 lexical verification requirements;
3. the KhasiLex-authored linguistic-data licence is explicitly approved;
4. security and protected CI are green;
5. release bundle hashes are reproducible;
6. the production deployment is healthy;
7. the public dictionary/API exposes verified authoritative material by default.

Pre-release software tags must not imply that unverified corpus material is authoritative.
