# KhasiLex Data Licensing

KhasiLex separates software licensing from linguistic-data licensing.

## Software

Source code and software documentation covered by the repository-level `LICENSE` are licensed under the MIT License.

The MIT software licence does **not** automatically relicense lexical data, corpora, dictionary source material, translation-memory data, evidence files, or contributor-authored linguistic content stored in or processed by this repository.

## Public-domain historical source

The following historical source is treated as public-domain source material:

- **U Nissor Singh, _Khasi-English Dictionary_ (1906)** (`source_id: nissor-1906-kha-en`).

The preserved source snapshot, historical headwords, historical glosses, and source-era grammatical labels derived directly from that public-domain work may be redistributed as public-domain source material. KhasiLex still preserves source provenance and keeps historical evidence separate from present-day editorial authority.

KhasiLex-authored review decisions, modern-status labels, annotations, examples, definitions, sense analysis, and other original editorial additions are not automatically placed in the public domain merely because they refer to a public-domain source.

## CC BY-SA 4.0 sources

Some evidence or candidate records derive from sources licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, including:

- the Khasi Named Entity Recognition Corpus (`source_id: khasi-ner-2026`) where source-derived material is distributed;
- English Wiktionary Khasi entries (`source_id: enwiktionary-kha`) where copyrightable text is copied or adapted.

Redistribution of copyrightable material derived from these sources must preserve the required attribution, licence notice, and ShareAlike obligations. Where practical, KhasiLex records source IDs and revision/version information per record.

## Reference-only sources

The following categories are reference/evidence sources, not bulk-redistribution sources unless separate permission or licensing evidence is established:

- Meghalaya Government Khasi publications registered for occurrence/spelling evidence;
- Glosbe community/translation-memory content;
- Webtran machine-translation output.

KhasiLex may record that a lexical form occurs in a referenced publication, together with source metadata, without copying substantial source prose into redistributable lexical data.

## Redistribution matrix

| Data or artifact | Redistribution status | Required treatment |
| --- | --- | --- |
| `data/sources/nissor-1906/...` source snapshot | Permitted as public-domain source material | Preserve source/provenance information where practical |
| Historical Nissor-derived headwords/glosses/POS evidence | Permitted as public-domain-derived historical evidence | Keep historical-source attribution and do not present it as automatically verified modern Khasi |
| Khasi NER-derived copyrightable/adapted material | Permitted subject to CC BY-SA 4.0 | Preserve attribution, licence, and ShareAlike requirements |
| Wiktionary copied/adapted text | Permitted subject to Wiktionary/CC BY-SA terms | Preserve page/revision attribution where practical and ShareAlike requirements |
| Meghalaya Government source documents/prose | Not approved here for bulk redistribution | Use only reference/occurrence metadata unless separate reuse permission is established |
| Glosbe/Webtran content | Not approved for bulk redistribution | Reference/candidate use only unless separate provenance/licensing review permits reuse |
| `build/nissor1906_structured.csv` | Mixed/project-derived | Preserve source provenance; do not represent KhasiLex-authored fields as MIT-licensed data |
| Modern-evidence overlays/reports/queues | Mixed-source | Carry source/licence metadata; CC BY-SA obligations follow applicable derived material; do not embed unlicensed source prose |
| Sense-candidate outputs based solely on Nissor historical glosses | Public-domain source plus project-generated structure | Preserve Nissor provenance; KhasiLex-authored metadata remains outside the MIT software grant |

## KhasiLex-authored linguistic/editorial data

Original KhasiLex definitions, examples, annotations, grammar metadata, modern canonical decisions, sense analysis, and review decisions are **not automatically covered by the MIT software licence merely because they are stored in this repository**.

A dedicated open-data licence for original KhasiLex-authored linguistic/editorial data should be selected explicitly by the project owner before a stable public data release. Until then, a public file must not be described as having a blanket open-data licence unless that file or release explicitly states one.

## Mixed-source files

Files combining KhasiLex-authored material with third-party evidence must preserve per-record provenance where practical. A mixed file must not be represented as wholly MIT-licensed merely because the surrounding software is MIT-licensed.

## Linguistic status is separate from licence status

Public-domain or openly licensed material is not automatically authoritative modern Standard Khasi. KhasiLex editorial and verification gates continue to apply independently of copyright/licensing status.

See also `THIRD_PARTY_DATA.md` and `data/sources/source_registry.csv`.
