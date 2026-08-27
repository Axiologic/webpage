#!/usr/bin/env python3
"""Build or verify the deterministic inventory for ``docs/content``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTENT_ROOT = REPO_ROOT / "docs" / "content"
INDEX_PATH = CONTENT_ROOT / "index.json"
INDEX_SCRIPT_PATH = CONTENT_ROOT / "index.js"
LANGUAGE_RE = re.compile(r"^[A-Z]{2}$")
LANGUAGES = {
    "EN": "English",
    "FR": "Français",
    "DE": "Deutsch",
    "ES": "Español",
    "PT": "Português",
    "IT": "Italiano",
    "RO": "Română",
    "PL": "Polski",
}
BOOK_ALIASES = {
    "Outfinitism_Meta_Rationality": "Outfinitism_Third_Edition",
}
EDITION_ALIASES = {
    ("The_Cascade_of_the_New_VOL_I", "RO"): "Cascada_Noului_Dosarul_Aster_Iteratia_3_RO",
    ("The_Right_to_Help", "RO"): "Dreptul_de_a_ajuta_RO",
    ("The_Thousand_Handed_Devil", "RO"): "Diavolul_cu_o_mie_de_maini_RO",
}


def describe(path: Path, root: Path = CONTENT_ROOT) -> dict[str, str]:
    relative = path.relative_to(root)
    parts = relative.parts
    record = {"path": relative.as_posix()}

    if parts[0] == "covers":
        record["kind"] = "cover"
    elif parts[0] == "thumbnails":
        record["kind"] = "thumbnail"
    elif parts[0] == "htmls" and len(parts) >= 3 and LANGUAGE_RE.fullmatch(parts[1]):
        record["kind"] = "html" if path.suffix.lower() == ".html" else "html-asset"
        record["language"] = parts[1]
    elif LANGUAGE_RE.fullmatch(parts[0]):
        record["kind"] = path.suffix.lower().lstrip(".") or "file"
        record["language"] = parts[0]
    else:
        record["kind"] = "file"
    return record


def find_edition_pdf(root: Path, language: str, basename: str, book_id: str) -> Path | None:
    alias = EDITION_ALIASES.get((book_id, language))
    if alias:
        path = root / language / f"{alias}.pdf"
        return path if path.is_file() else None
    candidates = list((root / language).glob(f"{basename}*.pdf"))
    if not candidates:
        return None
    expected = basename if language == "EN" else f"{basename}_{language}"

    def rank(path: Path) -> tuple[int, int, str]:
        stem = path.name.removesuffix(".pdf")
        if stem == expected:
            priority = 0
        elif stem.startswith(expected):
            priority = 1
        else:
            priority = 2
        return priority, len(path.name), path.name

    return min(candidates, key=rank)


def discover_books(root: Path = CONTENT_ROOT, docs_root: Path | None = None) -> list[dict[str, object]]:
    docs_root = docs_root or root.parent
    books = []
    cover_re = re.compile(r'class="[^"]*\bedition-cover\b[^"]*"[^>]*src="[^"]*/([^/]+)\.png"')
    for page in sorted((docs_root / "books").glob("*/index.html")):
        source = page.read_text(encoding="utf-8")
        match = cover_re.search(source)
        if not match:
            raise ValueError(f"book page has no edition cover: {page.relative_to(REPO_ROOT)}")
        book_id = unquote(match.group(1))
        basename = BOOK_ALIASES.get(book_id, book_id)
        editions = []
        for language, label in LANGUAGES.items():
            pdf = find_edition_pdf(root, language, basename, book_id)
            if pdf is None:
                continue
            html = root / "htmls" / language / pdf.with_suffix(".html").name
            if not html.is_file():
                raise ValueError(f"missing HTML edition for {pdf.relative_to(root)}")
            edition = {
                "language": language,
                "label": label,
                "pdf": pdf.relative_to(root).as_posix(),
                "html": html.relative_to(root).as_posix(),
            }
            if language == "EN":
                ten_minute = root / "10minutes" / pdf.with_suffix(".html").name
                if ten_minute.is_file():
                    edition["tenMinuteHtml"] = ten_minute.relative_to(root).as_posix()
            for extension in ("epub", "m4a", "mp3", "ogg"):
                alternative = pdf.with_suffix(f".{extension}")
                if alternative.is_file():
                    edition[extension if extension == "epub" else "audio"] = alternative.relative_to(root).as_posix()
                    break
            editions.append(edition)
        if not editions:
            raise ValueError(f"no content editions found for {page.relative_to(REPO_ROOT)} ({book_id})")
        books.append({"id": book_id, "slug": page.parent.name, "editions": editions})
    return books


def inventory(root: Path = CONTENT_ROOT) -> dict[str, object]:
    files = sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.name != "index.json"
            and path.name != "index.js"
            and path.name != ".gitkeep"
            and path.relative_to(root).parts[0] != "tools"
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    records = [describe(path, root) for path in files]
    languages = sorted({record["language"] for record in records if "language" in record})
    return {
        "schemaVersion": 1,
        "languages": languages,
        "fileCount": len(records),
        "books": discover_books(root),
        "files": records,
    }


def serialize(root: Path = CONTENT_ROOT) -> str:
    return json.dumps(inventory(root), ensure_ascii=False, indent=2) + "\n"


def serialize_script(root: Path = CONTENT_ROOT) -> str:
    """Expose the JSON manifest as a local-file-safe JavaScript include."""
    return "globalThis.__AXIOLOGIC_CONTENT_INDEX__ = " + serialize(root).rstrip() + ";\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    args = parser.parse_args(argv)
    expected = serialize()
    expected_script = serialize_script()
    if args.command == "build":
        INDEX_PATH.write_text(expected, encoding="utf-8")
        INDEX_SCRIPT_PATH.write_text(expected_script, encoding="utf-8")
        print(f"Indexed {inventory()['fileCount']} files in {INDEX_PATH.relative_to(REPO_ROOT)} and {INDEX_SCRIPT_PATH.relative_to(REPO_ROOT)}.")
        return 0
    if not INDEX_PATH.is_file():
        print(f"Missing {INDEX_PATH.relative_to(REPO_ROOT)}; run content_index.py build.", file=sys.stderr)
        return 1
    if INDEX_PATH.read_text(encoding="utf-8") != expected:
        print(f"Stale {INDEX_PATH.relative_to(REPO_ROOT)}; run content_index.py build.", file=sys.stderr)
        return 1
    if not INDEX_SCRIPT_PATH.is_file():
        print(f"Missing {INDEX_SCRIPT_PATH.relative_to(REPO_ROOT)}; run content_index.py build.", file=sys.stderr)
        return 1
    if INDEX_SCRIPT_PATH.read_text(encoding="utf-8") != expected_script:
        print(f"Stale {INDEX_SCRIPT_PATH.relative_to(REPO_ROOT)}; run content_index.py build.", file=sys.stderr)
        return 1
    print(f"Content index is current ({inventory()['fileCount']} files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
