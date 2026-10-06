# KhasiLex v1.0 Security Release Gate

A professional KhasiLex release must pass both software-security checks and lexical-data integrity checks.

## Automated security gates

The repository security workflow performs:

1. a complete-Git-history secret scan using the pinned Gitleaks CLI;
2. a Python dependency vulnerability audit with a pinned `pip-audit` version;
3. GitHub dependency review on pull requests;
4. CodeQL analysis for Python;
5. the existing KhasiLex CI matrix and Docker build.

Third-party GitHub Actions used by the project are pinned to immutable commit SHAs. The corresponding release version is retained as an inline comment for maintainability.

## Release-blocking findings

A v1.0 release is blocked by:

- an unresolved credential/secret finding;
- a high or critical dependency vulnerability without a documented mitigation;
- an unresolved high-confidence CodeQL finding affecting production paths;
- failure of the protected CI matrix;
- evidence that unreviewed lexical material can be exposed as authoritative production data.

## Full-history scan

The secret-scan job checks the complete repository history by checking out with `fetch-depth: 0` before running Gitleaks. A clean current tree alone is not sufficient for the v1.0 gate.

If a real credential is found, rotate/revoke it before any history rewrite. Do not merely delete the file in a later commit and assume the secret is remediated.

## Dependency maintenance

Dependabot is enabled for Python and GitHub Actions. Security-related upgrades must still pass the normal protected-branch CI and review process.

## Data integrity

Lexical integrity is part of the security model. In particular:

- no AI-generated item may self-promote to `verified`;
- Unicode normalization must not silently strip Khasi diacritics;
- historical/source evidence must remain distinguishable from modern authority;
- provenance and licence metadata must remain attached to published data.
