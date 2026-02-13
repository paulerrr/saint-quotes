#!/usr/bin/env python3
"""Extract quote records from 'A Dictionary of Quotes from the Saints' PDF.

Usage:
  python scripts/extract_saint_quotes.py \
    --pdf "A Dictionary of Quotes From th - Thigpen, Paul_6247.pdf" \
    --outdir output
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


UPPER_TOPIC_RE = re.compile(r"^[A-Z0-9 ,;:&'()\-\u2014]+$")
SEE_ALSO_TOPIC_RE = re.compile(
    r"^([A-Z0-9 ,;:&'()\-]+)\s*[—-]\s*See also\b.*$",
    re.IGNORECASE,
)
AUTHOR_RE = re.compile(
    r"^[A-Z][A-Za-z'\-]+(?: [A-Za-z][A-Za-z'\-]+){1,6}$"
)
CONNECTORS = {
    "of",
    "the",
    "de",
    "da",
    "del",
    "di",
    "la",
    "le",
    "van",
    "von",
}


@dataclass
class QuoteRecord:
    id: int
    topic: str
    quote: str
    author: str
    page: int
    source_title: str
    source_file: str


def looks_like_topic(line: str) -> bool:
    if not line:
        return False
    if len(line) > 120:
        return False
    if not UPPER_TOPIC_RE.match(line):
        return False
    return any(c.isalpha() for c in line)


def extract_topic(line: str) -> str | None:
    if looks_like_topic(line):
        return line

    match = SEE_ALSO_TOPIC_RE.match(line)
    if match:
        return match.group(1).strip()

    return None


def looks_like_author(line: str) -> bool:
    if not line:
        return False
    if line.isupper():
        return False
    if len(line) > 80:
        return False
    if not AUTHOR_RE.match(line):
        return False

    words = line.split()
    if len(words) < 2:
        return False
    if words[-1].lower() in CONNECTORS:
        return False

    for w in words:
        low = w.lower()
        if low in CONNECTORS:
            continue
        if not (w[0].isupper() and any(ch.isalpha() for ch in w)):
            return False
    return True


def split_inline_author_prefix(line: str) -> tuple[str, str] | None:
    words = line.split()
    if len(words) < 3:
        return None

    max_author_words = min(7, len(words) - 1)
    for author_word_count in range(max_author_words, 1, -1):
        author = " ".join(words[:author_word_count])
        remainder = " ".join(words[author_word_count:]).strip()
        if not remainder:
            continue
        if looks_like_author(author) and remainder[0].isupper():
            return author, remainder
    return None


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_quotes(pdf_path: Path, source_title: str) -> list[QuoteRecord]:
    reader = PdfReader(str(pdf_path))
    records: list[QuoteRecord] = []

    topic = ""
    quote_lines: list[str] = []
    quote_page = 0

    def flush(author: str) -> None:
        nonlocal quote_lines, quote_page
        quote = normalize_ws(" ".join(quote_lines))
        if quote and topic and author:
            records.append(
                QuoteRecord(
                    id=len(records) + 1,
                    topic=topic,
                    quote=quote,
                    author=author,
                    page=quote_page,
                    source_title=source_title,
                    source_file=pdf_path.name,
                )
            )
        quote_lines = []
        quote_page = 0

    for page_idx, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        lines = [ln.strip() for ln in raw.splitlines()]

        for line in lines:
            if not line:
                continue

            parsed_topic = extract_topic(line)
            if parsed_topic:
                topic = parsed_topic
                continue

            if looks_like_author(line):
                if quote_lines:
                    flush(line)
                continue

            if quote_lines:
                inline_author = split_inline_author_prefix(line)
                if inline_author:
                    author, remainder = inline_author
                    flush(author)
                    quote_page = page_idx
                    quote_lines.append(remainder)
                    continue

            if not quote_lines:
                quote_page = page_idx
            quote_lines.append(line)

    return records


def write_outputs(records: list[QuoteRecord], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    json_path = outdir / "saint_quotes.json"
    csv_path = outdir / "saint_quotes.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in records], f, indent=2, ensure_ascii=False)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "topic",
                "quote",
                "author",
                "page",
                "source_title",
                "source_file",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--outdir", default=Path("output"), type=Path)
    parser.add_argument(
        "--source-title",
        default="A Dictionary of Quotes from the Saints",
    )
    args = parser.parse_args()

    records = extract_quotes(args.pdf, args.source_title)
    write_outputs(records, args.outdir)

    print(f"Extracted {len(records)} quote records")
    print(f"JSON: {args.outdir / 'saint_quotes.json'}")
    print(f"CSV : {args.outdir / 'saint_quotes.csv'}")


if __name__ == "__main__":
    main()
