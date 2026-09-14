# Contributing to KhasiLex

KhasiLex is a public, professional Khasi lexical/NLP project. Contributions must preserve linguistic accuracy, provenance, Unicode integrity, licensing boundaries, and contributor privacy.

## Lexical contribution rules

1. Use UTF-8 and Unicode NFC.
2. Preserve Khasi diacritics such as `ï`, `Ï`, `ñ`, and `Ñ`; do not silently normalize them away.
3. Record source, licence, and provenance for every imported or source-derived candidate.
4. Do not import copyrighted dictionary/corpus text unless the licence or explicit permission permits the intended reuse and redistribution.
5. Keep AI-generated lexical content as candidate material requiring competent human Khasi review; AI alone may not create a final `verified` entry.
6. Use separate senses for genuinely different meanings and keep historical evidence distinct from modern editorial decisions.
7. Treat reduplication and multiword expressions as first-class linguistic entries rather than accidental duplicate text.
8. Do not use Glosbe, Webtran, or other reference-only services as bulk-import sources unless separate provenance/licensing review explicitly permits it.
9. Preserve per-record provenance in mixed-source datasets wherever practical.
10. Run repository validation and tests before opening a pull request.

## Review states

KhasiLex separates source attestation from editorial authority. The normal progression is:

`candidate / historical evidence -> lexical review -> reviewed -> verified`

Exact status names may vary by workflow, but no automated evidence, OCR import, corpus frequency, or AI output may bypass required human review gates.

## Public-source and licensing requirements

The repository-level `LICENSE` applies to KhasiLex software. Linguistic/data licensing is governed separately by `DATA_LICENSE.md`, `THIRD_PARTY_DATA.md`, and `data/sources/source_registry.csv`.

When contributing source-derived data:

- identify the exact source and, where relevant, page/revision/version;
- state the applicable licence or permission;
- preserve attribution/ShareAlike obligations for CC BY-SA-derived material;
- do not describe mixed-source datasets as wholly MIT-licensed;
- do not upload source files that are reference-only or not approved for redistribution.

By contributing software to this repository, you agree that your contribution may be distributed under the repository's MIT software licence. By contributing linguistic/editorial data, you confirm that you have the right to submit it and that its provenance/licensing metadata is accurate. Do not submit material whose redistribution rights are unclear.

## Privacy and secrets

This is a public repository. Do not commit:

- passwords, API keys, tokens, credentials, private keys, or `.env` files;
- private customer/user records or other confidential data;
- personal information that is not necessary for the contribution.

Public Git commits expose author metadata. Contributors who prefer not to publish a personal email address should configure GitHub's `noreply` commit email before committing.

If a secret is accidentally committed, revoke/rotate it immediately and report the incident through the process in `SECURITY.md`; deleting the file in a later commit is not sufficient by itself.

## Pull requests

Before opening a pull request:

1. keep the change focused and explain the linguistic/source impact;
2. run `python scripts/validate.py` and `python scripts/build_all.py`;
3. run `pytest -q -p no:cacheprovider`;
4. ensure new/changed data have provenance and licensing metadata;
5. do not claim `verified` status without the required human review evidence;
6. wait for the required GitHub Actions CI checks before merge.

For source or corpus additions, include the source identifier and explain whether the material is public domain, openly licensed, reference-only, or otherwise permissioned.
