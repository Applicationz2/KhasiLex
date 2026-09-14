# Third-Party Data Notices

KhasiLex software code and third-party linguistic data may have different licence obligations. This file records external resources approved for use in the corpus-development workflow.

## Khasi Named Entity Recognition Corpus

- Source ID: `khasi-ner-2026`
- Title: **Khasi Named Entity Recognition Corpus**
- Authors: Ransly Hoojon, Amitabha Nath, Saralin A. Lyngdoh
- Version: 1.0.0 (2026)
- DOI: `10.5281/zenodo.20474594`
- Licence: **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**
- KhasiLex use: candidate extraction, corpus-frequency analysis and linguistic evidence

Source-derived records must retain attribution/licence metadata. Adapted material distributed from this source remains subject to its ShareAlike requirements. Modern-evidence overlays produced from the full corpus must therefore retain the source ID, licence and attribution instead of being treated as licence-free KhasiLex data.

## Wiktionary Khasi entries

- Source ID: `enwiktionary-kha`
- Resource: English Wiktionary Khasi language/lemma entries
- Canonical category: `https://en.wiktionary.org/wiki/Category:Khasi_language`
- Text licence: **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, with additional Wiktionary terms and possible separately licensed embedded material
- KhasiLex use: candidate headwords, grammatical comparison and lexicographic evidence

When Wiktionary text is copied or adapted, KhasiLex must preserve attribution and the applicable ShareAlike terms, ideally including the exact page and revision identifier. Headword-only candidate extraction should still retain source provenance in the editorial workflow.

## Meghalaya Government current Khasi publications

The following registered resources are used only as **occurrence/spelling evidence** in the modern-evidence layer:

- `meg-gov-rti-kha` — Khasi RTI guide
- `meg-gov-cid-advisory-kha` — CID public-interest advisory in Khasi
- `meg-gov-aquaculture-kha` — Meghalaya State Aquaculture Mission Khasi form

KhasiLex does not bulk-copy their prose or import definitions from these publications. The seed evidence file records only lexical occurrence metadata, source identifiers and source URLs. This use does not assert that the publications grant a reusable dictionary-data licence; it uses them as references showing that particular forms occur in current official Khasi material.

## Modern-evidence overlays

`data/modern_evidence/current_attestations_seed.csv` and generated modern-evidence reports are evidence layers, not authoritative dictionary releases. They may combine public-domain historical records with reference metadata and CC BY-SA-derived corpus statistics. Any redistributed derivative containing CC BY-SA corpus-derived material must preserve the applicable attribution and ShareAlike obligations.

## Data release rule

A KhasiLex release must document which files are original KhasiLex data and which contain third-party or adapted material. No project-level software licence should be interpreted as relicensing third-party linguistic content.
