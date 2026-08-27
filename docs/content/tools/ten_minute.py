#!/usr/bin/env python3
"""Build concise, source-linked ten-minute reading guides for every English PDF edition."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTENT_ROOT = REPO_ROOT / "docs" / "content"
SOURCE_DIRECTORY = CONTENT_ROOT / "htmls" / "EN"
OUTPUT_DIRECTORY = CONTENT_ROOT / "10minutes"
TARGET_WORDS = 1_400
MIN_WORDS = 18
MAX_WORDS = 320
OMIT_TEXT = re.compile(
    r"\b(?:copyright|all rights reserved|author(?:'s)? note|publication and research note|"
    r"ai[- ]assistance disclosure|selected references|references and current resources|bibliography)\b",
    re.IGNORECASE,
)
END_MATTER_HEADING = re.compile(r"\b(?:bibliography|references|selected reading)\b", re.IGNORECASE)


def normalize(value: str) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    return re.sub(r"^[A-Z][A-Za-z ]{2,70}\s·\s\d{1,4}\s+", "", text)


def words(value: str) -> list[str]:
    return re.findall(r"[\w’'-]+", value)


@dataclass(frozen=True)
class Entry:
    tag: str
    text: str


@dataclass(frozen=True)
class Passage:
    position: int
    heading: str
    text: str

    @property
    def word_count(self) -> int:
        return len(words(self.text))


class ReflowParser(HTMLParser):
    """Collect readable headings and paragraphs from a generated reflow edition."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries: list[Entry] = []
        self._tag: str | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3", "p"}:
            self._tag = tag
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._tag:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != self._tag:
            return
        text = normalize("".join(self._parts))
        if text:
            self.entries.append(Entry(tag, text))
        self._tag = None
        self._parts = []


def parse_source(path: Path) -> list[Entry]:
    parser = ReflowParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.entries


def acceptable(text: str, heading: str) -> bool:
    count = len(words(text))
    if count < MIN_WORDS or count > MAX_WORDS:
        return False
    if OMIT_TEXT.search(heading) or OMIT_TEXT.search(text):
        return False
    if text.count("http") > 1 or text.count(";") > 10:
        return False
    return True


def split_passage(text: str) -> list[str]:
    """Keep long PDF-extraction paragraphs readable without cutting a sentence."""
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z‘“])", text)
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0
    for sentence in sentences:
        sentence_words = len(words(sentence))
        if current and current_words + sentence_words > 190:
            chunks.append(" ".join(current))
            current = []
            current_words = 0
        current.append(sentence)
        current_words += sentence_words
    if current:
        chunks.append(" ".join(current))
    return chunks


def passages(entries: list[Entry]) -> list[Passage]:
    current_heading = ""
    result: list[Passage] = []
    for position, entry in enumerate(entries):
        if entry.tag in {"h1", "h2", "h3"}:
            # A table of contents may list “References” before the book begins.
            # End matter only starts after a substantial body of readable prose.
            if len(result) >= 20 and END_MATTER_HEADING.search(entry.text):
                break
            current_heading = entry.text
        elif entry.tag == "p":
            for fragment_index, fragment in enumerate(split_passage(entry.text)):
                if acceptable(fragment, current_heading):
                    result.append(Passage(position * 100 + fragment_index, current_heading, fragment))
    return result


def score(passage: Passage) -> float:
    """Prefer self-contained prose near a substantial, non-bibliographic section."""
    length_score = 1 - abs(145 - passage.word_count) / 145
    sentence_score = min(passage.text.count(".") + passage.text.count("?") + passage.text.count("!"), 5) / 5
    heading_score = 0.18 if passage.heading else 0
    citation_penalty = min(passage.text.count("(") * 0.04, 0.2)
    return length_score + sentence_score + heading_score - citation_penalty


def choose_passages(candidates: list[Passage]) -> list[Passage]:
    if not candidates:
        raise ValueError("no readable passages found")

    selected: list[Passage] = []
    selected_positions: set[int] = set()
    bucket_count = 10
    for bucket in range(bucket_count):
        start = bucket * len(candidates) // bucket_count
        end = (bucket + 1) * len(candidates) // bucket_count
        group = candidates[start:end] or candidates[start:start + 1]
        choice = max(group, key=score)
        selected.append(choice)
        selected_positions.add(choice.position)

    selected.sort(key=lambda passage: passage.position)
    total = sum(passage.word_count for passage in selected)
    for candidate in sorted(candidates, key=score, reverse=True):
        if total >= TARGET_WORDS:
            break
        if candidate.position in selected_positions:
            continue
        selected.append(candidate)
        selected_positions.add(candidate.position)
        total += candidate.word_count

    return sorted(selected, key=lambda passage: passage.position)


def document_title(entries: list[Entry], fallback: str) -> str:
    for entry in entries:
        if entry.tag in {"h1", "h2"} and 1 < len(entry.text) < 150 and not OMIT_TEXT.search(entry.text):
            return entry.text
    return fallback.replace("_", " ").strip()


def encoded(relative: Path) -> str:
    return quote(relative.as_posix(), safe="/")


def render(pdf: Path, source: Path, destination: Path) -> str:
    entries = parse_source(source)
    selection = choose_passages(passages(entries))
    title = document_title(entries, pdf.stem)
    word_count = sum(passage.word_count for passage in selection)
    full_html = encoded(Path("..") / "htmls" / "EN" / source.name)
    original_pdf = encoded(Path("..") / "EN" / pdf.name)

    sections: list[str] = []
    previous_heading = ""
    for passage in selection:
        heading = passage.heading if passage.heading and passage.heading != previous_heading else ""
        if heading:
            sections.append(f"<h2>{escape(heading)}</h2>")
            previous_heading = passage.heading
        sections.append(f"<p>{escape(passage.text)}</p>")

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta name=\"description\" content=\"A ten-minute guided reading of {escape(title, quote=True)}.\">
  <meta name=\"reading-time\" content=\"10 minutes\">
  <meta name=\"source-pdf\" content=\"{escape(pdf.name, quote=True)}\">
  <title>{escape(title)} · 10-minute read</title>
  <link rel=\"stylesheet\" href=\"../../reader/standalone.css?v=20260827-3\">
  <style>
    .ten-minute-header {{ margin-bottom: 2.4rem; padding-bottom: 1.5rem; border-bottom: 1px solid color-mix(in srgb, currentColor 22%, transparent); }}
    .ten-minute-header p {{ text-indent: 0; text-align: left; }}
    .ten-minute-kicker {{ color: var(--standalone-link); font: 700 .78em/1.2 system-ui, sans-serif; letter-spacing: .12em; text-transform: uppercase; }}
    .ten-minute-links {{ display: flex; flex-wrap: wrap; gap: .8rem 1.1rem; margin-top: 1.2rem; font-family: system-ui, sans-serif; font-size: .82em; }}
    .ten-minute-note {{ font-size: .86em; color: color-mix(in srgb, currentColor 72%, transparent); }}
  </style>
  <script defer src=\"https://cloud.umami.is/script.js\" data-website-id=\"e252999d-4479-42d7-9526-5f778846d4f6\"></script>
</head>
<body>
  <header class=\"ten-minute-header\">
    <p class=\"ten-minute-kicker\">10-minute reading guide</p>
    <h1>{escape(title)}</h1>
    <p>About 10 minutes · {word_count:,} words</p>
    <p class=\"ten-minute-note\">This guided edition selects substantial passages from the English source to make the central argument readable in one sitting. It is not a replacement for the complete edition.</p>
    <nav class=\"ten-minute-links\" aria-label=\"Edition links\"><a href=\"{full_html}\">Read the full HTML edition</a><a href=\"{original_pdf}\">Download the original PDF</a></nav>
  </header>
  <main>
    {''.join(sections)}
  </main>
  <script defer src=\"../../reader/standalone.js?v=20260827-1\"></script>
</body>
</html>
"""


def targets() -> list[tuple[Path, Path, Path]]:
    pairs = []
    for pdf in sorted((CONTENT_ROOT / "EN").glob("*.pdf")):
        source = SOURCE_DIRECTORY / pdf.with_suffix(".html").name
        if not source.is_file():
            raise FileNotFoundError(f"missing English reflow edition for {pdf.relative_to(CONTENT_ROOT)}")
        pairs.append((pdf, source, OUTPUT_DIRECTORY / pdf.with_suffix(".html").name))
    return pairs


def build() -> int:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for pdf, source, destination in targets():
        destination.write_text(render(pdf, source, destination), encoding="utf-8")
    print(f"Built {len(targets())} ten-minute reading guides in {OUTPUT_DIRECTORY.relative_to(REPO_ROOT)}.")
    return 0


def check() -> int:
    problems = []
    for pdf, source, destination in targets():
        expected = render(pdf, source, destination)
        if not destination.is_file():
            problems.append(f"missing {destination.relative_to(REPO_ROOT)}")
        elif destination.read_text(encoding="utf-8") != expected:
            problems.append(f"stale {destination.relative_to(REPO_ROOT)}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"Ten-minute reading guides are current ({len(targets())} files).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    args = parser.parse_args(argv)
    return build() if args.command == "build" else check()


if __name__ == "__main__":
    raise SystemExit(main())
