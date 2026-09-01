#!/usr/bin/env python3
"""Prepare, assemble, and validate agent-translated HTML reader chunks.

This tool deliberately has no translation service integration. ``prepare``
replaces only visible, translatable text nodes with stable placeholders and
groups their source text into small JSON chunks. An agent translates the
``source`` value of each segment into its ``translation`` value. ``assemble``
then restores the translated text into the untouched HTML template.
"""

from __future__ import annotations

import argparse
from html import escape, unescape
import json
from pathlib import Path
import re
import sys

from translate_books import (
    IGNORED_TEXT_TAGS,
    LANGUAGE_TAGS,
    REPO_ROOT,
    TAG_NAME_RE,
    TAG_TOKEN_RE,
    rebase_local_urls,
    reader_targets,
    set_document_language,
    short_excerpt_source,
    strip_english_pdf_material,
    validate_translation_source,
)


PLACEHOLDER = "<!-- AXIOLOGIC_TRANSLATION:{slot_id} -->"
WHITESPACE_RE = re.compile(r"^(\s*)(.*?)(\s*)$", re.DOTALL)
WORD_RE = re.compile(r"[\w’'-]+")


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")


def translatable_slots(source: str) -> tuple[str, list[dict[str, str]]]:
    """Return an HTML template and ordered visible text slots.

    Tags, attributes, whitespace, images, scripts, styles, and code samples
    remain byte-for-byte intact. Text is restored only during assembly.
    """
    output: list[str] = []
    slots: list[dict[str, str]] = []
    stack: list[str] = []
    for token in TAG_TOKEN_RE.split(source):
        if not token:
            continue
        if token.startswith("<"):
            output.append(token)
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
            output.append(token)
            continue
        match = WHITESPACE_RE.match(token)
        assert match is not None
        prefix, text, suffix = match.groups()
        decoded = unescape(text)
        if not decoded or not any(character.isalpha() for character in decoded):
            output.append(token)
            continue
        slot_id = f"t{len(slots) + 1:06d}"
        slots.append({"id": slot_id, "source": decoded})
        output.append(prefix + PLACEHOLDER.format(slot_id=slot_id) + suffix)
    return "".join(output), slots


def chunk_slots(slots: list[dict[str, str]], maximum_words: int) -> list[list[dict[str, str]]]:
    chunks: list[list[dict[str, str]]] = []
    chunk: list[dict[str, str]] = []
    words = 0
    for slot in slots:
        slot_words = max(1, len(WORD_RE.findall(slot["source"])))
        if chunk and words + slot_words > maximum_words:
            chunks.append(chunk)
            chunk = []
            words = 0
        chunk.append(slot)
        words += slot_words
    if chunk:
        chunks.append(chunk)
    return chunks


def prepare_document(
    raw: str,
    source_path: Path,
    language: str,
    destination_path: Path,
    workdir: Path,
    maximum_words: int,
    full_paths: dict[Path, Path],
) -> None:
    """Normalize one source reader and emit its agent-translation workfiles."""
    source_path = source_path.resolve()
    destination_path = destination_path.resolve()
    workdir = workdir.resolve()
    if language not in LANGUAGE_TAGS:
        raise ValueError(f"unsupported language: {language}")
    prepared = strip_english_pdf_material(raw)
    prepared = rebase_local_urls(prepared, "", source_path, destination_path, full_paths)
    prepared = set_document_language(prepared, language)
    template, slots = translatable_slots(prepared)
    chunks = chunk_slots(slots, maximum_words)
    chunks_dir = workdir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    (workdir / "template.html").write_text(template, encoding="utf-8")
    manifest = {
        "source": relative(source_path),
        "destination": relative(destination_path),
        "language": language,
        "slotCount": len(slots),
        "chunkCount": len(chunks),
        "maximumWords": maximum_words,
    }
    (workdir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for number, chunk in enumerate(chunks, start=1):
        payload = {
            "language": language,
            "chunk": number,
            "segments": [{**slot, "translation": ""} for slot in chunk],
        }
        (chunks_dir / f"{number:04d}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(slots)} slots in {len(chunks)} chunks at {relative(workdir)}")


def prepare(source_path: Path, language: str, destination_path: Path, workdir: Path, maximum_words: int) -> None:
    source_path = source_path.resolve()
    raw = source_path.read_text(encoding="utf-8")
    prepare_document(raw, source_path, language, destination_path, workdir, maximum_words, {source_path: destination_path.resolve()})


def prepare_missing(languages: set[str], editions: set[str], work_root: Path, maximum_words: int, selected: set[str] | None) -> None:
    """Queue every missing reader file as independent, agent-translatable chunks."""
    prepared = 0
    skipped = 0
    for book, source_full, source_short, destination_full, destination_short, language, _ in reader_targets(languages):
        if selected is not None and str(book["id"]) not in selected:
            continue
        targets = []
        if "full" in editions:
            targets.append(("full", source_full.read_text(encoding="utf-8"), source_full, destination_full))
        if "short" in editions:
            short_source = source_short or source_full
            raw = source_short.read_text(encoding="utf-8") if source_short else short_excerpt_source(source_full.read_text(encoding="utf-8"))
            targets.append(("short", raw, short_source, destination_short))
        for edition, raw, source_path, destination in targets:
            if destination.is_file():
                skipped += 1
                continue
            workdir = work_root / language / str(book["id"]) / edition
            if (workdir / "manifest.json").is_file():
                skipped += 1
                continue
            prepare_document(raw, source_path, language, destination, workdir, maximum_words, {source_full.resolve(): destination_full.resolve()})
            prepared += 1
    print(f"Prepared {prepared} missing reader files; skipped {skipped} existing or queued files.")


def assemble(workdir: Path) -> None:
    workdir = workdir.resolve()
    manifest = json.loads((workdir / "manifest.json").read_text(encoding="utf-8"))
    template = (workdir / "template.html").read_text(encoding="utf-8")
    translations: dict[str, str] = {}
    for chunk_path in sorted((workdir / "chunks").glob("*.json")):
        payload = json.loads(chunk_path.read_text(encoding="utf-8"))
        for segment in payload["segments"]:
            slot_id = segment["id"]
            translated = segment.get("translation", "").strip()
            if not translated:
                raise ValueError(f"{relative(chunk_path)}: {slot_id} is untranslated")
            if slot_id in translations:
                raise ValueError(f"{relative(chunk_path)}: duplicate slot {slot_id}")
            translations[slot_id] = translated
    if len(translations) != manifest["slotCount"]:
        raise ValueError(f"expected {manifest['slotCount']} translations, found {len(translations)}")
    for slot_id, translated in translations.items():
        marker = PLACEHOLDER.format(slot_id=slot_id)
        if marker not in template:
            raise ValueError(f"template is missing {slot_id}")
        template = template.replace(marker, escape(translated, quote=False), 1)
    if "AXIOLOGIC_TRANSLATION:" in template:
        raise ValueError("template still contains untranslated placeholders")
    problems = validate_translation_source(template)
    if problems:
        raise ValueError("; ".join(problems))
    destination = REPO_ROOT / manifest["destination"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(template, encoding="utf-8")
    print(f"Assembled {relative(destination)}")


def check(workdir: Path) -> int:
    workdir = workdir.resolve()
    manifest = json.loads((workdir / "manifest.json").read_text(encoding="utf-8"))
    missing = []
    segments = 0
    for chunk_path in sorted((workdir / "chunks").glob("*.json")):
        payload = json.loads(chunk_path.read_text(encoding="utf-8"))
        for segment in payload["segments"]:
            segments += 1
            if not segment.get("translation", "").strip():
                missing.append(f"{chunk_path.name}:{segment['id']}")
    if segments != manifest["slotCount"]:
        missing.append(f"slot count mismatch: {segments} != {manifest['slotCount']}")
    if missing:
        print("\n".join(missing), file=sys.stderr)
        return 1
    print(f"All {segments} segments are translated.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare", help="extract stable translatable chunks")
    prepare_parser.add_argument("source", type=Path)
    prepare_parser.add_argument("--language", required=True, choices=tuple(LANGUAGE_TAGS))
    prepare_parser.add_argument("--destination", required=True, type=Path)
    prepare_parser.add_argument("--workdir", required=True, type=Path)
    prepare_parser.add_argument("--maximum-words", type=int, default=700)
    assemble_parser = commands.add_parser("assemble", help="rebuild HTML from translated chunks")
    assemble_parser.add_argument("workdir", type=Path)
    check_parser = commands.add_parser("check", help="report untranslated slots")
    check_parser.add_argument("workdir", type=Path)
    missing_parser = commands.add_parser("prepare-missing", help="queue all missing reader editions for direct agent translation")
    missing_parser.add_argument("--language", action="append", required=True, choices=tuple(LANGUAGE_TAGS))
    missing_parser.add_argument("--edition", action="append", choices=("full", "short"), help="edition to queue; defaults to both")
    missing_parser.add_argument("--book", action="append", dest="books", help="book ID to queue (repeatable)")
    missing_parser.add_argument("--work-root", type=Path, default=Path("docs/content/.translation-work"))
    missing_parser.add_argument("--maximum-words", type=int, default=700)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        if args.maximum_words < 1:
            parser.error("--maximum-words must be positive")
        prepare(args.source, args.language, args.destination, args.workdir, args.maximum_words)
        return 0
    if args.command == "assemble":
        assemble(args.workdir)
        return 0
    if args.command == "prepare-missing":
        if args.maximum_words < 1:
            parser.error("--maximum-words must be positive")
        prepare_missing(set(args.language), set(args.edition or ("full", "short")), args.work_root, args.maximum_words, set(args.books) if args.books else None)
        return 0
    return check(args.workdir)


if __name__ == "__main__":
    raise SystemExit(main())
