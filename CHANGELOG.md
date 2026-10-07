# Changelog

All notable KhasiLex changes intended for public releases are recorded here.

The project uses semantic versioning for software/API compatibility. Linguistic-data maturity is additionally controlled by verified-entry release gates.

## Unreleased

### Added
- v1.0 final-verification standard and exact 100-entry review pilot.
- Full-history secret scanning, dependency audit, CodeQL and Dependabot.
- Verified-only production API boundary, readiness checks, request IDs, structured logging, rate/request limits and security headers.
- Release-readiness and reproducible verified-only bundle foundation.
- Hardened non-root production container configuration.

### Changed
- Microsoft Word release export is verified-only by default.
- Professional v1.0 claims are gated on the 25,000 verified-entry professional-core target.

### Security
- Upgraded pytest requirement to the fixed 9.0.3+ range for PYSEC-2026-1845.
