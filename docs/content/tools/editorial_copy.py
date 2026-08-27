#!/usr/bin/env python3
"""Synchronize reviewed short editorial copy with book cards and book pages."""

from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys

import content_index


REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_ROOT = REPO_ROOT / "docs"
CONTENT_ROOT = DOCS_ROOT / "content"
SUMMARY_DIRECTORY = CONTENT_ROOT / "tools" / "ten_minute_summaries"
BOOKS_SCRIPT = DOCS_ROOT / "assets" / "js" / "books.js"


def js_string(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029") + "'"


def object_spans(source: str) -> list[tuple[int, int]]:
    array_start = source.index("[", source.index("const books"))
    spans = []
    depth = 0
    start = None
    quote = None
    escaped = False
    for index in range(array_start + 1, len(source)):
        character = source[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"', "`"}:
            quote = character
        elif character == "{":
            if depth == 0:
                start = index
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0 and start is not None:
                spans.append((start, index + 1))
                start = None
        elif character == "]" and depth == 0:
            break
    return spans


def property_value(block: str, name: str) -> str | None:
    match = re.search(rf"\b{name}:\s*'((?:\\.|[^'\\])*)'", block)
    if not match:
        return None
    return match.group(1).replace("\\'", "'").replace("\\\\", "\\")


def load_summaries() -> dict[str, dict[str, object]]:
    summaries = {}
    for path in sorted(SUMMARY_DIRECTORY.glob("*.json")):
        summary = json.loads(path.read_text(encoding="utf-8"))
        summaries[summary["id"]] = summary
    return summaries


def expected_books_script(source: str, summaries: dict[str, dict[str, object]]) -> tuple[str, set[str]]:
    replacements = []
    matched = set()
    for start, end in object_spans(source):
        block = source[start:end]
        book_id = property_value(block, "fileId") or property_value(block, "id")
        if book_id not in summaries:
            continue
        description = summaries[book_id]["listing_description"]
        updated, count = re.subn(
            r"(\bdescription:\s*)'(?:\\.|[^'\\])*'",
            lambda match: match.group(1) + js_string(str(description)),
            block,
            count=1,
        )
        if count != 1:
            raise ValueError(f"book object {book_id!r} has no unique description")
        replacements.append((start, end, updated))
        matched.add(book_id)
    for start, end, updated in reversed(replacements):
        source = source[:start] + updated + source[end:]
    return source, matched


def update_meta(source: str, attribute: str, value: str, text: str) -> str:
    pattern = rf'(<meta\s+{attribute}="{re.escape(value)}"\s+content=")[^"]*(")'
    return re.sub(pattern, lambda match: match.group(1) + escape(text, quote=True) + match.group(2), source, count=1)


def expected_page(source: str, hook: str) -> str:
    updated, count = re.subn(
        r'(<p\s+class="edition-why">).*?(</p>)',
        lambda match: match.group(1) + escape(hook) + match.group(2),
        source,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError("page has no unique edition-why paragraph")
    updated = update_meta(updated, "name", "description", hook)
    updated = update_meta(updated, "property", "og:description", hook)
    return updated


def page_map() -> dict[str, Path]:
    result = {}
    for book in content_index.discover_books():
        english = next((edition for edition in book["editions"] if edition["language"] == "EN"), None)
        if english:
            result[Path(english["pdf"]).stem] = DOCS_ROOT / "books" / book["slug"] / "index.html"
    return result


def synchronize(write: bool) -> int:
    summaries = load_summaries()
    if not summaries:
        raise ValueError("no editorial summaries found")

    source = BOOKS_SCRIPT.read_text(encoding="utf-8")
    expected, matched = expected_books_script(source, summaries)
    problems = []
    if matched != set(summaries):
        problems.append(f"books.js has no matching object for: {', '.join(sorted(set(summaries) - matched))}")
    if source != expected:
        if write:
            BOOKS_SCRIPT.write_text(expected, encoding="utf-8")
        else:
            problems.append(f"stale {BOOKS_SCRIPT.relative_to(REPO_ROOT)}")

    pages = page_map()
    for book_id, summary in summaries.items():
        page = pages.get(book_id)
        if page is None:
            problems.append(f"no book page for {book_id}")
            continue
        current = page.read_text(encoding="utf-8")
        expected_page_source = expected_page(current, str(summary["reader_hook"]))
        if current != expected_page_source:
            if write:
                page.write_text(expected_page_source, encoding="utf-8")
            else:
                problems.append(f"stale {page.relative_to(REPO_ROOT)}")

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    action = "Synchronized" if write else "Editorial copy is current for"
    print(f"{action} {len(summaries)} English books.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    args = parser.parse_args(argv)
    return synchronize(args.command == "build")


if __name__ == "__main__":
    raise SystemExit(main())
