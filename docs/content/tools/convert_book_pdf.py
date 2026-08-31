#!/usr/bin/env python3
"""Convert book PDFs to hybrid reflowable HTML with images and tables."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from html import escape
import hashlib
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from urllib.parse import quote
import xml.etree.ElementTree as ET

from book_html import ANALYTICS, CONTENT_ROOT, HTML_ROOT, REPO_ROOT, html_for_pdf, repair_source, warning_html


PAGE_BREAK = "\f"
TERMINAL_RE = re.compile(r"[.!?…]\s*[\"'”’»“„«‹）\)\]]*$")
URL_RE = re.compile(r"(https?://[^\s<]+|www\.[^\s<]+)")
PAGE_NUMBER_RE = re.compile(r"^\s*(?:[—–−-]+\s*)?(?:page\s+)?\d{1,4}(?:\s*(?:/|of)\s*\d{1,4})?(?:\s*[—–−|·•*_=~.:-]+)?\s*$", re.IGNORECASE)
DECORATED_LETTER_RE = re.compile(r"^\s*[—–−|·•*_=~.:-]+\s*(?:[A-Za-z]|[IVXLCDM]{1,8})\s*[—–−|·•*_=~.:-]+\s*$", re.IGNORECASE)
ROMAN_NUMBER_RE = re.compile(r"^[IVXLCDM]{1,8}$", re.IGNORECASE)
QUOTED_SPEECH_RE = re.compile(
    r'"[^"“”„«»‹›\n]+?"|“[^"“”„«»‹›\n]+?”|'
    r'„[^"“”„«»‹›\n]+?”|„[^"“”„«»‹›\n]+?“|'
    r'«[^"“”„«»‹›\n]+?»|‹[^"“”„«»‹›\n]+?›'
)
MIXED_QUOTED_SPEECH_RE = re.compile(r'["“„«‹][^"“”„«»‹›\n]+?["”“»›]')
ATTRIBUTION_VERB_RE = re.compile(
    r"\b(?:said|asked|replied|answered|whispered|shouted|murmured|called|"
    r"spuse|întreb\w*|raspun\w*|răspun\w*|șopti\w*|strig\w*|"
    r"dijo|pregunt\w*|respond\w*|disse|pergunt\w*|"
    r"dit|demanda\w*|répon\w*|chiese|rispose|"
    r"sagte|fragte|antwort\w*|powiedzia\w*|zapyta\w*|odpowied\w*)\b",
    re.IGNORECASE,
)
STRUCTURAL_HEADING_RE = re.compile(
    r"^(?:chapter|part|volume|book|appendix|contents|abstract|introduction|preface|prologue|epilogue|references|sources|section)\b",
    re.IGNORECASE,
)
OUTLINE_HEADING_RE = re.compile(
    r"^(?:(?:[A-Z]|\d{1,3})\.\d{1,3}(?:\.\d{1,3})*\s+(?=[A-ZÀ-Ž])|.{1,80}\s[A-Z]\.\d{1,3}(?:\.\d{1,3})*\s*$)"
)
CONTENTS_HEADING_RE = re.compile(
    r"^(?:contents?|content|inhalt|inhaltsverzeichnis|índice|indice|sommaire|table des matières|spis treści|cuprins)$",
    re.IGNORECASE,
)
LIGATURES = str.maketrans({"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"})


def is_finished(text: str) -> bool:
    return bool(TERMINAL_RE.search(text.rstrip()))


@dataclass
class FontSpec:
    size: float
    family: str = ""


@dataclass
class TextBox:
    top: float
    left: float
    width: float
    height: float
    text: str
    font_size: float
    bold: bool = False
    italic: bool = False
    leading_space: bool = False
    trailing_space: bool = False
    toc_entry: bool = False

    @property
    def right(self) -> float:
        return self.left + self.width


@dataclass
class VisualLine:
    boxes: list[TextBox]
    source_index: int = 0

    @property
    def top(self) -> float:
        return min(box.top for box in self.boxes)

    @property
    def left(self) -> float:
        return min(box.left for box in self.boxes)

    @property
    def right(self) -> float:
        return max(box.right for box in self.boxes)

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return max(box.height for box in self.boxes)

    @property
    def font_size(self) -> float:
        return max(box.font_size for box in self.boxes)

    @property
    def bold(self) -> bool:
        bold_chars = sum(len(box.text) for box in self.boxes if box.bold)
        return bold_chars >= max(1, sum(len(box.text) for box in self.boxes) * 0.55)

    @property
    def italic(self) -> bool:
        italic_chars = sum(len(box.text) for box in self.boxes if box.italic)
        return italic_chars >= max(1, sum(len(box.text) for box in self.boxes) * 0.55)

    @property
    def toc_entry(self) -> bool:
        return any(box.toc_entry for box in self.boxes)

    @property
    def text(self) -> str:
        return join_boxes(self.boxes)


@dataclass
class ImageBox:
    page: int
    index: int
    top: float
    left: float
    width: float
    height: float
    source: Path


@dataclass
class PdfPage:
    number: int
    width: float
    height: float
    lines: list[VisualLine]
    images: list[ImageBox]


@dataclass
class ContentBlock:
    top: float
    kind: str
    text: str = ""
    rows: list[list[str]] = field(default_factory=list)
    image: ImageBox | None = None
    bold: bool = False
    italic: bool = False
    font_size: float = 0.0
    page_anchor: int | None = None
    last_top: float | None = None


def clean_text(text: str) -> str:
    text = text.translate(LIGATURES).replace("\u200b", "")
    text = re.sub(r"\s*[._·•]{2,}\s*\d{1,4}\s*$", "", text)
    if re.search(r"[._·•]{8,}", text):
        text = re.sub(r"[._·•]{8,}", " ", text)
        text = re.sub(r"\s+\d{1,4}\s*$", "", text)
    return " ".join(text.split())


def join_boxes(boxes: list[TextBox]) -> str:
    ordered = sorted((box for box in boxes if box.text), key=lambda box: box.left)
    result = ""
    previous: TextBox | None = None
    for box in ordered:
        if previous and result and box.text:
            gap = box.left - previous.right
            if (gap > 1 or previous.trailing_space or box.leading_space) and not result.endswith((" ", "-", "—", "–", "/")) and not box.text.startswith((" ", ".", ",", ";", ":", "!", "?", ")", "]")):
                result += " "
        result += box.text
        previous = box
    return clean_text(result)


def group_visual_lines(boxes: list[TextBox]) -> list[VisualLine]:
    lines: list[VisualLine] = []
    for box in sorted((item for item in boxes if item.text), key=lambda item: (item.top, item.left)):
        def same_visual_row(line: VisualLine) -> bool:
            smaller_height = min(line.height, box.height)
            overlap = min(line.top + line.height, box.top + box.height) - max(line.top, box.top)
            similar_top = abs(line.top - box.top) <= max(3.0, smaller_height * 0.3)
            substantial_overlap = overlap >= smaller_height * 0.55
            return similar_top or substantial_overlap

        match = next((line for line in reversed(lines[-4:]) if same_visual_row(line)), None)
        if match is None:
            lines.append(VisualLine([box]))
        else:
            match.boxes.append(box)
    lines.sort(key=lambda line: (line.top, line.left))
    for index, line in enumerate(lines):
        line.source_index = index
    return lines


def parse_pdf_xml(xml_path: Path) -> list[PdfPage]:
    root = ET.parse(xml_path).getroot()
    fonts: dict[str, FontSpec] = {}
    pages: list[PdfPage] = []
    for page_element in root.findall("page"):
        for font in page_element.findall("fontspec"):
            fonts[font.get("id", "")] = FontSpec(float(font.get("size", "12")), font.get("family", ""))
        boxes: list[TextBox] = []
        for element in page_element.findall("text"):
            raw_text = "".join(element.itertext()).translate(LIGATURES).replace("\u200b", "")
            text = clean_text(raw_text)
            if not text:
                continue
            font = fonts.get(element.get("font", ""), FontSpec(12))
            toc_entry = bool(re.search(r"[._·•]{2,}\s*\d{1,4}\s*$", raw_text))
            boxes.append(TextBox(float(element.get("top", "0")), float(element.get("left", "0")), float(element.get("width", "0")), float(element.get("height", str(font.size))), text, font.size, element.find(".//b") is not None, element.find(".//i") is not None, bool(raw_text[:1].isspace()), bool(raw_text[-1:].isspace()), toc_entry))
        number = int(page_element.get("number", str(len(pages) + 1)))
        images = [ImageBox(number, index, float(element.get("top", "0")), float(element.get("left", "0")), float(element.get("width", "0")), float(element.get("height", "0")), Path(element.get("src", ""))) for index, element in enumerate(page_element.findall("image"), start=1) if element.get("src")]
        pages.append(PdfPage(number, float(page_element.get("width", "1")), float(page_element.get("height", "1")), group_visual_lines(boxes), images))
    return pages


def remove_repeated_template_images(pages: list[PdfPage], minimum_pages: int = 3) -> int:
    """Drop byte-identical images repeated across pages (backgrounds/logos).

    Exact byte identity plus page-edge/full-page placement keeps deliberately
    repeated figures in the body while removing document-template decoration.
    """
    digests: dict[Path, str] = {}
    pages_by_digest: dict[str, set[int]] = {}
    for page in pages:
        for image in page.images:
            if not image.source.is_file():
                continue
            digest = hashlib.sha256(image.source.read_bytes()).hexdigest()
            digests[image.source] = digest
            pages_by_digest.setdefault(digest, set()).add(page.number)
    repeated = {digest for digest, page_numbers in pages_by_digest.items() if len(page_numbers) >= minimum_pages}
    removed = 0
    for page in pages:
        retained = []
        for image in page.images:
            area_ratio = image.width * image.height / max(1.0, page.width * page.height)
            at_page_edge = image.top + image.height <= page.height * 0.16 or image.top >= page.height * 0.84
            looks_like_template = area_ratio >= 0.65 or (area_ratio <= 0.16 and at_page_edge)
            if digests.get(image.source) in repeated and looks_like_template:
                removed += 1
            else:
                retained.append(image)
        page.images = retained
    return removed


def split_cells(line: VisualLine, page_width: float) -> list[list[TextBox]]:
    cells: list[list[TextBox]] = []
    threshold = max(20.0, page_width * 0.04)
    for box in sorted(line.boxes, key=lambda item: item.left):
        if not cells or box.left - max(item.right for item in cells[-1]) >= threshold:
            cells.append([box])
        else:
            cells[-1].append(box)
    return cells


def cluster_positions(values: list[float], tolerance: float) -> list[float]:
    clusters: list[list[float]] = []
    for value in sorted(values):
        if not clusters or value - statistics.mean(clusters[-1]) > tolerance:
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return [statistics.median(cluster) for cluster in clusters]


def table_regions(lines: list[VisualLine], page_width: float) -> list[tuple[list[int], list[list[str]]]]:
    result: list[tuple[list[int], list[list[str]]]] = []
    index = 0
    while index < len(lines):
        if len(split_cells(lines[index], page_width)) < 2:
            index += 1
            continue
        region = [index]
        multi_count = 1
        cursor = index + 1
        while cursor < len(lines):
            previous, line = lines[region[-1]], lines[cursor]
            if line.top - previous.top > max(54.0, previous.height * 2.8):
                break
            cells = split_cells(line, page_width)
            if len(cells) >= 2:
                region.append(cursor)
                multi_count += 1
            elif len(cells) == 1 and line.width < page_width * 0.48:
                region.append(cursor)
            else:
                break
            cursor += 1
        if multi_count < 2:
            index += 1
            continue
        anchor_values = [min(box.left for box in cell) for line_index in region for cell in split_cells(lines[line_index], page_width) if len(split_cells(lines[line_index], page_width)) >= 2]
        anchors = cluster_positions(anchor_values, page_width * 0.09)
        if len(anchors) < 2 or anchors[-1] - anchors[0] < page_width * 0.18:
            index += 1
            continue
        anchors = anchors[:8]
        rows: list[list[str]] = []
        current: list[str] | None = None
        previous_line: VisualLine | None = None
        for line_index in region:
            line = lines[line_index]
            assigned = ["" for _ in anchors]
            cell_positions: list[tuple[int, float]] = []
            for cell in split_cells(line, page_width):
                left = min(box.left for box in cell)
                column = min(range(len(anchors)), key=lambda candidate: abs(anchors[candidate] - left))
                assigned[column] = join_boxes(cell)
                cell_positions.append((column, left))
            populated = [column for column, value in enumerate(assigned) if value]
            close_continuation = previous_line is not None and line.top - previous_line.top <= max(previous_line.height * 1.55, 26)
            shifted_wrap = bool(cell_positions) and all(left < anchors[column] - page_width * 0.018 for column, left in cell_positions)
            begins_row = (len(populated) >= 2 and not (close_continuation and shifted_wrap)) or current is None or not close_continuation
            if begins_row:
                current = assigned
                rows.append(current)
            elif current is not None:
                for column in populated:
                    current[column] = clean_text(f"{current[column]} {assigned[column]}")
            previous_line = line
        if len(rows) >= 2:
            result.append((region, rows))
            index = region[-1] + 1
        else:
            index += 1
    return result


def repeated_furniture(pages: list[PdfPage]) -> set[str]:
    counts: Counter[str] = Counter()
    for page in pages:
        counts.update({line.text for line in page.lines if line.text and (line.top <= page.height * 0.09 or line.top >= page.height * 0.88)})
    return {text for text, count in counts.items() if count >= 3}


def is_page_furniture(line: VisualLine, page: PdfPage, repeated: set[str]) -> bool:
    near_edge = line.top <= page.height * 0.09 or line.top >= page.height * 0.88
    at_footer = line.top >= page.height * 0.88
    page_number = bool(PAGE_NUMBER_RE.fullmatch(line.text))
    stray_edge_marker = bool(DECORATED_LETTER_RE.fullmatch(line.text) or (at_footer and ROMAN_NUMBER_RE.fullmatch(line.text)))
    return not line.text or bool(near_edge and (line.text in repeated or page_number or stray_edge_marker))


def looks_heading(line: VisualLine, body_size: float) -> bool:
    letters = [char for char in line.text if char.isalpha()]
    upper_ratio = sum(char.isupper() for char in letters) / max(1, len(letters))
    first_alpha = next((char for char in line.text if char.isalpha()), "")
    size_only_heading = line.font_size >= body_size * 1.35 and not first_alpha.islower() and not (is_finished(line.text) and not line.bold and upper_ratio < 0.82)
    uppercase_heading = upper_ratio >= 0.82 and len(letters) >= 5 and line.font_size >= body_size * 0.9
    structural_heading = looks_structural_heading(line)
    return bool(line.text) and len(line.text) <= 150 and (
        size_only_heading
        or (line.bold and line.font_size >= body_size * 1.05)
        or uppercase_heading
        or structural_heading
    )


def looks_structural_heading(line: VisualLine) -> bool:
    return bool(line.text) and len(line.text) <= 100 and bool(
        STRUCTURAL_HEADING_RE.match(line.text) or OUTLINE_HEADING_RE.match(line.text)
    )


def prose_run_indices(lines: list[VisualLine]) -> set[int]:
    """Find sustained same-style prose runs on pages with mixed font scales."""
    result: set[int] = set()
    start = 0
    while start < len(lines):
        run = [start]
        cursor = start + 1
        while cursor < len(lines):
            previous, current = lines[cursor - 1], lines[cursor]
            similar_font = abs(previous.font_size - current.font_size) <= max(previous.font_size, current.font_size) * 0.08
            close = current.top - previous.top <= max(30.0, max(previous.font_size, current.font_size) * 1.8)
            if not similar_font or previous.bold != current.bold or not close:
                break
            run.append(cursor)
            cursor += 1
        characters = sum(len(lines[index].text) for index in run)
        letters = [char for index in run for char in lines[index].text if char.isalpha()]
        lowercase_ratio = sum(char.islower() for char in letters) / max(1, len(letters))
        sustained_prose = len(run) >= 3 and characters >= 180 and any(is_finished(lines[index].text) for index in run)
        sentence_like_display = (
            len(run) >= 2
            and characters >= 120
            and not lines[run[0]].bold
            and lowercase_ratio >= 0.5
            and is_finished(lines[run[-1]].text)
        )
        if sustained_prose or sentence_like_display:
            result.update(run)
        start = cursor
    return result


def heading_run_indices(lines: list[VisualLine], body_size: float) -> set[int]:
    """Find dense heading-style runs that are lists/contents, not one title."""
    result: set[int] = set()
    start = 0
    while start < len(lines):
        if not looks_heading(lines[start], body_size):
            start += 1
            continue
        run = [start]
        cursor = start + 1
        while cursor < len(lines):
            previous, current = lines[cursor - 1], lines[cursor]
            similar_font = abs(previous.font_size - current.font_size) <= max(previous.font_size, current.font_size) * 0.12
            close = current.top - previous.top <= max(previous.font_size, current.font_size) * 2.3
            if not looks_heading(current, body_size) or not similar_font or previous.bold != current.bold or not close:
                break
            run.append(cursor)
            cursor += 1
        if len(run) >= 4 and sum(len(lines[index].text) for index in run) >= 140:
            result.update(run)
        start = cursor
    return result


def spoken_quote(match: re.Match[str]) -> bool:
    following = match.string[match.end():match.end() + 4]
    return bool(re.search(r"[.!?…,;:]\s*$", match.group(0)[1:-1]) or re.match(r"\s*[.,;:!?]", following))


def quote_matches(text: str) -> list[re.Match[str]]:
    """Prefer correctly paired quotes, adding only non-overlapping mixed pairs."""
    matches = list(QUOTED_SPEECH_RE.finditer(text))
    spans = [(match.start(), match.end()) for match in matches]
    for match in MIXED_QUOTED_SPEECH_RE.finditer(text):
        if not any(match.start() < end and start < match.end() for start, end in spans):
            matches.append(match)
            spans.append((match.start(), match.end()))
    return sorted(matches, key=lambda match: match.start())


def leading_quote(text: str) -> re.Match[str] | None:
    return next((match for match in quote_matches(text) if match.start() == 0), None)


def first_sentence(text: str) -> tuple[str, str]:
    match = re.match(r"^(.+?[.!?…])(?:\s+|$)(.*)$", text, re.DOTALL)
    return (match.group(1), match.group(2)) if match else (text, "")


def dialogue_parts(text: str, force: bool = False) -> list[str]:
    """Split dialogue-heavy prose while retaining short speech attributions."""
    matches = [match for match in quote_matches(text) if force or spoken_quote(match)]
    if not matches:
        return [text]
    parts: list[tuple[str, str]] = []
    cursor = 0
    for match in matches:
        outside = clean_text(text[cursor:match.start()])
        joined_next_quote = False
        if outside:
            if parts and parts[-1][0] == "dialogue":
                sentence, remainder = first_sentence(outside)
                first_alpha = next((char for char in sentence if char.isalpha()), "")
                attribution = len(sentence) <= 72 and (first_alpha.islower() or ATTRIBUTION_VERB_RE.search(sentence))
                if attribution:
                    parts[-1] = ("dialogue", clean_text(f"{parts[-1][1]} {sentence}"))
                    joined_next_quote = not remainder
                    outside = clean_text(remainder)
            if outside:
                parts.append(("narration", outside))
        external_punctuation = re.match(r"\s*([.,;:!?])", text[match.end():])
        quote = clean_text(match.group(0))
        consumed_end = match.end()
        if external_punctuation:
            quote += external_punctuation.group(1)
            consumed_end += external_punctuation.end()
        if joined_next_quote and parts and parts[-1][0] == "dialogue":
            parts[-1] = ("dialogue", clean_text(f"{parts[-1][1]} {quote}"))
        else:
            parts.append(("dialogue", quote))
        cursor = consumed_end
    tail = clean_text(text[cursor:])
    if tail:
        if parts and parts[-1][0] == "dialogue":
            sentence, remainder = first_sentence(tail)
            first_alpha = next((char for char in sentence if char.isalpha()), "")
            if len(sentence) <= 72 and (first_alpha.islower() or ATTRIBUTION_VERB_RE.search(sentence)):
                parts[-1] = ("dialogue", clean_text(f"{parts[-1][1]} {sentence}"))
                tail = clean_text(remainder)
        if tail:
            parts.append(("narration", tail))
    return [part for _, part in parts if part]


def long_prose_parts(text: str, maximum: int = 1800) -> list[str]:
    """Break extraction-created walls of text only at sentence boundaries."""
    if len(text) <= maximum:
        return [text]
    sentences = re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-ŽĂÂÎȘȚÄÖÜẞ“\"„«‹])", text)
    if len(sentences) < 2:
        return [text]
    parts: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = clean_text(f"{current} {sentence}") if current else sentence
        if current and len(candidate) > maximum:
            parts.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def page_blocks(page: PdfPage, repeated: set[str]) -> list[ContentBlock]:
    lines = [line for line in page.lines if not is_page_furniture(line, page, repeated)]
    full_page = [image for image in page.images if image.width * image.height >= page.width * page.height * 0.72]
    if full_page:
        image = max(full_page, key=lambda item: item.width * item.height)
        return [ContentBlock(image.top, "image", image=image, page_anchor=page.number)]
    isolated_display_title = bool(
        not page.images
        and 1 <= len(lines) <= 3
        and all(line.bold and line.font_size >= page.height * 0.02 for line in lines)
        and all(
            abs(lines[0].font_size - line.font_size) <= max(lines[0].font_size, line.font_size) * 0.12
            for line in lines[1:]
        )
        and all(
            current.top - previous.top <= max(previous.font_size, current.font_size) * 1.75
            for previous, current in zip(lines, lines[1:])
        )
    )
    if isolated_display_title:
        return [
            ContentBlock(
                lines[0].top,
                "title",
                text=clean_text(" ".join(line.text for line in lines)),
                bold=True,
                font_size=max(line.font_size for line in lines),
                page_anchor=page.number,
            )
        ]
    regions = table_regions(lines, page.width)
    table_by_start = {indices[0]: (set(indices), rows) for indices, rows in regions}
    table_indices = {index for indices, _ in regions for index in indices}
    blocks: list[ContentBlock] = []
    body_sizes = [line.font_size for index, line in enumerate(lines) if index not in table_indices]
    body_size = statistics.median(body_sizes) if body_sizes else 12.0
    prose_indices = prose_run_indices(lines)
    list_heading_indices = heading_run_indices(lines, body_size)
    contents_indices = {index for index, line in enumerate(lines) if CONTENTS_HEADING_RE.fullmatch(line.text.strip())}
    toc_page = bool(contents_indices) or sum(line.toc_entry for line in lines) >= 3
    if toc_page:
        list_heading_indices.update(index for index in range(len(lines)) if index not in contents_indices)
    body_lines = [line for index, line in enumerate(lines) if index not in table_indices and (index in prose_indices or index in list_heading_indices or not looks_heading(line, body_size))]
    # In first-line-indented books, paragraph starts can outnumber wrapped
    # continuation lines. The statistical mode therefore selects the indent,
    # collapsing a whole page into one paragraph. Long lines reveal the true
    # body margin: use their leftmost cluster and treat the indent as a break.
    long_body_lines = [line for line in body_lines if line.width >= page.width * 0.52 or line.right >= page.width * 0.84]
    margin_candidates = long_body_lines or body_lines
    margin_left = min((round(line.left / 5) * 5 for line in margin_candidates), default=min((line.left for line in lines), default=0))
    indent_threshold = max(8.0, page.width * 0.012)
    # A first-line indent is meaningful only when it recurs at the same offset.
    # Individual extracted lines often drift a few pixels to the right because
    # of PDF glyph boxes or justification; treating every such drift as a new
    # paragraph produces the arbitrary splits the reflow reader must avoid.
    indent_offsets = Counter(
        round((line.left - margin_left) / 5) * 5
        for line in body_lines
        if line.left >= margin_left + indent_threshold
    )
    recurring_indents = {offset for offset, count in indent_offsets.items() if count >= 2}

    def is_recurring_indent(line: VisualLine) -> bool:
        offset = line.left - margin_left
        return any(abs(offset - indent) <= 4.0 for indent in recurring_indents)

    current: list[VisualLine] = []

    def flush() -> None:
        if current:
            text = clean_text(" ".join(line.text for line in current))
            if text:
                blocks.append(ContentBlock(current[0].top, "paragraph", text=text, bold=all(line.bold for line in current), italic=all(line.italic for line in current)))
            current.clear()

    previous_index: int | None = None
    for index, line in enumerate(lines):
        if index in table_by_start:
            flush()
            indices, rows = table_by_start[index]
            blocks.append(ContentBlock(line.top, "table", rows=rows))
            previous_index = max(indices)
            continue
        if index in table_indices:
            continue
        if index in list_heading_indices:
            flush()
            blocks.append(ContentBlock(line.top, "paragraph", text=line.text, bold=line.bold, italic=line.italic))
            previous_index = index
            continue
        previous_heading = blocks[-1] if blocks and not current and blocks[-1].kind == "heading" else None
        combined_heading = clean_text(f"{previous_heading.text} {line.text}") if previous_heading else line.text
        structural_heading = looks_structural_heading(line)
        heading_font_tolerance = 0.12 if previous_heading and previous_heading.bold else 0.08
        continuation_style = bool(
            previous_heading
            and previous_heading.font_size
            and abs(previous_heading.font_size - line.font_size)
            <= max(previous_heading.font_size, line.font_size) * heading_font_tolerance
            and previous_heading.bold == line.bold
            and (previous_heading.bold or line.bold or previous_heading.font_size >= body_size * 1.25)
        )
        continues_heading = bool(
            previous_heading
            and index not in prose_indices
            and not structural_heading
            and continuation_style
            and line.top - (previous_heading.last_top if previous_heading.last_top is not None else previous_heading.top)
            <= max(previous_heading.font_size, line.font_size) * 2.3
            and len(combined_heading) <= 240
            and not is_finished(line.text)
        )
        if continues_heading and previous_heading is not None:
            previous_heading.text = clean_text(f"{previous_heading.text} {line.text}")
            previous_heading.italic = previous_heading.italic and line.italic
            previous_heading.last_top = line.top
            previous_index = index
            continue
        if (index not in prose_indices or structural_heading) and looks_heading(line, body_size):
            flush()
            previous = blocks[-1] if blocks else None
            same_heading_style = bool(
                previous
                and previous.kind == "heading"
                and previous.font_size
                and abs(previous.font_size - line.font_size) <= max(previous.font_size, line.font_size) * 0.12
                and previous.bold == line.bold
                and not structural_heading
                and line.top - previous.top <= max(previous.font_size, line.font_size) * 1.75
            )
            if same_heading_style and previous is not None:
                previous.text = clean_text(f"{previous.text} {line.text}")
                previous.bold = previous.bold and line.bold
                previous.italic = previous.italic and line.italic
                previous.last_top = line.top
            else:
                blocks.append(ContentBlock(line.top, "heading", text=line.text, bold=line.bold, italic=line.italic, font_size=line.font_size, last_top=line.top))
            previous_index = index
            continue
        if current:
            previous = current[-1]
            previous_letters = [char for char in previous.text if char.isalpha()]
            current_letters = [char for char in line.text if char.isalpha()]
            continues_display = bool(
                line.bold
                and all(item.bold for item in current)
                and previous_letters
                and current_letters
                and sum(char.isupper() for char in previous_letters) / len(previous_letters) >= 0.78
                and sum(char.isupper() for char in current_letters) / len(current_letters) >= 0.78
                and abs(previous.font_size - line.font_size) <= max(previous.font_size, line.font_size) * 0.12
                and line.top - previous.top <= max(previous.font_size, line.font_size) * 1.75
            )
            line_gap = line.top - previous.top
            has_extra_vertical_space = line_gap > max(previous.height * 1.28, body_size * 1.45)
            starts_indented_paragraph = (
                line.left >= margin_left + indent_threshold
                and (is_recurring_indent(line) or has_extra_vertical_space)
            )
            if not continues_display and (
                (previous_index is not None and index != previous_index + 1)
                or starts_indented_paragraph
                or line_gap > max(previous.height * 1.35, body_size * 1.8)
            ):
                flush()
        current.append(line)
        previous_index = index
    flush()
    page_text = " ".join(line.text for line in lines)
    page_quotes = quote_matches(page_text)
    dialogue_page = len(page_quotes) >= 4 or sum(1 for match in page_quotes if spoken_quote(match)) >= 2
    leading_quoted_speech = any(
        block.kind == "paragraph"
        and (match := leading_quote(block.text))
        and spoken_quote(match)
        for block in blocks
    )
    if blocks:
        separated: list[ContentBlock] = []
        for block in blocks:
            starts_quoted_speech = bool(
                block.kind == "paragraph"
                and (match := leading_quote(block.text))
                and spoken_quote(match)
            )
            dialogue_split = dialogue_parts(block.text, force=dialogue_page) if block.kind == "paragraph" and (dialogue_page or starts_quoted_speech) else [block.text]
            parts = [part for item in dialogue_split for part in (long_prose_parts(item) if block.kind == "paragraph" else [item])]
            for offset, part in enumerate(parts):
                separated.append(ContentBlock(block.top + offset * 0.001, block.kind, text=part, rows=block.rows, image=block.image, bold=block.bold, italic=block.italic, font_size=block.font_size, page_anchor=block.page_anchor if offset == 0 else None))
        blocks = separated
    blocks.extend(ContentBlock(image.top, "image", image=image) for image in page.images)
    blocks.sort(key=lambda block: block.top)
    if blocks:
        blocks[0].page_anchor = page.number
    return blocks


def render_linked_text(text: str) -> str:
    result: list[str] = []
    cursor = 0
    for match in URL_RE.finditer(text):
        result.append(escape(text[cursor:match.start()]))
        label = match.group(0)
        trailing = ""
        while label and label[-1] in ".,;:!?)]":
            trailing = label[-1] + trailing
            label = label[:-1]
        href = label if label.startswith("http") else "https://" + label
        result.append(f'<a href="{escape(href, quote=True)}">{escape(label)}</a>')
        result.append(escape(trailing))
        cursor = match.end()
    result.append(escape(text[cursor:]))
    return "".join(result)


def render_table(rows: list[list[str]], anchor: str) -> str:
    head = "".join(f'<th scope="col">{render_linked_text(cell)}</th>' for cell in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{render_linked_text(cell)}</td>" for cell in row) + "</tr>" for row in rows[1:])
    return f'<div class="pdf-table-wrap"{anchor}><table class="pdf-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def hybrid_html(pages: list[PdfPage], title: str, css_href: str, script_href: str, pdf_name: str, image_urls: dict[tuple[int, int], str]) -> str:
    repeated = repeated_furniture(pages)
    body = [warning_html(pdf_name).strip()]
    for page in pages:
        for block in page_blocks(page, repeated):
            anchor = f' id="page_{block.page_anchor}"' if block.page_anchor else ""
            if block.kind in {"heading", "title"}:
                text = render_linked_text(block.text)
                level = 1 if block.kind == "title" else 2
                body.append(f"<h{level}{anchor}>{'<em>' + text + '</em>' if block.italic else text}</h{level}>")
            elif block.kind == "table":
                body.append(render_table(block.rows, anchor))
            elif block.kind == "image" and block.image:
                url = image_urls.get((block.image.page, block.image.index))
                if url:
                    body.append(f'<figure class="pdf-figure"{anchor}><img src="{escape(url, quote=True)}" width="{int(block.image.width)}" height="{int(block.image.height)}" loading="lazy" alt="Figure from PDF page {block.image.page}"/><figcaption>Figure from PDF page {block.image.page}</figcaption></figure>')
            else:
                text = render_linked_text(block.text)
                if block.bold:
                    text = f"<strong>{text}</strong>"
                if block.italic:
                    text = f"<em>{text}</em>"
                body.append(f"<p{anchor}>{text}</p>")
    document = f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml"><head><title>{escape(title)}</title>
<meta content="PDF Reflow conversion" name="generator"/><meta content="Poppler XML hybrid conversion" name="pdf-conversion-engine"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
{ANALYTICS}<link rel="stylesheet" type="text/css" href="{escape(css_href, quote=True)}"/></head><body class="pdf-reflow">
{os.linesep.join(body)}<script defer="defer" src="{escape(script_href, quote=True)}"></script></body></html>"""
    return repair_source(document, pdf_name)[0]


def blocks_for_page(page: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for raw_line in page.replace("\r", "").split("\n"):
        line = clean_text(raw_line)
        if not line:
            if current:
                blocks.append(current)
                current = []
        elif current and line.startswith(("— ", "– ")):
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def is_heading(text: str) -> bool:
    letters = [char for char in text if char.isalpha()]
    ratio = sum(char.isupper() for char in letters) / max(1, len(letters))
    return len(text) <= 110 and not TERMINAL_RE.search(text) and (ratio > 0.72 or len(text.split()) <= 10)


def pdf_text_to_html(raw_text: str, title: str, css_href: str, script_href: str, pdf_name: str) -> str:
    body = [warning_html(pdf_name).strip()]
    for page_number, page in enumerate((page for page in raw_text.split(PAGE_BREAK) if page.strip()), start=1):
        for index, lines in enumerate(blocks_for_page(page)):
            text = " ".join(lines)
            tag = "h2" if is_heading(text) else "p"
            anchor = f' id="page_{page_number}"' if index == 0 else ""
            body.append(f"<{tag}{anchor}>{render_linked_text(text)}</{tag}>")
    document = f'<html><head><title>{escape(title)}</title><meta content="PDF Reflow conversion" name="generator"/>{ANALYTICS}<link rel="stylesheet" href="{escape(css_href, quote=True)}"/></head><body>{"".join(body)}<script defer="defer" src="{escape(script_href, quote=True)}"></script></body></html>'
    return repair_source(document, pdf_name)[0]


def extract_title(pdf_path: Path) -> str:
    try:
        output = subprocess.run(["pdfinfo", str(pdf_path)], check=True, text=True, capture_output=True, timeout=30).stdout
        for line in output.splitlines():
            if line.startswith("Title:") and line.partition(":")[2].strip():
                title = line.partition(":")[2].strip()
                return title.replace("_", " ") if " " not in title else title
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return pdf_path.stem.replace("_", " ").strip()


def convert_pdf(pdf_path: Path, force: bool = False) -> str:
    pdf_path = pdf_path.resolve()
    try:
        html_path = html_for_pdf(pdf_path)
    except ValueError as error:
        raise ValueError(f"PDF must be under {CONTENT_ROOT}/<LANG>/") from error
    if pdf_path.suffix.lower() != ".pdf" or not pdf_path.is_file():
        raise ValueError(f"not a PDF file: {pdf_path}")
    if html_path.exists() and html_path.stat().st_mtime_ns >= pdf_path.stat().st_mtime_ns and not force:
        return f"up to date: {html_path.relative_to(REPO_ROOT)}"
    if shutil.which("pdftohtml") is None:
        raise RuntimeError("pdftohtml (Poppler) is required but was not found")
    with tempfile.TemporaryDirectory(prefix="pdf-hybrid-") as temporary:
        xml_path = Path(temporary) / "document.xml"
        subprocess.run(["pdftohtml", "-q", "-xml", "-hidden", "-enc", "UTF-8", str(pdf_path), str(xml_path)], check=True, text=True, capture_output=True)
        pages = parse_pdf_xml(xml_path)
        decorative_images = remove_repeated_template_images(pages)
        images = [image for page in pages for image in page.images if image.source.is_file()]
        assets_dir = html_path.with_suffix(".assets")
        image_urls: dict[tuple[int, int], str] = {}
        staged: list[tuple[Path, Path]] = []
        for image in images:
            suffix = image.source.suffix.lower() or ".png"
            filename = f"page-{image.page:04d}-image-{image.index:02d}{suffix}"
            staged.append((image.source, assets_dir / filename))
            image_urls[(image.page, image.index)] = f"{quote(assets_dir.name)}/{quote(filename)}"
        reader_dir = REPO_ROOT / "docs" / "reader"
        css_href = Path(os.path.relpath(reader_dir / "standalone.css", html_path.parent)).as_posix() + "?v=20260828-1"
        script_href = Path(os.path.relpath(reader_dir / "standalone.js", html_path.parent)).as_posix() + "?v=20260824-1"
        pdf_href = Path(os.path.relpath(pdf_path, html_path.parent)).as_posix()
        document = hybrid_html(pages, extract_title(pdf_path), css_href, script_href, pdf_href, image_urls)
        if assets_dir.exists():
            shutil.rmtree(assets_dir)
        if staged:
            assets_dir.mkdir(parents=True, exist_ok=True)
            for source, destination in staged:
                shutil.copy2(source, destination)
        html_path.write_text(document, encoding="utf-8")
    decorative_note = f", {decorative_images} repeated decoration(s) omitted" if decorative_images else ""
    return f"converted: {pdf_path.relative_to(REPO_ROOT)} -> {html_path.relative_to(REPO_ROOT)} ({len(images)} image(s), {document.count('class=\"pdf-table\"')} table(s){decorative_note})"


def selected_pdfs(raw_paths: list[str], convert_all: bool) -> list[Path]:
    paths = list((CONTENT_ROOT / "EN").glob("*.pdf")) if convert_all else [Path(raw) for raw in raw_paths]
    return sorted({path.resolve() for path in paths})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="*", help="PDF files under docs/content/<LANG>/")
    parser.add_argument("--all", action="store_true", help="convert every book PDF")
    parser.add_argument("--force", action="store_true", help="reconvert even when HTML is newer")
    parser.add_argument("--jobs", type=int, default=1, help="parallel conversions")
    args = parser.parse_args(argv)
    pdfs = selected_pdfs(args.pdfs, args.all)
    if not pdfs:
        parser.error("provide PDFs or use --all")
    failures = 0
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
        futures = {executor.submit(convert_pdf, pdf, args.force): pdf for pdf in pdfs}
        for future in as_completed(futures):
            try:
                print(future.result(), flush=True)
            except Exception as error:
                failures += 1
                print(f"failed: {futures[future]}: {error}", file=sys.stderr, flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
