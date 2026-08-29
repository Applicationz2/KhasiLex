# Nissor Singh 1906 Full-Dictionary Ingestion

KhasiLex v0.4 processes U Nissor Singh's **Khasi-English Dictionary (1906)** as a complete historical evidence source.

Canonical digital source:

- Internet Archive item: `khasienglishdict00singrich`
- OCR text: `https://archive.org/download/khasienglishdict00singrich/khasienglishdict00singrich_djvu.txt`
- scan/PDF: Wikimedia Commons / Internet Archive
- publication: Shillong, Eastern Bengal and Assam Secretariat Press, 1906
- historical variety: the author's preface identifies Cherra/Cherrapunji as the principal standard basis
- rights status used by KhasiLex: public-domain historical work

## Corpus policy

The entire OCR snapshot is preserved so later parser improvements remain reproducible. Extracted records are **historical candidates**, never automatic modern dictionary entries.

Every extracted row is `pending` and `human_review_required=yes` because the source may contain historical spelling, obsolete senses, dialectal material, OCR corruption, older grammatical terminology, source abbreviations, loanword markers, and polysemy requiring modern sense separation.

## Layout-aware parser

Parser v1.2 is deliberately conservative. The OCR preserves the original dictionary layout sufficiently well that genuine headword records normally begin on a new line. KhasiLex therefore requires an entry-shaped headword/POS structure at a **line start** instead of scanning arbitrary definition text.

This prevents imitative examples such as `[Imit. ...]` and embedded cross-references from being promoted to independent entries merely because they contain text resembling a part-of-speech abbreviation.

The parser also:

- preserves source apostrophes and markers in the raw historical row;
- checks the real alphabetic initial even when an apostrophe precedes it;
- downgrades non-native/likely OCR initials instead of deleting them;
- downgrades headwords with suspicious short trailing OCR tokens;
- preserves low-confidence rows in the complete historical corpus;
- excludes low-confidence rows from the normal editorial queue.

## Generated layers

`data/sources/nissor-1906/khasienglishdict00singrich_djvu.txt`
: Exact downloaded public-domain OCR snapshot used for the ingest.

`data/historical/nissor-1906/entries.csv`
: Complete structurally recognized historical extraction. This is evidence data, not an authoritative modern lexicon.

`data/historical/nissor-1906/review_queue.csv`
: One best record per normalized headword/POS pair with structural confidence at or above the editorial threshold. These are candidates for human Khasi review.

`data/historical/nissor-1906/suspicious_queue.csv`
: OCR/anomaly cases deliberately withheld from the normal review queue. Reviewers can recover genuine entries from this queue after checking the scanned page.

`quality/nissor1906_ingest_report.json`
: Reproducibility and coverage report containing source SHA-256, byte size, parser version, extracted counts, POS distribution and queue counts.

## Reproducible workflow

`.github/workflows/ingest-nissor-1906.yml` downloads the canonical OCR, regenerates all three data layers, validates them, runs the full KhasiLex test/build suite, builds the Docker image, and commits generated results back to the feature branch.

## Promotion workflow

Historical rows move through:

`raw source -> historical extraction -> editorial/suspicious queue -> scan check -> modern spelling review -> POS/grammar review -> sense separation -> independently reviewed Khasi definition -> English gloss review -> example review -> reviewed -> verified`

Only records that complete the full KhasiLex editorial process may be promoted into `data/master/khasi_lexicon.csv` as authoritative entries.

## Historical variants

When a 1906 spelling differs from a modern accepted spelling, KhasiLex should preserve the historical form as evidence and link it to the reviewed modern canonical form rather than silently deleting the historical orthography.

## Reduplication and imitative constructions

The source explicitly contains imitative word collocations and compounds. Genuine Khasi reduplications and repeated constructions must be modeled as linguistic forms, while strings appearing only inside an `[Imit.]` annotation must not automatically become dictionary headwords. Human review determines their final lexical or grammatical status.
