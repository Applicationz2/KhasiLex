from __future__ import annotations

from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile

from scripts.export_word_dic import build_words
from scripts.release_readiness import evaluate

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "data/master/khasi_lexicon.csv"

VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verified_csv_bytes() -> bytes:
    with LEXICON.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get("verification_status") == "verified"]
        fields = reader.fieldnames or []
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def hunspell_files(words: list[str]) -> tuple[bytes, bytes]:
    dic = (str(len(words)) + "\n" + "\n".join(words) + ("\n" if words else "")).encode("utf-8")
    aff = "SET UTF-8\nTRY abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZïÏñÑ\n".encode("utf-8")
    return dic, aff


def deterministic_zip(path: Path, files: dict[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, files[name])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a reproducible verified-only KhasiLex release bundle.")
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--target",
        choices=("review-pilot", "technical-alpha", "public-beta", "professional-core"),
        default="professional-core",
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "release")
    args = parser.parse_args()

    if not VERSION_RE.fullmatch(args.version):
        raise SystemExit("version must look like 1.0.0 or 1.0.0-rc.1")

    readiness = evaluate(args.target)
    if not readiness["ready"]:
        raise SystemExit("release blocked:\n- " + "\n- ".join(readiness["errors"]))

    verified_csv = verified_csv_bytes()
    words = build_words(include_unverified=False)
    word_dic = ("\n".join(words) + ("\n" if words else "")).encode("utf-8")
    hun_dic, hun_aff = hunspell_files(words)

    files: dict[str, bytes] = {
        f"KhasiLex-{args.version}/data/khasi_lexicon_verified.csv": verified_csv,
        f"KhasiLex-{args.version}/dictionaries/microsoft-word/Khasi.dic": word_dic,
        f"KhasiLex-{args.version}/dictionaries/hunspell/kha_IN.dic": hun_dic,
        f"KhasiLex-{args.version}/dictionaries/hunspell/kha_IN.aff": hun_aff,
        f"KhasiLex-{args.version}/quality/release_readiness.json": (
            json.dumps(readiness, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8"),
    }

    for name in ("LICENSE", "DATA_LICENSE.md", "THIRD_PARTY_DATA.md"):
        files[f"KhasiLex-{args.version}/{name}"] = (ROOT / name).read_bytes()

    manifest = {
        "schema_version": "1.0",
        "version": args.version,
        "target": args.target,
        "verified_entries": readiness["verified_entries"],
        "files": {
            name: {"sha256": sha256(data), "bytes": len(data)}
            for name, data in sorted(files.items())
        },
    }
    files[f"KhasiLex-{args.version}/MANIFEST.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")

    zip_path = args.output_dir / f"KhasiLex-{args.version}.zip"
    deterministic_zip(zip_path, files)
    checksum = sha256(zip_path.read_bytes())
    (args.output_dir / f"KhasiLex-{args.version}.zip.sha256").write_text(
        f"{checksum}  {zip_path.name}\n", encoding="utf-8"
    )
    print(zip_path)
    print(checksum)


if __name__ == "__main__":
    main()
