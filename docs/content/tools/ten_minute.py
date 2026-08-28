#!/usr/bin/env python3
"""Build editorial ten-minute syntheses for every English PDF edition."""

from __future__ import annotations

import argparse
from html import escape, unescape
import json
from math import ceil
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTENT_ROOT = REPO_ROOT / "docs" / "content"
SOURCE_DIRECTORY = CONTENT_ROOT / "htmls" / "EN"
OUTPUT_DIRECTORY = CONTENT_ROOT / "10minutes"
SUMMARY_DIRECTORY = CONTENT_ROOT / "tools" / "ten_minute_summaries"
MIN_SUMMARY_WORDS = 1_000
MAX_SUMMARY_WORDS = 1_500
MIN_SHORT_WORDS = 18
MAX_LISTING_WORDS = 60
MAX_HOOK_WORDS = 75
FINAL_HEADING = "Why read the complete book"
TITLE_SUFFIX = ": A 10-Minute Synthesis"
HOOK_META_LANGUAGE = re.compile(r"\b(?:this|the)\s+(?:guide|overview|summary)\b", re.IGNORECASE)
HEADING = re.compile(r"<h([1-6])(?:\s[^>]*)?>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
OPENING_TEN_MINUTE = re.compile(r"\b(?:ten|10)[ -]?minutes?\b", re.IGNORECASE)
OPENING_NUMBERED_CHAPTER = re.compile(r"^(?:chapter\s+(?:1|one)\b|1(?:[.):]|\s))", re.IGNORECASE)
TAG = re.compile(r"<[^>]+>")


def words(value: str) -> list[str]:
    return re.findall(r"[\w’'-]+", value)


def encoded(relative: Path) -> str:
    return quote(relative.as_posix(), safe="/")


def targets() -> list[tuple[Path, Path, Path]]:
    pairs = []
    for pdf in sorted((CONTENT_ROOT / "EN").glob("*.pdf")):
        source = SOURCE_DIRECTORY / pdf.with_suffix(".html").name
        if not source.is_file():
            raise FileNotFoundError(f"missing English reflow edition for {pdf.relative_to(CONTENT_ROOT)}")
        pairs.append((pdf, source, OUTPUT_DIRECTORY / pdf.with_suffix(".html").name))
    return pairs


def summary_path(book_id: str) -> Path:
    return SUMMARY_DIRECTORY / f"{book_id}.json"


def summary_word_count(summary: dict[str, Any]) -> int:
    return sum(len(words(paragraph)) for section in summary["sections"] for paragraph in section["paragraphs"])


def plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(TAG.sub(" ", value))).strip()


def source_headings(source: str) -> list[tuple[re.Match[str], str]]:
    return [(match, plain_text(match.group(2))) for match in HEADING.finditer(source)]


def opening_ten_minute_heading(source: str) -> str | None:
    """Return an explicitly labelled short opening chapter, when present."""
    for index, (_, heading) in enumerate(source_headings(source)):
        if OPENING_TEN_MINUTE.search(heading) and (index < 12 or OPENING_NUMBERED_CHAPTER.search(heading)):
            return heading
    return None


def extract_source_excerpt(source: str, excerpt: dict[str, str]) -> str:
    headings = source_headings(source)
    start_heading = excerpt["start_heading"]
    end_heading = excerpt["end_heading"]
    start_index = next((index for index, (_, heading) in enumerate(headings) if heading == start_heading), None)
    if start_index is None:
        raise ValueError(f"opening chapter start heading not found: {start_heading!r}")
    end_match = next(
        (match for match, heading in headings[start_index + 1 :] if heading == end_heading),
        None,
    )
    if end_match is None:
        raise ValueError(f"opening chapter end heading not found after start: {end_heading!r}")
    start_match = headings[start_index][0]
    content = source[start_match.start() : end_match.start()].strip()
    if len(words(plain_text(content))) < 500:
        raise ValueError(f"opening chapter excerpt is unexpectedly short: {start_heading!r}")
    return re.sub(
        r'(?P<attribute>src|href)="(?P<url>(?![a-z]+:|/|#)[^"]+)"',
        lambda match: f'{match.group("attribute")}="../htmls/EN/{match.group("url")}"',
        content,
        flags=re.IGNORECASE,
    )


def validate_summary(summary: Any, expected_id: str | None = None) -> list[str]:
    problems: list[str] = []
    if not isinstance(summary, dict):
        return ["summary must be a JSON object"]

    is_source_excerpt = "source_excerpt" in summary
    required = {"id", "title", "listing_description", "reader_hook", "source_excerpt" if is_source_excerpt else "sections"}
    missing = required - set(summary)
    extra = set(summary) - required
    if missing:
        problems.append(f"missing fields: {', '.join(sorted(missing))}")
    if extra:
        problems.append(f"unexpected fields: {', '.join(sorted(extra))}")
    if problems:
        return problems

    book_id = summary["id"]
    if not isinstance(book_id, str) or not book_id:
        problems.append("id must be a non-empty string")
    elif expected_id is not None and book_id != expected_id:
        problems.append(f"id is {book_id!r}, expected {expected_id!r}")

    for field, maximum in (("listing_description", MAX_LISTING_WORDS), ("reader_hook", MAX_HOOK_WORDS)):
        value = summary[field]
        if not isinstance(value, str):
            problems.append(f"{field} must be a string")
            continue
        count = len(words(value))
        if count < MIN_SHORT_WORDS or count > maximum:
            problems.append(f"{field} has {count} words; expected {MIN_SHORT_WORDS}-{maximum}")
    if isinstance(summary["reader_hook"], str) and HOOK_META_LANGUAGE.search(summary["reader_hook"]):
        problems.append("reader_hook must invite readers into the book, not mention a guide, overview or summary")

    if not isinstance(summary["title"], str) or not summary["title"].strip():
        problems.append("title must be a non-empty string")
    elif not is_source_excerpt and not summary["title"].endswith(TITLE_SUFFIX):
        problems.append(f"title must end with {TITLE_SUFFIX!r}")

    if is_source_excerpt:
        excerpt = summary["source_excerpt"]
        if not isinstance(excerpt, dict) or set(excerpt) != {"start_heading", "end_heading"}:
            problems.append("source_excerpt must contain only start_heading and end_heading")
        elif any(not isinstance(excerpt[field], str) or not excerpt[field].strip() for field in excerpt):
            problems.append("source_excerpt headings must be non-empty strings")
        return problems

    sections = summary["sections"]
    if not isinstance(sections, list) or not 6 <= len(sections) <= 9:
        problems.append("sections must contain 6-9 thematic sections")
        return problems
    for index, section in enumerate(sections, start=1):
        if not isinstance(section, dict) or set(section) != {"heading", "paragraphs"}:
            problems.append(f"section {index} must contain only heading and paragraphs")
            continue
        if not isinstance(section["heading"], str) or not section["heading"].strip():
            problems.append(f"section {index} has no heading")
        paragraphs = section["paragraphs"]
        if not isinstance(paragraphs, list) or not paragraphs:
            problems.append(f"section {index} has no paragraphs")
        elif any(not isinstance(paragraph, str) or not paragraph.strip() for paragraph in paragraphs):
            problems.append(f"section {index} contains an empty or invalid paragraph")
    if isinstance(sections[-1], dict) and sections[-1].get("heading") != FINAL_HEADING:
        problems.append(f"final section must be titled {FINAL_HEADING!r}")

    if not problems:
        count = summary_word_count(summary)
        if count < MIN_SUMMARY_WORDS or count > MAX_SUMMARY_WORDS:
            problems.append(f"synthesis has {count} words; expected {MIN_SUMMARY_WORDS}-{MAX_SUMMARY_WORDS}")
    return problems


def load_summary(book_id: str) -> dict[str, Any]:
    path = summary_path(book_id)
    if not path.is_file():
        raise FileNotFoundError(f"missing editorial source {path.relative_to(REPO_ROOT)}")
    summary = json.loads(path.read_text(encoding="utf-8"))
    problems = validate_summary(summary, book_id)
    if problems:
        raise ValueError(f"invalid {path.relative_to(REPO_ROOT)}: {'; '.join(problems)}")
    return summary


def render(pdf: Path, source: Path, destination: Path) -> str:
    del destination
    summary = load_summary(pdf.stem)
    title = summary["title"]
    source_html = source.read_text(encoding="utf-8")
    original_heading = opening_ten_minute_heading(source_html)
    is_source_excerpt = "source_excerpt" in summary
    if original_heading and not is_source_excerpt:
        raise ValueError(
            f"{pdf.name} begins with {original_heading!r}; use its original chapter through source_excerpt"
        )
    book_title = title if is_source_excerpt else title.removesuffix(TITLE_SUFFIX)
    full_html = encoded(Path("..") / "htmls" / "EN" / source.name)
    original_pdf = encoded(Path("..") / "EN" / pdf.name)

    if is_source_excerpt:
        body = extract_source_excerpt(source_html, summary["source_excerpt"])
        word_count = len(words(plain_text(body)))
        reading_minutes = max(1, ceil(word_count / 200))
        document_description = f"The original opening chapter of {book_title}."
        document_title = f"{book_title} · original opening chapter"
        kicker = "Original opening chapter"
        reading_note = f"Author’s original text · About {reading_minutes} minutes · {word_count:,} words"
    else:
        sections = []
        for section in summary["sections"]:
            paragraphs = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in section["paragraphs"])
            sections.append(f"<section><h2>{escape(section['heading'])}</h2>{paragraphs}</section>")
        body = "".join(sections)
        word_count = summary_word_count(summary)
        reading_minutes = 10
        document_description = f"A ten-minute synthesis of {book_title}."
        document_title = f"{book_title} · 10-minute synthesis"
        kicker = "10-minute synthesis"
        reading_note = f"About 10 minutes · {word_count:,} words"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(document_description, quote=True)}">
  <meta name="reading-time" content="{reading_minutes} minutes">
  <meta name="source-pdf" content="{escape(pdf.name, quote=True)}">
  <title>{escape(document_title)}</title>
  <link rel="stylesheet" href="../../reader/standalone.css?v=20260828-1">
  <style>
    .ten-minute-header {{ margin-bottom: 2.4rem; padding-bottom: 1.5rem; border-bottom: 1px solid color-mix(in srgb, currentColor 22%, transparent); }}
    .ten-minute-header p {{ text-indent: 0; text-align: left; }}
    .ten-minute-kicker {{ color: var(--standalone-link); font: 700 .78em/1.2 system-ui, sans-serif; letter-spacing: .12em; text-transform: uppercase; }}
    .ten-minute-links {{ display: flex; flex-wrap: wrap; gap: .8rem 1.1rem; margin-top: 1.2rem; font-family: system-ui, sans-serif; font-size: .82em; }}
  </style>
  <script defer src="https://cloud.umami.is/script.js" data-website-id="e252999d-4479-42d7-9526-5f778846d4f6"></script>
</head>
<body>
  <header class="ten-minute-header">
    <p class="ten-minute-kicker">{escape(kicker)}</p>
    <h1>{escape(title)}</h1>
    <p>{escape(reading_note)}</p>
    <nav class="ten-minute-links" aria-label="Edition links"><a href="{full_html}">Read the full HTML edition</a><a href="{original_pdf}">Download the original PDF</a></nav>
  </header>
  <main>
    {body}
  </main>
  <script defer src="../../reader/standalone.js?v=20260827-1"></script>
</body>
</html>
"""


def build(available_only: bool = False) -> int:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    built = 0
    for pdf, source, destination in targets():
        if available_only and not summary_path(pdf.stem).is_file():
            continue
        destination.write_text(render(pdf, source, destination), encoding="utf-8")
        built += 1
    qualifier = " available" if available_only else ""
    print(f"Built {built}{qualifier} editorial ten-minute syntheses in {OUTPUT_DIRECTORY.relative_to(REPO_ROOT)}.")
    return 0


def check() -> int:
    problems = []
    for pdf, source, destination in targets():
        try:
            expected = render(pdf, source, destination)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
            problems.append(str(error))
            continue
        if not destination.is_file():
            problems.append(f"missing {destination.relative_to(REPO_ROOT)}")
        elif destination.read_text(encoding="utf-8") != expected:
            problems.append(f"stale {destination.relative_to(REPO_ROOT)}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"Editorial ten-minute syntheses are current ({len(targets())} files).")
    return 0


def import_batch(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summaries = payload.get("summaries") if isinstance(payload, dict) else None
    if not isinstance(summaries, list) or not summaries:
        raise ValueError("batch must contain a non-empty summaries array")
    for summary in summaries:
        if isinstance(summary, dict) and isinstance(summary.get("title"), str):
            summary["title"] = summary["title"].replace(
                ": A 10-Minute Reading Guide", TITLE_SUFFIX
            )
    known_ids = {pdf.stem for pdf, _, _ in targets()}
    failures = []
    for summary in summaries:
        book_id = summary.get("id", "<missing>") if isinstance(summary, dict) else "<invalid>"
        issues = validate_summary(summary)
        if book_id not in known_ids:
            issues.append(f"id {book_id!r} does not match an English PDF")
        if issues:
            failures.append(f"{book_id}: {'; '.join(issues)}")
    if failures:
        raise ValueError("\n".join(failures))

    SUMMARY_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for summary in summaries:
        destination = summary_path(summary["id"])
        destination.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Imported {destination.relative_to(REPO_ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "build-available", "check", "import"))
    parser.add_argument("path", nargs="?", type=Path, help="JSON batch to import")
    args = parser.parse_args(argv)
    if args.command == "import":
        if args.path is None:
            parser.error("import requires a JSON batch path")
        return import_batch(args.path)
    if args.path is not None:
        parser.error(f"{args.command} does not accept a path")
    if args.command == "build-available":
        return build(available_only=True)
    return build() if args.command == "build" else check()


if __name__ == "__main__":
    raise SystemExit(main())
