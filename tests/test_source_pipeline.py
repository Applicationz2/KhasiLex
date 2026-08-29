from pathlib import Path
import csv
import subprocess
import sys

from scripts.extract_frequency_candidates import source_record

ROOT = Path(__file__).resolve().parents[1]


def test_approved_sources_are_registered():
    ner = source_record("khasi-ner-2026")
    assert ner["status"] == "approved"
    assert ner["license"] == "CC-BY-SA-4.0"

    wiktionary = source_record("enwiktionary-kha")
    assert wiktionary["status"] == "approved"
    assert wiktionary["share_alike"] == "yes"


def test_frequency_extractor_excludes_existing_master(tmp_path):
    output = tmp_path / "candidates.csv"
    fixture = ROOT / "tests/fixtures/sample_khasi_corpus.txt"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/extract_frequency_candidates.py"),
            str(fixture),
            "--source-id",
            "khasi-ner-2026",
            "--min-frequency",
            "2",
            "--limit",
            "20",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    with output.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    by_word = {row["headword"].casefold(): row for row in rows}
    assert "ïing" not in by_word
    assert "um" not in by_word
    assert "bam" not in by_word
    assert by_word["kloi"]["frequency"] == "4"
    assert by_word["briew"]["frequency"] == "3"
    assert by_word["kloi"]["source"] == "khasi-ner-2026"
    assert by_word["kloi"]["license"] == "CC-BY-SA-4.0"


def test_frequency_extractor_can_include_existing_for_analysis(tmp_path):
    output = tmp_path / "all_candidates.csv"
    fixture = ROOT / "tests/fixtures/sample_khasi_corpus.txt"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/extract_frequency_candidates.py"),
            str(fixture),
            "--source-id",
            "khasi-ner-2026",
            "--min-frequency",
            "2",
            "--include-existing",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    with output.open(encoding="utf-8", newline="") as f:
        words = {row["headword"].casefold() for row in csv.DictReader(f)}

    assert {"ïing", "um", "bam", "kloi", "briew"}.issubset(words)
