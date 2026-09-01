#!/usr/bin/env python3
"""Translate all reader editions from canonical English HTML in parallel.

The tool never translates PDFs.  It writes complete and ten-minute HTML reader
editions for every supported text language, preserves reader assets and Umami,
and removes the English-only PDF conversion notice and its source download.
It keeps bibliographic links to external PDF sources. It is
resumable: normal builds add only missing targets; use ``--force`` to replace
an existing translation after its English source has been revised.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from html import escape, unescape
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import content_index
from book_html import ANALYTICS, node_text, parse_body


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTENT_ROOT = REPO_ROOT / "docs" / "content"
HTML_ROOT = CONTENT_ROOT / "htmls"
TEN_MINUTE_ROOT = CONTENT_ROOT / "10minutes"
LANGUAGES = tuple(language for language in content_index.LANGUAGES if language != "EN")
LANGUAGE_TAGS = {
    "EN": "en",
    "RO": "ro",
    "PL": "pl",
    "IT": "it",
    "ES": "es",
    "PT": "pt",
    "DE": "de",
    "FR": "fr",
}
TRANSLATION_ENDPOINT = "https://translate.googleapis.com/translate_a/single"
CACHE_ROOT = Path(__file__).resolve().parent / ".translation-cache"
# The public endpoint accepts a little under 10 KB of URL-encoded source.  A
# larger chunk materially reduces requests while leaving room for punctuation
# expansion during encoding.
MAX_REQUEST_CHARS = 9_500
TAG_TOKEN_RE = re.compile(r"(<!--.*?-->|<[^>]+>)", re.DOTALL)
TAG_NAME_RE = re.compile(r"<\s*(/?)\s*([a-zA-Z][\w:-]*)\b[^>]*>")
IGNORED_TEXT_TAGS = {"code", "pre", "script", "style"}
WARNING_RE = re.compile(r"\s*<aside\b[^>]*\bdata-pdf-conversion-warning=[\"'][^\"']+[\"'][^>]*>.*?</aside>", re.IGNORECASE | re.DOTALL)
# Reader controls point back to the canonical local English PDF. Bibliographic
# PDF citations use external URLs and remain part of the translated text.
SOURCE_PDF_DOWNLOAD_RE = re.compile(r"\s*<a\b[^>]*\bhref=[\"'][^\"']*(?:\.\./|/)EN/[^\"']+\.pdf(?:[?#][^\"']*)?[\"'][^>]*>.*?</a>", re.IGNORECASE | re.DOTALL)
PDF_META_RE = re.compile(r"\s*<meta\b[^>]*\b(?:name|content)=[\"'](?:source-pdf|PDF Reflow conversion|Poppler XML hybrid conversion)[\"'][^>]*>", re.IGNORECASE)
REPAIR_META_RE = re.compile(r"\s*<meta\b[^>]*\bname=[\"']pdf-reflow-repair[\"'][^>]*>", re.IGNORECASE)
URL_ATTRIBUTE_RE = re.compile(r"(?P<name>\b(?:src|href))=(?P<quote>[\"'])(?P<url>.*?)(?P=quote)", re.IGNORECASE)


def split_text(text: str, maximum: int = MAX_REQUEST_CHARS) -> list[str]:
    """Split only oversized text nodes, preferring sentence boundaries."""
    if len(text) <= maximum:
        return [text]
    parts: list[str] = []
    remaining = text
    while len(remaining) > maximum:
        boundary = max(
            remaining.rfind(mark, 0, maximum)
            for mark in (". ", "! ", "? ", "; ", ": ", " ")
        )
        if boundary <= 0:
            boundary = maximum
        else:
            boundary += 1
        parts.append(remaining[:boundary])
        remaining = remaining[boundary:]
    if remaining:
        parts.append(remaining)
    return parts


class GoogleWebTranslator:
    """Small, dependency-free client for the public Google web translator."""

    def __init__(self, language: str, source_language: str = "EN") -> None:
        self.language = LANGUAGE_TAGS[language]
        self.source_language = LANGUAGE_TAGS[source_language]

    def translate(self, text: str) -> str:
        if not text.strip() or not any(character.isalpha() for character in text):
            return text
        translated = []
        for part in split_text(text):
            translated.append(self._translate_part(part))
        return "".join(translated)

    def _translate_part(self, text: str) -> str:
        digest = hashlib.sha256(f"{self.source_language}:{self.language}:{text}".encode("utf-8")).hexdigest()
        cache_path = CACHE_ROOT / self.source_language / self.language / f"{digest}.txt"
        if cache_path.is_file():
            return cache_path.read_text(encoding="utf-8")
        query = urlencode(
            [("client", "gtx"), ("sl", self.source_language), ("tl", self.language), ("dt", "t"), ("q", text)],
            quote_via=quote,
        )
        request = Request(f"{TRANSLATION_ENDPOINT}?{query}", headers={"User-Agent": "Axiologic reader translation builder/1.0"})
        last_error: Exception | None = None
        for attempt in range(5):
            try:
                with urlopen(request, timeout=45) as response:  # nosec B310: fixed HTTPS endpoint above
                    payload = json.loads(response.read().decode("utf-8"))
                translated = "".join(segment[0] for segment in payload[0] if segment and segment[0])
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(translated, encoding="utf-8")
                return translated
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, IndexError, TypeError) as error:
                last_error = error
                if attempt == 4:
                    break
                time.sleep(2**attempt)
        raise RuntimeError(f"translation request failed for {self.language}: {last_error}")


def output_name(book: dict[str, object], english_html: Path, language: str) -> str:
    alias = content_index.EDITION_ALIASES.get((str(book["id"]), language))
    stem = re.sub(r"_[A-Z]{2}$", "", english_html.stem)
    return f"{alias or stem}_{language}.html"


def full_destination(book: dict[str, object], english_html: Path, language: str) -> Path:
    if language == "EN":
        return HTML_ROOT / "EN" / f"{book['id']}.html"
    stem = re.sub(r"_[A-Z]{2}$", "", english_html.stem)
    existing = content_index.find_edition_html(CONTENT_ROOT, language, stem, str(book["id"]))
    return existing or HTML_ROOT / language / output_name(book, english_html, language)


def reader_targets(languages: set[str] | None = None) -> list[tuple[dict[str, object], Path, Path | None, Path, Path, str, str]]:
    """Return full and short source/target records for all public books."""
    records = []
    for book in content_index.discover_books():
        english = next((edition for edition in book["editions"] if edition["language"] == "EN"), None)
        if english:
            source_language = "EN"
            source_full = CONTENT_ROOT / str(english["html"])
            source_short = CONTENT_ROOT / str(english["tenMinuteHtml"])
            target_languages = LANGUAGES
        else:
            source_language = content_index.TEXT_ONLY_BOOK_SOURCES.get(str(book["id"]))
            if source_language is None:
                raise ValueError(f"no English or declared text source for {book['id']}")
            source = next((edition for edition in book["editions"] if edition["language"] == source_language), None)
            if source is None:
                raise ValueError(f"missing declared {source_language} source for {book['id']}")
            source_full = CONTENT_ROOT / str(source["html"])
            source_short = None
            target_languages = ("EN", *LANGUAGES)
        for language in target_languages:
            if languages is not None and language not in languages:
                continue
            translated_full = full_destination(book, source_full, language)
            translated_short = (TEN_MINUTE_ROOT / translated_full.name) if language == "EN" else (TEN_MINUTE_ROOT / language / translated_full.name)
            records.append((book, source_full, source_short, translated_full, translated_short, language, source_language))
    return records


def rebase_local_urls(source: str, destination: str, source_path: Path, destination_path: Path, full_paths: dict[Path, Path]) -> str:
    """Keep CSS, JS, figures, and translated full-reader links valid after a move."""
    def replace(match: re.Match[str]) -> str:
        value = match.group("url")
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or value.startswith(("/", "#", "data:")):
            return match.group(0)
        try:
            original = (source_path.parent / unescape(parsed.path)).resolve()
        except (OSError, ValueError):
            return match.group(0)
        target = full_paths.get(original, original)
        try:
            relative = os.path.relpath(target, destination_path.parent).replace(os.sep, "/")
        except ValueError:
            return match.group(0)
        rewritten = urlunsplit(("", "", relative, parsed.query, parsed.fragment))
        return f'{match.group("name")}={match.group("quote")}{escape(rewritten, quote=True)}{match.group("quote")}'

    return URL_ATTRIBUTE_RE.sub(replace, source)


def strip_english_pdf_material(source: str) -> str:
    source = WARNING_RE.sub("", source)
    source = SOURCE_PDF_DOWNLOAD_RE.sub("", source)
    source = PDF_META_RE.sub("", source)
    return REPAIR_META_RE.sub("", source)


def set_document_language(source: str, language: str) -> str:
    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        tag = re.sub(r"\s+lang=[\"'][^\"']*[\"']", "", tag, flags=re.IGNORECASE)
        return tag[:-1] + f' lang="{LANGUAGE_TAGS[language]}">'

    return re.sub(r"<html\b[^>]*>", replace, source, count=1, flags=re.IGNORECASE)


def short_excerpt_source(source: str) -> str:
    """Create a compact reader excerpt for a declared text-only source."""
    document = strip_english_pdf_material(source)
    parser = parse_body(document)
    selected: list[str] = []
    words = 0
    for node in parser.nodes:
        if node.tag in {"aside", "script"}:
            continue
        selected.append(node.raw(document))
        words += len(re.findall(r"[\w’'-]+", node_text(node, document)))
        if words >= 1_150:
            break
    head = re.search(r"<head\b[^>]*>(.*?)</head>", document, re.IGNORECASE | re.DOTALL)
    if head is None:
        raise ValueError("text-only reader has no head")
    title = re.search(r"<title>(.*?)</title>", head.group(1), re.IGNORECASE | re.DOTALL)
    title_text = unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip() if title else "Axiologic Reader"
    return f"""<!doctype html>
<html><head>{head.group(1)}</head><body class="pdf-reflow">
<header class="ten-minute-header"><p class="ten-minute-kicker">10-minute excerpt</p><h1>{escape(title_text)}</h1><p>About 10 minutes</p></header>
<main>{''.join(selected)}</main><script defer src="../../../reader/standalone.js"></script></body></html>"""


def translate_markup(source: str, translate: Callable[[str], str]) -> str:
    """Translate HTML text nodes while preserving every tag and reader asset."""
    result: list[str] = []
    stack: list[str] = []
    for token in TAG_TOKEN_RE.split(source):
        if not token:
            continue
        if token.startswith("<"):
            result.append(token)
            match = TAG_NAME_RE.match(token)
            if not match or token.startswith("<!--"):
                continue
            closing, name = match.groups()
            name = name.lower()
            if closing:
                for index in range(len(stack) - 1, -1, -1):
                    if stack[index] == name:
                        del stack[index:]
                        break
            elif not token.rstrip().endswith("/>") and name not in {"meta", "link", "img", "br", "hr", "input", "source"}:
                stack.append(name)
            continue
        if any(tag in IGNORED_TEXT_TAGS for tag in stack):
            result.append(token)
            continue
        whitespace = re.match(r"^(\s*)(.*?)(\s*)$", token, re.DOTALL)
        assert whitespace is not None
        prefix, text, suffix = whitespace.groups()
        if not text or not any(character.isalpha() for character in unescape(text)):
            result.append(token)
            continue
        result.append(prefix + escape(translate(unescape(text)), quote=False) + suffix)
    return "".join(result)


def validate_translation(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    head = re.search(r"<head\b[^>]*>(.*?)</head>", source, re.IGNORECASE | re.DOTALL)
    problems = []
    if source.count(ANALYTICS) != 1 or head is None or head.group(1).count(ANALYTICS) != 1:
        problems.append("analytics must occur exactly once in head")
    if "standalone.css" not in source or "standalone.js" not in source:
        problems.append("standalone reader assets are missing")
    if "data-pdf-conversion-warning" in source:
        problems.append("English PDF conversion warning remains")
    if SOURCE_PDF_DOWNLOAD_RE.search(source):
        problems.append("English PDF download link remains")
    return problems


def build(force: bool, jobs: int, selected: set[str] | None, languages: set[str] | None, rebuild_index: bool) -> int:
    targets = [record for record in reader_targets(languages) if selected is None or record[0]["id"] in selected]
    tasks: list[tuple[Path, Path, str, str, bool, Path, Path]] = []
    for _, source_full, source_short, destination_full, destination_short, language, source_language in targets:
        tasks.append((source_full, destination_full, language, source_language, False, source_full, destination_full))
        tasks.append((source_short or source_full, destination_short, language, source_language, source_short is None, source_full, destination_full))
    pending = [task for task in tasks if force or not task[1].is_file()]
    if not pending:
        print("All requested translated reader editions already exist.")
        return 0

    def translate_one(task: tuple[Path, Path, str, str, bool, Path, Path]) -> Path:
        source_path, destination_path, language, source_language, make_excerpt, source_full, destination_full = task
        source = source_path.read_text(encoding="utf-8")
        source = short_excerpt_source(source) if make_excerpt else strip_english_pdf_material(source)
        source = rebase_local_urls(source, str(source_path), source_path, destination_path, {source_full: destination_full})
        source = set_document_language(source, language)
        translated = translate_markup(source, GoogleWebTranslator(language, source_language).translate)
        problems = validate_translation_source(translated)
        if problems:
            raise ValueError(f"{destination_path.relative_to(REPO_ROOT)}: {'; '.join(problems)}")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(translated, encoding="utf-8")
        return destination_path

    failures = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {executor.submit(translate_one, task): task for task in pending}
        for future in as_completed(futures):
            task = futures[future]
            try:
                destination = future.result()
                print(f"Translated {destination.relative_to(REPO_ROOT)}")
            except Exception as error:  # keep successful documents when a provider rate-limits one request
                failures.append(f"{task[1].relative_to(REPO_ROOT)}: {error}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    if rebuild_index:
        rebuild_content_index()
    print(f"Translated {len(pending)} reader files across {len(languages or LANGUAGES)} languages.")
    return 0


def validate_translation_source(source: str) -> list[str]:
    head = re.search(r"<head\b[^>]*>(.*?)</head>", source, re.IGNORECASE | re.DOTALL)
    problems = []
    if source.count(ANALYTICS) != 1 or head is None or head.group(1).count(ANALYTICS) != 1:
        problems.append("analytics must occur exactly once in head")
    if "standalone.css" not in source or "standalone.js" not in source:
        problems.append("standalone reader assets are missing")
    if "data-pdf-conversion-warning" in source:
        problems.append("English PDF conversion warning remains")
    if SOURCE_PDF_DOWNLOAD_RE.search(source):
        problems.append("English PDF download link remains")
    return problems


def rebuild_content_index() -> None:
    """Publish new reader editions through the public content manifest."""
    content_index.INDEX_PATH.write_text(content_index.serialize(), encoding="utf-8")
    content_index.INDEX_SCRIPT_PATH.write_text(content_index.serialize_script(), encoding="utf-8")


def check(selected: set[str] | None, languages: set[str] | None) -> int:
    problems = []
    for book, source_full, source_short, destination_full, destination_short, language, source_language in reader_targets(languages):
        if selected is not None and book["id"] not in selected:
            continue
        for destination in (destination_full, destination_short):
            if not destination.is_file():
                problems.append(f"missing {destination.relative_to(REPO_ROOT)}")
                continue
            problems.extend(f"{destination.relative_to(REPO_ROOT)}: {problem}" for problem in validate_translation(destination))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print("All requested complete and ten-minute translations are present and valid.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    parser.add_argument("--book", action="append", dest="books", help="book ID to process (repeatable)")
    parser.add_argument(
        "--language",
        action="append",
        dest="languages",
        choices=(*LANGUAGES, "EN"),
        help="language to process (repeatable; defaults to every translated language)",
    )
    parser.add_argument("--force", action="store_true", help="replace reviewed translations with a fresh machine translation")
    parser.add_argument("--jobs", type=int, default=8, help="parallel document translations (default: 8)")
    parser.add_argument("--no-index", action="store_true", help="do not rebuild the public content index (for parallel workers)")
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    selected = set(args.books) if args.books else None
    languages = set(args.languages) if args.languages else None
    if args.command == "check":
        return check(selected, languages)
    return build(args.force, args.jobs, selected, languages, not args.no_index)


if __name__ == "__main__":
    raise SystemExit(main())
