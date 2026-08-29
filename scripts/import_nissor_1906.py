from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path

SOURCE_ID = "nissor-1906-kha-en"
SOURCE_YEAR = 1906
DEFAULT_SOURCE_URL = (
    "https://archive.org/download/khasienglishdict00singrich/"
    "khasienglishdict00singrich_djvu.txt"
)

LETTERS = "A-Za-zÀ-ÖØ-öø-ÿÏïÑñ"
UPPER = "A-ZÀ-ÖØ-ÞÏÑ"
POS_PATTERN = (
    r"(?:n|v|a|ad|adv|adj|conj|coll|prep|pron|p|phr|int|interj|"
    r"pref|suf|part|aux|imper|impers)"
)

HEAD_ATOM = rf"(?:['’][{LETTERS}]|[{UPPER}])[{LETTERS}'’\-]*"
ENTRY_RE = re.compile(
    rf"(?<![{LETTERS}\w])"
    rf"(?P<marker>[*†‡+/^\\]{{0,3}})\s*"
    rf"(?P<head>{HEAD_ATOM}(?:\s+[{LETTERS}'’\-]+){{0,6}})"
    rf"\s*(?:[!?])?\s*,?\s*"
    rf"(?:(?P<sense>\d+)\.\s*)?"
    rf"(?:(?P<gender>[{LETTERS}\^?]{{1,10}})\s*,\s*)?"
    rf"(?P<pos>{POS_PATTERN})\s*\.",
)

HEADER_WORDS = {
    "KHASI", "ENGLISH", "DICTIONARY", "NOTES", "PREFACE",
    "HINDI", "BENGALI", "ENGLISLI", "ENGLISH.",
}

POS_MAP = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "ad": "adverb",
    "adv": "adverb",
    "adj": "adjective",
    "conj": "conjunction",
    "coll": "conjunction",
    "prep": "preposition",
    "pron": "pronoun",
    "p": "pronoun",
    "phr": "phrase",
    "int": "interjection",
    "interj": "interjection",
    "pref": "prefix",
    "suf": "suffix",
    "part": "particle",
    "aux": "auxiliary",
    "imper": "imperative",
    "impers": "impersonal",
}

LOAN_MARKERS = {
    "*": "source-marked-loan-or-foreign",
    "†": "source-marked-loan-or-foreign",
    "‡": "source-marked-loan-or-foreign",
}


@dataclass
class Candidate:
    record_id: str
    headword_raw: str
    headword_candidate: str
    normalized: str
    language: str
    entry_type: str
    part_of_speech: str
    part_of_speech_raw: str
    gender_or_article_raw: str
    source_marker: str
    source_marker_interpretation: str
    historical_gloss_raw: str
    source_id: str
    source_year: str
    source_url: str
    source_line_start: str
    source_page_approx: str
    ocr_confidence: str
    review_priority: str
    duplicate_headword_pos_count: str
    existing_master: str
    verification_status: str
    human_review_required: str
    notes: str


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def compact_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def clean_headword(raw: str) -> str:
    value = compact_ws(nfc(raw))
    value = value.strip(" ,.;:")
    return value


def normalized_key(headword: str) -> str:
    return nfc(headword).casefold().strip()


def estimate_page(text: str, offset: int) -> int:
    formfeeds = text.count("\f", 0, offset)
    if formfeeds:
        return formfeeds + 1
    if not text:
        return 1
    return max(1, round((offset / len(text)) * 272))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def plausible_match(match: re.Match[str]) -> bool:
    head = clean_headword(match.group("head"))
    if not head or len(head) > 70:
        return False
    tokens = head.split()
    if len(tokens) > 7:
        return False
    if len(tokens) > 1 and len(tokens[0].strip("'’")) == 1:
        return False
    alpha = [ch for ch in head if ch.isalpha()]
    if len(alpha) < 1:
        return False
    if head.upper() in HEADER_WORDS:
        return False
    if len(tokens) > 1 and head.isupper():
        return False
    return True


def confidence_for(head: str, gloss: str, marker: str, pos: str) -> float:
    score = 0.45
    if len(head) <= 40:
        score += 0.10
    if re.fullmatch(rf"[{LETTERS}'’\- ]+", head):
        score += 0.10
    if pos in POS_MAP:
        score += 0.10
    if 3 <= len(gloss) <= 900:
        score += 0.10
    if head[:1].isupper() or head.startswith(("'", "’")):
        score += 0.05
    if len(head.split()) <= 4:
        score += 0.05
    if marker in LOAN_MARKERS or marker == "":
        score += 0.025
    if len(gloss) > 1800:
        score -= 0.15
    if any(ch.isdigit() for ch in head):
        score -= 0.25
    if re.search(r"[\[\]{}<>_=]", head):
        score -= 0.25
    if len(head.split()) > 5:
        score -= 0.05
    return max(0.0, min(1.0, score))


def priority_for(score: float) -> str:
    if score >= 0.90:
        return "1"
    if score >= 0.75:
        return "2"
    return "3"


def detect_entry_type(headword: str, pos: str) -> str:
    if " " in headword:
        return "phrase"
    if re.search(r"\b(.+?)[-\s]\1\b", headword, flags=re.IGNORECASE):
        return "reduplication"
    if "-" in headword:
        return "compound"
    if pos == "phrase":
        return "phrase"
    return "word"


def load_master_headwords(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            normalized_key(row.get("headword", ""))
            for row in csv.DictReader(handle)
            if row.get("headword")
        }


def locate_dictionary_body(text: str) -> str:
    probes = [
        "KHASI-ENGLISH DICTIONARY. A",
        "KHASI-ENGLISH DICTIONARY.\nA",
        "KHASI-ENGLISH DICTIONARY.  A",
    ]
    starts = [text.find(p) for p in probes if text.find(p) >= 0]
    if starts:
        start = max(starts)
        return text[start:]
    marker = "Abbreviations and Signs used in this Dictionary"
    idx = text.find(marker)
    if idx >= 0:
        return text[idx:]
    return text


def extract_candidates(
    text: str,
    source_url: str = DEFAULT_SOURCE_URL,
    master_headwords: set[str] | None = None,
) -> list[Candidate]:
    text = nfc(text.replace("\r\n", "\n").replace("\r", "\n"))
    body = locate_dictionary_body(text)
    body_offset = text.find(body)
    master_headwords = master_headwords or set()

    matches = [m for m in ENTRY_RE.finditer(body) if plausible_match(m)]
    prelim: list[dict[str, object]] = []

    for index, match in enumerate(matches):
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        gloss = compact_ws(body[match.end():next_start])
        if len(gloss) > 3000:
            gloss = gloss[:3000].rstrip() + " …"

        raw_head = clean_headword(match.group("head"))
        pos_raw = match.group("pos").lower()
        pos = POS_MAP.get(pos_raw, pos_raw)
        marker = match.group("marker") or ""
        gender = (match.group("gender") or "").strip()
        score = confidence_for(raw_head, gloss, marker, pos_raw)
        normalized = normalized_key(raw_head)
        absolute_offset = body_offset + match.start()

        prelim.append(
            {
                "raw_head": raw_head,
                "headword_candidate": raw_head.casefold(),
                "normalized": normalized,
                "pos": pos,
                "pos_raw": pos_raw,
                "gender": gender,
                "marker": marker,
                "gloss": gloss,
                "line": line_number(text, absolute_offset),
                "page": estimate_page(text, absolute_offset),
                "score": score,
            }
        )

    duplicate_counts = Counter((item["normalized"], item["pos"]) for item in prelim)

    result: list[Candidate] = []
    for idx, item in enumerate(prelim, start=1):
        headword = str(item["headword_candidate"])
        pos = str(item["pos"])
        duplicate_count = duplicate_counts[(item["normalized"], pos)]
        notes = [
            "Automatically extracted from the complete 1906 public-domain OCR.",
            "Historical spelling/meaning/POS must be checked against the scan and modern Khasi usage.",
        ]
        if duplicate_count > 1:
            notes.append("Repeated headword/POS in OCR; inspect for sense split, cross-reference, or OCR duplication.")
        if item["normalized"] in master_headwords:
            notes.append("Headword already exists in the KhasiLex master lexicon; update/review rather than duplicate.")
        if float(item["score"]) < 0.75:
            notes.append("Lower OCR confidence; inspect source image before lexical use.")

        result.append(
            Candidate(
                record_id=f"kha-n1906-{idx:06d}",
                headword_raw=str(item["raw_head"]),
                headword_candidate=headword,
                normalized=str(item["normalized"]),
                language="kha",
                entry_type=detect_entry_type(headword, pos),
                part_of_speech=pos,
                part_of_speech_raw=str(item["pos_raw"]),
                gender_or_article_raw=str(item["gender"]),
                source_marker=str(item["marker"]),
                source_marker_interpretation=LOAN_MARKERS.get(str(item["marker"]), ""),
                historical_gloss_raw=str(item["gloss"]),
                source_id=SOURCE_ID,
                source_year=str(SOURCE_YEAR),
                source_url=source_url,
                source_line_start=str(item["line"]),
                source_page_approx=str(item["page"]),
                ocr_confidence=f"{float(item['score']):.3f}",
                review_priority=priority_for(float(item["score"])),
                duplicate_headword_pos_count=str(duplicate_count),
                existing_master="yes" if item["normalized"] in master_headwords else "no",
                verification_status="pending",
                human_review_required="yes",
                notes=" ".join(notes),
            )
        )

    return result


def write_csv(path: Path, rows: list[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(Candidate.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_review_queue(path: Path, rows: list[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    best: dict[tuple[str, str], Candidate] = {}
    for row in rows:
        key = (row.normalized, row.part_of_speech)
        incumbent = best.get(key)
        if incumbent is None or float(row.ocr_confidence) > float(incumbent.ocr_confidence):
            best[key] = row

    selected = sorted(best.values(), key=lambda r: (int(r.review_priority), r.normalized, r.part_of_speech))
    fields = [
        "record_id", "headword_candidate", "normalized", "part_of_speech",
        "entry_type", "historical_gloss_raw", "source_page_approx",
        "ocr_confidence", "review_priority", "existing_master",
        "verification_status", "human_review_required",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in selected:
            data = asdict(row)
            writer.writerow({field: data[field] for field in fields})


def build_report(raw_bytes: bytes, rows: list[Candidate], source_url: str) -> dict[str, object]:
    unique_headwords = {row.normalized for row in rows}
    unique_headword_pos = {(row.normalized, row.part_of_speech) for row in rows}
    pos_counts = Counter(row.part_of_speech for row in rows)
    priority_counts = Counter(row.review_priority for row in rows)
    initial_counts = Counter(row.normalized[:1] for row in rows if row.normalized)
    return {
        "source_id": SOURCE_ID,
        "source_year": SOURCE_YEAR,
        "source_url": source_url,
        "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "source_bytes": len(raw_bytes),
        "parser_version": "1.0.0",
        "records_extracted": len(rows),
        "unique_headwords": len(unique_headwords),
        "unique_headword_pos_pairs": len(unique_headword_pos),
        "part_of_speech_counts": dict(sorted(pos_counts.items())),
        "review_priority_counts": dict(sorted(priority_counts.items())),
        "initial_character_counts": dict(sorted(initial_counts.items())),
        "pending_records": sum(row.verification_status == "pending" for row in rows),
        "existing_master_records": sum(row.existing_master == "yes" for row in rows),
        "low_confidence_records": sum(float(row.ocr_confidence) < 0.75 for row in rows),
        "policy": (
            "Historical OCR extraction only. No record is authoritative until "
            "modern Khasi human review and KhasiLex verification gates are complete."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract the complete U Nissor Singh 1906 Khasi-English OCR into a pending KhasiLex historical corpus."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--entries-output", required=True, type=Path)
    parser.add_argument("--review-output", required=True, type=Path)
    parser.add_argument("--report-output", required=True, type=Path)
    parser.add_argument("--master", type=Path)
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL)
    args = parser.parse_args()

    raw_bytes = args.input.read_bytes()
    text = raw_bytes.decode("utf-8", errors="replace")
    master = load_master_headwords(args.master)

    rows = extract_candidates(text, args.source_url, master)
    write_csv(args.entries_output, rows)
    write_review_queue(args.review_output, rows)

    report = build_report(raw_bytes, rows, args.source_url)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        f"NISSOR 1906 INGEST COMPLETE: {len(rows)} records, "
        f"{report['unique_headwords']} unique headwords, "
        f"{report['unique_headword_pos_pairs']} unique headword/POS pairs"
    )


if __name__ == "__main__":
    main()
