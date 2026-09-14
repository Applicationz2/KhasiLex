# KhasiLex Public-Release Audit

Date: 2026-09-14

This document records repository checks performed after KhasiLex changed from private to public visibility and after the Nissor modern-evidence pipeline landed on `main`.

## Scope

The audit covers the current public repository tree for:

- obvious committed secrets and secret-bearing filenames;
- public/private data separation;
- software and linguistic-data licensing boundaries;
- third-party source provenance;
- redistribution rules for generated data;
- public-repository governance risks.

This is a release-engineering audit, not legal advice and not a substitute for a dedicated full-history secret scanner.

## Findings

### 1. Current-tree secret indicators

Repository code searches on the public default branch found no obvious matches for the common secret indicators checked during this audit, including API-key/password labels, GitHub personal-access-token prefixes, AWS access-key prefixes, bearer-token literals, or private-key headers.

The checked tree contains no committed `.env`, `.pem`, or `.key` files. `.gitignore` is hardened to exclude local environment files, common private-key/container formats, common credentials/secrets JSON filenames, local SQLite databases, virtual environments, caches, and generated build output.

**Boundary:** this does not prove that no secret ever existed in an older commit. If GitHub secret scanning reports an alert, or if a credential is known to have been committed historically, revoke/rotate the credential first and then consider history rewriting.

### 2. Software licence

The repository-level `LICENSE` is the unmodified MIT licence for software. Linguistic/data restrictions and third-party obligations are documented separately rather than modifying the MIT grant.

### 3. Public-domain Nissor Singh corpus

The 1906 U Nissor Singh Khasi-English Dictionary source layer is documented as public-domain historical material. KhasiLex keeps historical evidence distinct from present-day editorial authority.

Public-domain status does not imply that historical spellings, senses, POS labels, register, borrowing status, or present-day usage are verified modern Standard Khasi.

### 4. CC BY-SA sources

The source registry identifies the Khasi NER corpus and English Wiktionary Khasi material as CC BY-SA 4.0 sources where applicable source-derived copyrightable content is distributed.

Source-derived records must preserve attribution and licence/provenance metadata. Files containing applicable CC BY-SA-derived material must not be described as MIT-licensed merely because the software is MIT-licensed.

### 5. Reference-only sources

Registered Meghalaya Government publications are used as current Khasi occurrence/spelling evidence without bulk-copying source prose. Glosbe and Webtran remain reference/candidate-only services. Their content is not approved for bulk redistribution or authoritative import without separate provenance and licensing review.

### 6. Generated and mixed-source artifacts

`DATA_LICENSE.md` defines a redistribution matrix for preserved source material, historical Nissor-derived data, modern-evidence overlays, review queues, sense-candidate outputs, and reference-only evidence.

Generated artifacts must preserve source/provenance metadata and must not be presented as carrying a blanket MIT data licence.

### 7. Original KhasiLex linguistic data

Original KhasiLex-authored definitions, examples, annotations, grammar metadata, modern canonical decisions, and sense analysis still need an explicit dedicated open-data licence before a stable public data release. The software MIT licence does not automatically cover those linguistic/editorial data.

### 8. Public-repository governance

Changing repository visibility disabled the previous ruleset state. `main` should be protected again after this hardening PR is merged.

Recommended minimum protection for `main`:

- require a pull request before merge;
- require KhasiLex CI Python 3.11, 3.12, 3.13 and Docker checks;
- block force pushes;
- block branch deletion;
- require conversation resolution when review threads are used.

### 9. Commit identity privacy

A public Git repository exposes commit author metadata. Contributors who do not want a personal email address published should use a GitHub-provided `noreply` commit email and enable GitHub email-privacy settings for future commits.

## Release decision

No current-tree blocker was found that requires KhasiLex to return to private visibility.

Before calling the corpus itself a stable open-data release, complete these remaining governance items:

1. select an explicit licence for original KhasiLex-authored linguistic/editorial data;
2. restore `main` branch/ruleset protection;
3. review GitHub secret-scanning alerts, if any, and perform a dedicated full-history secret scan before a major release;
4. retain per-record provenance for mixed-source data.
