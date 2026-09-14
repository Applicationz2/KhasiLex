from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

for script in [
    "validate.py",
    "validate_sources.py",
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
subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts" / "structure_nissor_1906_corpus.py"),
        "--output",
        str(build_dir / "nissor1906_structured.csv"),
    ],
    cwd=ROOT,
    check=True,
)

print("KhasiLex v0.4 corpus build complete.")
