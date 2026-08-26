#!/usr/bin/env python3
"""Audit and repair the HTML editions generated from PDFs for the inline reader.

The implementation deliberately edits only direct children of ``<body>`` in files
marked as ``PDF Reflow conversion``.  It preserves all visible source tokens while
joining layout-induced paragraph fragments and adding dialogue line breaks.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import sys
from typing import Iterable
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTENT_ROOT = REPO_ROOT / "docs" / "content"
HTML_ROOT = CONTENT_ROOT / "htmls"
LANGUAGE_RE = re.compile(r"^[A-Z]{2}$")
GENERATOR_MARKER = '<meta content="PDF Reflow conversion" name="generator"/>'
ANALYTICS = (
    '<script defer src="https://cloud.umami.is/script.js" '
    'data-website-id="e252999d-4479-42d7-9526-5f778846d4f6"></script>'
)
WARNING_ATTRIBUTE = 'data-pdf-conversion-warning="true"'
REPAIR_VERSION = "3"
PROCESSED_MARKER = f'<meta content="{REPAIR_VERSION}" name="pdf-reflow-repair"/>'
PROCESSED_META_RE = re.compile(r'<meta\s+[^>]*name=["\']pdf-reflow-repair["\'][^>]*/?>', re.IGNORECASE)
TAG_RE = re.compile(r"<!--.*?-->|<[^>]+>", re.DOTALL)
SPACE_RE = re.compile(r"\s+")
PAGE_ID_RE = re.compile(r"^page_\d+$")
TERMINAL_RE = re.compile(r"[.!?…]\s*[\"'”’»“„«‹）\)\]]*$")
DIALOG_START_RE = re.compile(r"^(?:[\s\"'“”„‘«‹（\(\[]*[—–]\s+|\s*[\"“„«‹]\s*\S)")
DIALOG_JOIN_RE = re.compile(r'([.!?…][\"”’»]?)([ \t]+)(?=[—–][ \t]+\S)')
LIST_START_RE = re.compile(r"^\s*(?:[•◦▪‣]|\(?\d{1,3}[.)]\s|[A-Za-z][.)]\s)")


@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None]
    start: int
    start_end: int
    close_start: int
    end: int

    def inner(self, source: str) -> str:
        return source[self.start_end : self.close_start]

    def raw(self, source: str) -> str:
        return source[self.start : self.end]

    @property
    def page_id(self) -> str | None:
        value = self.attrs.get("id")
        return value if value and PAGE_ID_RE.fullmatch(value) else None


class BodyChildrenParser(HTMLParser):
    """Collect exact character spans for direct element children of body."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_starts = [0]
        for match in re.finditer("\n", source):
            self.line_starts.append(match.end())
        self.stack: list[tuple[str, Node | None]] = []
        self.in_body = False
        self.body_start_end: int | None = None
        self.body_close_start: int | None = None
        self.nodes: list[Node] = []

    def source_offset(self) -> int:
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        start = self.source_offset()
        raw = self.get_starttag_text()
        start_end = start + len(raw)
        if tag == "body":
            self.in_body = True
            self.body_start_end = start_end
            self.stack.append((tag, None))
            return
        direct = self.in_body and self.stack and self.stack[-1][0] == "body"
        node = Node(tag, dict(attrs), start, start_end, start_end, start_end) if direct else None
        if tag in self.VOID:
            if node is not None:
                self.nodes.append(node)
            return
        self.stack.append((tag, node))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        start = self.source_offset()
        end = start + len(self.get_starttag_text())
        if self.in_body and self.stack and self.stack[-1][0] == "body":
            self.nodes.append(Node(tag.lower(), dict(attrs), start, end, end, end))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        start = self.source_offset()
        end = self.source.find(">", start)
        end = len(self.source) if end < 0 else end + 1
        if tag == "body":
            self.body_close_start = start
            self.in_body = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] != tag:
                continue
            _, node = self.stack[index]
            del self.stack[index:]
            if node is not None:
                node.close_start = start
                node.end = end
                self.nodes.append(node)
            break


def parse_body(source: str) -> BodyChildrenParser:
    parser = BodyChildrenParser(source)
    parser.feed(source)
    parser.nodes.sort(key=lambda node: node.start)
    if parser.body_start_end is None or parser.body_close_start is None:
        raise ValueError("document has no complete <body> element")
    return parser


def visible(raw: str) -> str:
    return SPACE_RE.sub(" ", unescape(TAG_RE.sub(" ", raw))).strip().replace("\u200b", "")


def node_text(node: Node, source: str) -> str:
    return visible(node.inner(source))


def starts_lower(text: str) -> bool:
    for char in text:
        if char.isalpha():
            return char.islower()
        if char.isdigit():
            return False
    return False


def is_finished(text: str) -> bool:
    return bool(TERMINAL_RE.search(text.rstrip()))


def is_blank(text: str) -> bool:
    return not text.replace("\xa0", "").strip()


def is_page_number(text: str) -> bool:
    return bool(
        re.fullmatch(
            r"\s*(?:[—–−-]+\s*)?(?:(?:Page\s+)\d{1,4}(?:\s*(?:/|of)\s*\d{1,4})?|\d{1,3}(?:\s*(?:/|of)\s*\d{1,3})?)(?:\s*[—–−|·•*_=~.:-]+)?\s*",
            text,
            re.IGNORECASE,
        )
    )


def looks_like_heading(node: Node, text: str, source: str) -> bool:
    if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return True
    if not text:
        return False
    letters = [char for char in text if char.isalpha()]
    uppercase_ratio = sum(char.isupper() for char in letters) / max(1, len(letters))
    raw = node.inner(source).lower()
    if len(text) <= 120 and uppercase_ratio >= 0.78:
        return True
    if len(text) <= 90 and ("<b" in raw or "<strong" in raw or "<i" in raw or "<em" in raw):
        return True
    if len(text) <= 140 and re.search(r"\.{4,}\s*\d*\s*$", text):
        return True
    return False


def paragraph_nodes(parser: BodyChildrenParser) -> list[Node]:
    return [node for node in parser.nodes if node.tag == "p"]


def semantic_paragraphs(parser: BodyChildrenParser, source: str) -> list[Node]:
    return [node for node in paragraph_nodes(parser) if not is_blank(node_text(node, source))]


def repeated_page_headers(parser: BodyChildrenParser, source: str) -> set[str]:
    counts = Counter(
        node_text(node, source)
        for node in parser.nodes
        if node.page_id and not is_blank(node_text(node, source))
    )
    return {text for text, count in counts.items() if count >= 3}


def candidate_edges(parser: BodyChildrenParser, source: str) -> list[tuple[Node, Node]]:
    """Return pairs whose paragraph boundary came from PDF layout."""
    nodes = parser.nodes
    position = {id(node): index for index, node in enumerate(nodes)}
    texts = {id(node): node_text(node, source) for node in nodes}
    semantic = [node for node in nodes if node.tag == "p" and not is_blank(texts[id(node)])]
    edges: list[tuple[Node, Node]] = []

    # Physical PDF lines emitted as paragraphs, sometimes separated by any
    # number of empty paragraphs or a bare page number.
    for previous, current in zip(semantic, semantic[1:]):
        previous_text = texts[id(previous)]
        current_text = texts[id(current)]
        between = nodes[position[id(previous)] + 1 : position[id(current)]]
        if any(
            node.tag != "p" or (not is_blank(texts[id(node)]) and not is_page_number(texts[id(node)]))
            for node in between
        ):
            continue
        if is_page_number(previous_text) or is_page_number(current_text):
            continue
        if previous.page_id or current.page_id:
            continue
        if is_finished(previous_text):
            continue
        if DIALOG_START_RE.match(current_text):
            continue
        if LIST_START_RE.match(current_text):
            continue
        if looks_like_heading(previous, previous_text, source) or looks_like_heading(current, current_text, source):
            continue
        # Once headings, lists, page furniture and dialogue starts are excluded,
        # an unfinished preceding paragraph is treated as a wrapped line even
        # when the continuation begins with a proper name or quotation.
        edges.append((previous, current))

    # Sentences interrupted by page furniture and a repeated running header.
    marker_counts = Counter(texts[id(node)] for node in nodes if node.page_id and not is_blank(texts[id(node)]))
    repeated_headers = {text for text, count in marker_counts.items() if count >= 3}
    for marker_index, marker in enumerate(nodes):
        if not marker.page_id:
            continue
        marker_text = texts[id(marker)]
        if marker_text in repeated_headers:
            continuation = next(
                (
                    node
                    for node in nodes[marker_index + 1 :]
                    if node.tag == "p" and not is_blank(texts[id(node)]) and not is_page_number(texts[id(node)])
                ),
                None,
            )
        else:
            continuation = (
                marker
                if marker.tag == "p" and not is_blank(marker_text) and not is_page_number(marker_text)
                else None
            )
        if continuation is None:
            continue
        previous = next(
            (
                node
                for node in reversed(nodes[:marker_index])
                if node.tag == "p" and not is_blank(texts[id(node)]) and not is_page_number(texts[id(node)])
            ),
            None,
        )
        if previous is None or previous is continuation:
            continue
        previous_text = texts[id(previous)]
        continuation_text = texts[id(continuation)]
        if is_finished(previous_text) or DIALOG_START_RE.match(continuation_text):
            continue
        if looks_like_heading(previous, previous_text, source) or looks_like_heading(continuation, continuation_text, source):
            continue
        edges.append((previous, continuation))

    # Deduplicate without relying on mutable dataclass hashing.
    seen: set[tuple[int, int]] = set()
    result: list[tuple[Node, Node]] = []
    for left, right in edges:
        key = (id(left), id(right))
        if key not in seen:
            seen.add(key)
            result.append((left, right))
    return result


def insert_dialog_breaks(inner: str) -> tuple[str, int]:
    """Insert visual line breaks without touching tags or visible characters."""
    parts = re.split(r"(<[^>]+>)", inner)
    count = 0
    for index in range(0, len(parts), 2):
        parts[index], added = DIALOG_JOIN_RE.subn(r'\1<br class="pdf-dialog-break"/>\2', parts[index])
        count += added
    return "".join(parts), count


def warning_html(pdf_href: str) -> str:
    href = quote(pdf_href)
    if not href.startswith((".", "/")):
        href = "./" + href
    return (
        '\n<aside data-pdf-conversion-warning="true" role="note" '
        'style="margin:1rem auto 2rem;max-width:52rem;padding:1rem 1.2rem;border:1px solid #c7962d;'
        'border-radius:.5rem;background:#fff8df;color:#3b2b08;font:16px/1.5 system-ui,sans-serif">'
        '<strong>Conversion notice:</strong> This HTML edition was generated automatically from the PDF. '
        'Some figures and formatting may be missing or simplified. '
        f'<a href="{href}">The original PDF is available here.</a></aside>\n'
    )


def content_token_counter(source: str) -> Counter[str]:
    parser = parse_body(source)
    tokens: Counter[str] = Counter()
    for node in parser.nodes:
        if WARNING_ATTRIBUTE in node.raw(source):
            continue
        if node.tag == "p" and is_page_number(node_text(node, source)):
            continue
        tokens.update(re.findall(r"\S+", node_text(node, source)))
    return tokens


def apply_once(source: str, pdf_href: str) -> tuple[str, Counter[str]]:
    parser = parse_body(source)
    stats: Counter[str] = Counter()
    replacements: list[tuple[int, int, str]] = []

    edges = candidate_edges(parser, source)
    parents: dict[int, int] = {}
    node_by_id = {id(node): node for node in paragraph_nodes(parser)}

    def find(value: int) -> int:
        parents.setdefault(value, value)
        while parents[value] != value:
            parents[value] = parents[parents[value]]
            value = parents[value]
        return value

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    for left, right in edges:
        union(id(left), id(right))

    groups: dict[int, list[Node]] = {}
    for value in list(parents):
        groups.setdefault(find(value), []).append(node_by_id[value])
    group_members = {id(node) for group in groups.values() for node in group}

    for group in groups.values():
        group.sort(key=lambda node: node.start)
        root = group[0]
        joined = ""
        for index, node in enumerate(group):
            if index:
                joined += " "
            joined += node.inner(source)
        joined, dialog_count = insert_dialog_breaks(joined)
        stats["dialog_breaks"] += dialog_count
        replacements.append((root.start_end, root.close_start, joined))
        for node in group[1:]:
            placeholder = f'<span id="{node.page_id}" class="pdf-page-anchor"></span>' if node.page_id else ""
            replacements.append((node.start, node.end, placeholder))
        stats["paragraph_joins"] += len(group) - 1

    for node in paragraph_nodes(parser):
        if id(node) in group_members:
            continue
        changed, dialog_count = insert_dialog_breaks(node.inner(source))
        if dialog_count:
            replacements.append((node.start_end, node.close_start, changed))
            stats["dialog_breaks"] += dialog_count

    # Empty layout paragraphs create very large vertical gaps in a reflowable
    # reader. Paragraph margins already provide the semantic separation.
    for node in paragraph_nodes(parser):
        if id(node) in group_members:
            continue
        text = node_text(node, source)
        if is_blank(text):
            placeholder = f'<span id="{node.page_id}" class="pdf-page-anchor"></span>' if node.page_id else ""
            replacements.append((node.start, node.end, placeholder))
            stats["blank_paragraphs_removed"] += 1
        elif is_page_number(text):
            placeholder = f'<span id="{node.page_id}" class="pdf-page-anchor"></span>' if node.page_id else ""
            replacements.append((node.start, node.end, placeholder))
            stats["page_numbers_removed"] += 1

    if WARNING_ATTRIBUTE not in source:
        replacements.append((parser.body_start_end, parser.body_start_end, warning_html(pdf_href)))
        stats["warnings_added"] += 1

    if PROCESSED_MARKER not in source:
        old_marker = PROCESSED_META_RE.search(source)
        if old_marker:
            replacements.append((old_marker.start(), old_marker.end(), PROCESSED_MARKER))
        else:
            head_close = source.lower().find("</head>")
            if head_close < 0:
                raise ValueError("document has no closing </head> element")
            replacements.append((head_close, head_close, f"  {PROCESSED_MARKER}\n"))
        stats["markers_added"] += 1

    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source, stats


def repair_source(source: str, pdf_href: str) -> tuple[str, Counter[str]]:
    before_tokens = content_token_counter(source)
    total: Counter[str] = Counter()
    for _ in range(128):
        source, stats = apply_once(source, pdf_href)
        total.update(stats)
        if not any(stats.values()):
            break
    else:
        raise RuntimeError("repair did not become idempotent after 128 passes")
    # Source-only whitespace between elements has no semantic value. Keep at
    # most one physical newline so generated files remain inspectable as well.
    source = re.sub(r">[ \t]*\n(?:[ \t]*\n)+[ \t]*<", ">\n<", source)
    after_tokens = content_token_counter(source)
    if before_tokens != after_tokens:
        missing = before_tokens - after_tokens
        added = after_tokens - before_tokens
        raise ValueError(f"visible text integrity check failed; missing={missing.most_common(5)}, added={added.most_common(5)}")
    return source, total


def pdf_for_html(path: Path) -> Path:
    """Return the language PDF paired with an HTML edition."""
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(HTML_ROOT)
    except ValueError:
        # Low-level repair helpers remain usable for isolated fixtures. Public
        # discovery below still enforces the repository's content layout.
        return resolved.with_suffix(".pdf")
    if len(relative.parts) != 2 or not LANGUAGE_RE.fullmatch(relative.parts[0]):
        raise ValueError(f"HTML edition must be under {HTML_ROOT}/<LANG>/")
    return (CONTENT_ROOT / relative).with_suffix(".pdf")


def html_for_pdf(path: Path) -> Path:
    """Return the generated HTML path paired with a language PDF."""
    relative = path.resolve().relative_to(CONTENT_ROOT)
    if len(relative.parts) != 2 or not LANGUAGE_RE.fullmatch(relative.parts[0]):
        raise ValueError(f"PDF edition must be under {CONTENT_ROOT}/<LANG>/")
    return (HTML_ROOT / relative).with_suffix(".html")


def relative_pdf_href(html_path: Path) -> str:
    return Path(os.path.relpath(pdf_for_html(html_path), html_path.parent)).as_posix()


def is_supported_html(path: Path, source: str | None = None) -> bool:
    try:
        pdf_path = pdf_for_html(path)
    except ValueError:
        return False
    if path.suffix.lower() != ".html" or not pdf_path.is_file():
        return False
    if source is None:
        source = path.read_text(encoding="utf-8")
    return "PDF Reflow conversion" in source


def discover_html(paths: Iterable[str] | None = None) -> list[Path]:
    if paths:
        candidates: list[Path] = []
        for raw in paths:
            path = Path(raw).resolve()
            if path.is_dir():
                candidates.extend(path.rglob("*.html"))
            else:
                candidates.append(path)
    else:
        candidates = list(HTML_ROOT.rglob("*.html"))
    result = []
    for path in sorted(set(candidates)):
        try:
            path.relative_to(HTML_ROOT)
            pdf_path = pdf_for_html(path)
        except ValueError:
            continue
        # Exact PDF/HTML basename pairs define reader support. Keep discovery
        # metadata-only so the stale command never scans book contents.
        if path.is_file() and path.suffix.lower() == ".html" and pdf_path.is_file():
            result.append(path)
    return result


def stale_pairs(paths: Iterable[Path] | None = None) -> list[tuple[Path, Path]]:
    html_paths = list(paths) if paths is not None else discover_html()
    result = []
    for html_path in html_paths:
        pdf_path = pdf_for_html(html_path)
        if html_path.stat().st_mtime_ns < pdf_path.stat().st_mtime_ns:
            result.append((html_path, pdf_path))
    return result


def fix_files(paths: list[Path], dry_run: bool = False, force: bool = False) -> Counter[str]:
    totals: Counter[str] = Counter(files_scanned=len(paths))
    for path in paths:
        with path.open("r", encoding="utf-8") as stream:
            prefix = stream.read(8192)
        if PROCESSED_MARKER in prefix and not force:
            totals["files_skipped_marker"] += 1
            continue
        source = path.read_text(encoding="utf-8")
        if not is_supported_html(path, source):
            totals["files_skipped_unsupported"] += 1
            continue
        repaired, stats = repair_source(source, relative_pdf_href(path))
        totals.update(stats)
        if repaired != source:
            totals["files_changed"] += 1
            if not dry_run:
                original_stat = path.stat()
                path.write_text(repaired, encoding="utf-8")
                # Repairing an edition must not hide that its PDF is newer.
                os.utime(path, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
    return totals


def audit_files(paths: list[Path]) -> tuple[Counter[str], list[str]]:
    totals: Counter[str] = Counter(files_scanned=len(paths))
    problems: list[str] = []
    for path in paths:
        with path.open("r", encoding="utf-8") as stream:
            prefix = stream.read(8192)
        if PROCESSED_MARKER in prefix:
            totals["files_skipped_marker"] += 1
            continue
        source = path.read_text(encoding="utf-8")
        if not is_supported_html(path, source):
            totals["files_skipped_unsupported"] += 1
            continue
        try:
            parser = parse_body(source)
        except ValueError as error:
            problems.append(f"{path.relative_to(REPO_ROOT)}: {error}")
            continue
        analytics_count = source.count(ANALYTICS)
        warning_count = source.count(WARNING_ATTRIBUTE)
        remaining_edges = len(candidate_edges(parser, source))
        remaining_dialogs = sum(
            len(DIALOG_JOIN_RE.findall(part))
            for node in paragraph_nodes(parser)
            for part in re.split(r"(<[^>]+>)", node.inner(source))[::2]
        )
        if analytics_count != 1:
            problems.append(f"{path.relative_to(REPO_ROOT)}: analytics script count is {analytics_count}, expected 1")
        if warning_count != 1:
            problems.append(f"{path.relative_to(REPO_ROOT)}: conversion warning count is {warning_count}, expected 1")
        if remaining_edges:
            problems.append(f"{path.relative_to(REPO_ROOT)}: {remaining_edges} likely broken paragraph boundary/boundaries")
        if remaining_dialogs:
            problems.append(f"{path.relative_to(REPO_ROOT)}: {remaining_dialogs} dialogue break(s) still missing")
        totals["remaining_edges"] += remaining_edges
        totals["remaining_dialogs"] += remaining_dialogs
    totals["stale_files"] = len(stale_pairs(paths))
    return totals, problems


def print_stale(paths: list[Path] | None = None) -> int:
    pairs = stale_pairs(paths)
    if not pairs:
        print("No HTML edition is older than its matching PDF.")
        return 0
    print("HTML editions older than their matching PDF (conversion required):")
    for html_path, pdf_path in pairs:
        print(f"- {html_path.relative_to(REPO_ROOT)} <- {pdf_path.relative_to(REPO_ROOT)}")
    return len(pairs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("fix", "audit"):
        child = subparsers.add_parser(command)
        child.add_argument("paths", nargs="*", help="Book HTML files or directories (default: all supported editions)")
        if command == "fix":
            child.add_argument("--dry-run", action="store_true")
            child.add_argument("--force", action="store_true", help="repair even files carrying the current marker")
    stale_parser = subparsers.add_parser("stale")
    stale_parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    paths = discover_html(getattr(args, "paths", None))
    if args.command == "fix":
        stats = fix_files(paths, args.dry_run, args.force)
        print(
            f"Scanned {stats['files_scanned']} files; changed {stats['files_changed']}; "
            f"skipped {stats['files_skipped_marker']} already-marked files; "
            f"joined {stats['paragraph_joins']} paragraph fragments; "
            f"removed {stats['blank_paragraphs_removed']} empty paragraphs and {stats['page_numbers_removed']} page numbers; "
            f"inserted {stats['dialog_breaks']} dialogue breaks; added {stats['warnings_added']} warnings."
        )
        print_stale(paths)
        return 0
    if args.command == "audit":
        stats, problems = audit_files(paths)
        for problem in problems:
            print(problem)
        print(
            f"Audited {stats['files_scanned']} files; {len(problems)} problem report(s); "
            f"{stats['stale_files']} conversion(s) required."
        )
        return 1 if problems else 0
    print_stale(paths)
    return 0


if __name__ == "__main__":
    sys.exit(main())
