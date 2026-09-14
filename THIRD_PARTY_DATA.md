# Third-Party Data Notices

KhasiLex software code and third-party linguistic data have different licence and provenance obligations. The repository-level MIT `LICENSE` applies to software, not automatically to linguistic data. See `DATA_LICENSE.md` for the data-licensing boundary and redistribution matrix.

## U Nissor Singh, Khasi-English Dictionary (1906)

- Source ID: `nissor-1906-kha-en`
- Title: **Khasi-English Dictionary**
- Author: U Nissor Singh
- Publication year: 1906
- Canonical source: public-domain Internet Archive / Wikimedia Commons scan
- Licence/status: **Public Domain**
- KhasiLex use: historical headwords, historical English glosses, grammatical labels, historical lexical comparison and OCR/review evidence

KhasiLex preserves the source snapshot and provenance separately from modern review decisions. Public-domain status does not make historical spelling, meaning, POS, register or present-day usage automatically authoritative modern Standard Khasi.

## Khasi Named Entity Recognition Corpus

- Source ID: `khasi-ner-2026`
- Title: **Khasi Named Entity Recognition Corpus**
- Authors: Ransly Hoojon, Amitabha Nath, Saralin A. Lyngdoh
- Version: 1.0.0 (2026)
- DOI: `10.5281/zenodo.20474594`
- Licence: **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**
- KhasiLex use: candidate extraction, corpus-frequency analysis and linguistic evidence

Source-derived records must retain attribution/licence metadata. Adapted material distributed from this source remains subject to the applicable ShareAlike requirements. Modern-evidence overlays produced from the corpus must retain source ID, licence and attribution rather than being represented as licence-free KhasiLex data.

## English Wiktionary Khasi entries

- Source ID: `enwiktionary-kha`
- Resource: English Wiktionary Khasi language/lemma entries
- Canonical category: `https://en.wiktionary.org/wiki/Category:Khasi_language`
- Text licence: **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, with additional Wiktionary terms and possible separately licensed embedded material
- KhasiLex use: candidate headwords, grammatical comparison and lexicographic evidence

When copyrightable Wiktionary text is copied or adapted, KhasiLex must preserve attribution and the applicable ShareAlike terms, including page/revision information where practical. Headword-only candidate extraction should still retain source provenance in the editorial workflow.

## Meghalaya Government current Khasi publications

The following registered resources are used only as **occurrence/spelling evidence** in the modern-evidence layer:

- `meg-gov-rti-kha` — Khasi RTI guide
- `meg-gov-cid-advisory-kha` — CID public-interest advisory in Khasi
- `meg-gov-aquaculture-kha` — Meghalaya State Aquaculture Mission Khasi form

KhasiLex does not bulk-copy their prose or import definitions from these publications. The seed evidence file records lexical occurrence metadata, source identifiers and source URLs. This reference use does not assert a general reusable dictionary-data licence for the publications.

## Reference-only services

The source registry also tracks services such as Glosbe and Webtran for reference/candidate comparison. Their content is **not approved for bulk redistribution or authoritative import** unless separate provenance and licensing review establishes that reuse is permitted.

## Modern-evidence overlays

`data/modern_evidence/current_attestations_seed.csv` and generated modern-evidence reports are evidence layers, not authoritative dictionary releases. They may combine public-domain historical records with reference metadata and CC BY-SA-derived corpus evidence. Any redistributed derivative containing applicable CC BY-SA-derived material must preserve the corresponding attribution and ShareAlike obligations.

## Data release rule

Every public release must identify which files are:

1. KhasiLex software under MIT;
2. public-domain source material;
3. CC BY-SA-derived material;
4. reference-only evidence/metadata;
5. original KhasiLex-authored linguistic/editorial data; or
6. mixed-source data with per-record provenance.

No project-level software licence should be interpreted as relicensing third-party linguistic content.
