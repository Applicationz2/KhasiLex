from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORD_DIC = ROOT / "dictionaries/microsoft-word/Khasi.dic"
HUNSPELL_DIC = ROOT / "dictionaries/hunspell/kha_IN.dic"
HUNSPELL_AFF = ROOT / "dictionaries/hunspell/kha_IN.aff"
HUNSPELL_DIC.parent.mkdir(parents=True, exist_ok=True)

words = [w.strip() for w in WORD_DIC.read_text(encoding="utf-8").splitlines() if w.strip()]
HUNSPELL_DIC.write_text(str(len(words)) + "\n" + "\n".join(words) + "\n", encoding="utf-8")
if not HUNSPELL_AFF.exists():
    HUNSPELL_AFF.write_text("SET UTF-8\nTRY abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZïÏ\n", encoding="utf-8")
print(f"Wrote {len(words)} words to {HUNSPELL_DIC}")
