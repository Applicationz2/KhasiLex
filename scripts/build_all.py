from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

for script in ["validate.py", "export_word_dic.py", "export_hunspell.py"]:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)

print("KhasiLex core build complete.")
