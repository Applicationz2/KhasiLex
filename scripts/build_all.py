from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

for script in [
    "validate.py",
    "validate_sources.py",
    "validate_modern_evidence.py",
    "validate_nissor_1906_corpus.py",
    "validate_nissor_1906_ocr_resolutions.py",
    "audit_review_batch.py",
    "corpus_audit.py",
    "export_word_dic.py",
    "export_hunspell.py",
]:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)

build_dir = ROOT / "build"
build_dir.mkdir(parents=True, exist_ok=True)
structured = build_dir / "nissor1906_structured.csv"
modern_overlay = build_dir / "nissor1906_modern_evidence.csv"
modern_report = build_dir / "nissor1906_modern_evidence_report.json"
sense_candidates = build_dir / "nissor1906_sense_candidates.csv"
review_queue = build_dir / "nissor1906_modern_review_queue.csv"
review_manifest = build_dir / "nissor1906_modern_review_manifest.json"

subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts" / "structure_nissor_1906_corpus.py"),
        "--output",
        str(structured),
    ],
    cwd=ROOT,
    check=True,
)

subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts" / "enrich_nissor_modern.py"),
        "--structured",
        str(structured),
        "--output",
        str(modern_overlay),
        "--report",
        str(modern_report),
    ],
    cwd=ROOT,
    check=True,
)

subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts" / "generate_nissor_sense_candidates.py"),
        "--structured",
        str(structured),
        "--output",
        str(sense_candidates),
    ],
    cwd=ROOT,
    check=True,
)

subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts" / "generate_modern_review_queue.py"),
        "--overlay",
        str(modern_overlay),
        "--output",
        str(review_queue),
        "--manifest",
        str(review_manifest),
        "--batch-size",
        "100",
    ],
    cwd=ROOT,
    check=True,
)

print("KhasiLex v0.4 corpus build complete with structured modern-evidence, sense-candidate and ranked-review layers.")
