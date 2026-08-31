from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "content" / "tools"))
from book_html import ANALYTICS, PROCESSED_MARKER, audit_files, fix_files, repair_source, stale_pairs  # noqa: E402
from convert_book_pdf import ImageBox, PdfPage, dialogue_parts, hybrid_html, long_prose_parts, parse_pdf_xml, pdf_text_to_html, remove_repeated_template_images  # noqa: E402


def document(body: str) -> str:
    return f"""<?xml version='1.0' encoding='utf-8'?>
<html><head><meta content="PDF Reflow conversion" name="generator"/>{ANALYTICS}</head>
<body>{body}</body></html>"""


class RepairTests(unittest.TestCase):
    def test_joins_wrapped_physical_lines_without_losing_text(self):
        source = document(
            '<p class="body">This is a deliberately long physical line that has no sentence ending and therefore</p>'
            '<p class="body">continues on the next extracted line without becoming a new paragraph.</p>'
        )
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["paragraph_joins"], 1)
        self.assertIn("therefore continues", repaired)
        self.assertNotIn("therefore</p><p", repaired)

    def test_joins_line_fragments_when_the_first_fragment_carries_a_page_anchor(self):
        source = document(
            '<p id="page_9">That evening Daniel stood beneath the apple tree planted for his</p>'
            '<p>daughter and listened to the distant machinery clearing the road.</p>'
        )
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["paragraph_joins"], 1)
        self.assertIn("for his daughter and listened", repaired)
        self.assertEqual(repaired.count('id="page_9"'), 1)

    def test_joins_short_fragment_before_uppercase_continuation(self):
        source = document('<p>She finally saw</p><p>&nbsp;</p><p>Maria crossing the square.</p>')
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["paragraph_joins"], 1)
        self.assertIn("saw Maria", repaired)

    def test_joins_across_empty_layout_paragraphs_and_removes_page_furniture(self):
        source = document(
            '<p>This short sentence fragment</p>\n\n'
            '<p>&nbsp;</p>\n<p>17</p>\n<p>\u00a0</p>\n\n'
            '<p>continues after absurd extraction whitespace.</p>'
        )
        repaired, stats = repair_source(source, "book.pdf")
        self.assertIn("fragment continues", repaired)
        self.assertEqual(stats["paragraph_joins"], 1)
        self.assertEqual(stats["page_numbers_removed"], 1)
        self.assertGreaterEqual(stats["blank_paragraphs_removed"], 2)
        self.assertNotRegex(repaired, r"<p[^>]*>\s*(?:&nbsp;|\u00a0)?\s*</p>")
        self.assertNotIn(">17</p>", repaired)
        self.assertNotIn("\n\n", repaired)

    def test_removes_decorated_page_number_but_keeps_meaningful_initial(self):
        source = document('<p>Text before.</p><p>— 37 —</p><p>E.</p><p>Text after.</p>')
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["page_numbers_removed"], 1)
        self.assertNotIn("— 37 —", repaired)
        self.assertIn("<p>E.</p>", repaired)

    def test_joins_sentence_across_repeated_page_header_and_keeps_anchor(self):
        source = document(
            '<p>This sufficiently long sentence crosses the physical PDF page and must remain one continuous</p>'
            '<p>1</p><p id="page_2">BOOK TITLE</p><p>paragraph in the reflowable edition.</p>'
            '<p>Complete sentence.</p><p>2</p><p id="page_3">BOOK TITLE</p><p>Complete sentence.</p>'
            '<p>Complete sentence.</p><p>3</p><p id="page_4">BOOK TITLE</p><p>Complete sentence.</p>'
        )
        repaired, stats = repair_source(source, "book.pdf")
        self.assertGreaterEqual(stats["paragraph_joins"], 1)
        self.assertIn("continuous paragraph", repaired)
        self.assertEqual(repaired.count('id="page_2"'), 1)

    def test_does_not_join_heading_or_new_dialogue(self):
        source = document(
            '<p><b>A deliberately long chapter heading that should stay separate from the following line</b></p>'
            '<p><i>chapter subtitle</i></p>'
            '<p>This sufficiently long narrative line intentionally introduces a speaker without punctuation</p>'
            '<p>— A new speaker remains on a new line.</p>'
        )
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["paragraph_joins"], 0)
        self.assertIn("</p><p><i>chapter subtitle", repaired)
        self.assertIn("</p><p>— A new speaker", repaired)

    def test_does_not_join_quoted_dialogue_to_unfinished_narration(self):
        source = document('<p>Narrative introduction without terminal punctuation</p><p>„Nu.”</p>')
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["paragraph_joins"], 0)
        self.assertIn('</p><p>„Nu.”</p>', repaired)

    def test_keeps_french_spaced_guillemets_and_german_quote_endings_separate(self):
        source = document(
            '<p>« Première réplique. »</p><p>« Deuxième réplique. »</p>'
            '<p>„Erste Replik.“</p><p>„Zweite Replik.“</p>'
        )
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["paragraph_joins"], 0)
        self.assertIn('»</p><p>«', repaired)
        self.assertIn('.“</p><p>„', repaired)

    def test_keeps_numbered_items_separate_while_reflowing_each_item(self):
        source = document(
            '<p>1. A deliberately long list item wraps at the physical edge of the PDF page and</p>'
            '<p>continues here without a semantic break</p>'
            '<p>2. The next numbered item must not be absorbed into the first item.</p>'
        )
        repaired, stats = repair_source(source, "book.pdf")
        self.assertEqual(stats["paragraph_joins"], 1)
        self.assertIn("and continues here", repaired)
        self.assertIn("</p><p>2. The next", repaired)

    def test_adds_dialogue_break_and_one_english_warning(self):
        source = document('<p>Narrative sentence. — Dialogue starts here.</p>')
        repaired, stats = repair_source(source, "A Book.pdf")
        self.assertEqual(stats["dialog_breaks"], 1)
        self.assertEqual(repaired.count('class="pdf-dialog-break"'), 1)
        self.assertEqual(repaired.count('data-pdf-conversion-warning="true"'), 1)
        self.assertEqual(repaired.count(PROCESSED_MARKER), 1)
        self.assertIn("Some figures and formatting may be missing or simplified", repaired)
        self.assertIn('href="./A%20Book.pdf"', repaired)
        second, second_stats = repair_source(repaired, "A Book.pdf")
        self.assertEqual(second, repaired)
        self.assertFalse(sum(second_stats.values()))

    def test_preserves_stale_mtime_when_repairing(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            folder = Path(temp_dir)
            pdf = folder / "sample.pdf"
            html = folder / "sample.html"
            pdf.write_bytes(b"pdf")
            html.write_text(document("<p>Text.</p>"), encoding="utf-8")
            old = 1_700_000_000_000_000_000
            new = old + 10_000_000_000
            os.utime(html, ns=(old, old))
            os.utime(pdf, ns=(new, new))
            # Direct helper accepts arbitrary paths; discovery is what enforces repo scope.
            fix_files([html])
            self.assertEqual(html.stat().st_mtime_ns, old)
            self.assertEqual(stale_pairs([html]), [(html, pdf)])
            second_stats = fix_files([html])
            self.assertEqual(second_stats["files_skipped_marker"], 1)
            forced_stats = fix_files([html], force=True)
            self.assertEqual(forced_stats["files_skipped_marker"], 0)
            self.assertEqual(forced_stats["files_changed"], 0)


class ConversionTests(unittest.TestCase):
    def test_splits_quoted_dialogue_from_narration_and_keeps_attribution(self):
        text = (
            'Nethra knew the history. "A connection is not consensual," she said. '
            '"It enters us through an opening." "Origaya is not using anything," Mirel said. '
            'She had come in person. "I built the translation." No defence followed.'
        )
        self.assertEqual(
            dialogue_parts(text),
            [
                "Nethra knew the history.",
                '"A connection is not consensual," she said. "It enters us through an opening."',
                '"Origaya is not using anything," Mirel said.',
                "She had come in person.",
                '"I built the translation."',
                "No defence followed.",
            ],
        )

    def test_splits_romanian_low_high_quotation_marks(self):
        self.assertEqual(
            dialogue_parts('Narațiune. „Prima replică.” „A doua replică.” Descriere.'),
            ['Narațiune.', '„Prima replică.”', '„A doua replică.”', 'Descriere.'],
        )

    def test_keeps_long_dialogue_introduction_as_narration(self):
        parts = dialogue_parts(
            '„Prima replică.“ Un membru al familiei întrebă de ce trebuie să accepte această probă dificilă. '
            '„A doua replică.“',
            force=True,
        )
        self.assertEqual(
            parts,
            [
                '„Prima replică.“',
                'Un membru al familiei întrebă de ce trebuie să accepte această probă dificilă.',
                '„A doua replică.“',
            ],
        )

    def test_recovers_inner_replies_when_outer_translation_quote_is_unclosed(self):
        parts = dialogue_parts(
            '„O introducere cu ghilimea rămasă deschisă. Narațiunea continuă. '
            '"Prima replică." Descriere separată. "A doua replică." Final narativ.',
            force=True,
        )
        self.assertEqual(
            parts,
            [
                '„O introducere cu ghilimea rămasă deschisă. Narațiunea continuă.',
                '"Prima replică."',
                'Descriere separată.',
                '"A doua replică."',
                'Final narativ.',
            ],
        )
        inverse = dialogue_parts(
            '"Introducere rămasă deschisă. „Prima replică.“ Descriere. „A doua replică.“',
            force=True,
        )
        self.assertEqual(inverse[1:], ['„Prima replică.“', 'Descriere.', '„A doua replică.“'])

    def test_collapses_absurd_toc_leader_without_retaining_page_number(self):
        from convert_book_pdf import clean_text
        self.assertEqual(clean_text("The Assembly................................................................ 27"), "The Assembly")

    def test_splits_long_prose_only_after_complete_sentences(self):
        text = "First complete sentence. " + "A" * 1100 + ". " + "B" * 1100 + ". Final sentence."
        parts = long_prose_parts(text, maximum=1200)
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(part.endswith((".", "!", "?", "…")) for part in parts))
        self.assertEqual(" ".join(parts), text)

    def test_removes_only_byte_identical_images_repeated_across_pages(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            folder = Path(temp_dir)
            template_files = []
            for index in range(3):
                path = folder / f"template-{index}.png"
                path.write_bytes(b"identical page decoration")
                template_files.append(path)
            figure = folder / "unique-figure.png"
            figure.write_bytes(b"unique figure")
            repeated_figures = []
            for index in range(3):
                path = folder / f"repeated-figure-{index}.png"
                path.write_bytes(b"same intentional body figure")
                repeated_figures.append(path)
            pages = [
                PdfPage(index + 1, 600, 800, [], [ImageBox(index + 1, 1, 0, 0, 600, 800, path)])
                for index, path in enumerate(template_files)
            ]
            for index, page in enumerate(pages):
                page.images.append(ImageBox(index + 1, 2, 250, 200, 180, 180, repeated_figures[index]))
            pages[1].images.append(ImageBox(2, 2, 200, 200, 100, 100, figure))
            removed = remove_repeated_template_images(pages)
        self.assertEqual(removed, 3)
        self.assertEqual([image.source for image in pages[0].images], [repeated_figures[0]])
        self.assertEqual([image.source for image in pages[1].images], [repeated_figures[1], figure])

    def test_converter_reflows_lines_pages_dialogue_and_reader_assets(self):
        raw = (
            "CHAPTER ONE\n\n"
            "A paragraph is wrapped by the PDF extraction at this physical\n"
            "line but remains a single logical\n\f"
            "paragraph. Narrative ends. — A speaker begins.\n"
        )
        converted = pdf_text_to_html(raw, "Example", "../../reader/standalone.css", "../../reader/standalone.js", "Example.pdf")
        self.assertIn("physical line but remains", converted)
        self.assertIn("logical paragraph", converted)
        self.assertIn('class="pdf-dialog-break"', converted)
        self.assertEqual(converted.count(ANALYTICS), 1)
        self.assertEqual(converted.count('data-pdf-conversion-warning="true"'), 1)
        self.assertIn("../../reader/standalone.css", converted)

    def test_hybrid_converter_preserves_table_and_image_in_reading_order(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="1" width="600" height="800">
<fontspec id="0" size="12" family="Serif"/>
<text top="100" left="50" width="80" height="16" font="0"><b>Chapter</b></text>
<text top="100" left="300" width="120" height="16" font="0"><b>Question</b></text>
<text top="130" left="50" width="120" height="16" font="0">1. Beginning</text>
<text top="130" left="300" width="140" height="16" font="0">Why does it start?</text>
<text top="160" left="50" width="100" height="16" font="0">2. Ending</text>
<text top="160" left="300" width="140" height="16" font="0">How does it finish?</text>
</page><page number="2" width="600" height="800">
<fontspec id="1" size="12" family="Serif"/>
<text top="80" left="50" width="200" height="16" font="1">A paragraph before the figure.</text>
<image top="180" left="120" width="360" height="220" src="figure.png"/>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "sample.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(
            pages,
            "Hybrid Example",
            "../../reader/standalone.css",
            "../../reader/standalone.js",
            "Hybrid.pdf",
            {(2, 1): "Hybrid.assets/page-0002-image-01.png"},
        )
        self.assertIn('class="pdf-table"', converted)
        self.assertIn("<th scope=\"col\">Chapter</th>", converted)
        self.assertIn("Why does it start?", converted)
        self.assertIn('class="pdf-figure"', converted)
        self.assertIn("Hybrid.assets/page-0002-image-01.png", converted)
        self.assertIn('name="pdf-conversion-engine"', converted)

    def test_hybrid_converter_recovers_indented_dialogue_and_narration_paragraphs(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="12" width="918" height="1188">
<fontspec id="0" size="18" family="Serif"/>
<text top="87" left="123" width="90" height="22" font="0">Felix oftă.</text>
<text top="118" left="123" width="430" height="22" font="0">— Nu trebuie să transformi fiecare cameră într-un tribunal.</text>
<text top="149" left="123" width="100" height="22" font="0">— Ethan—</text>
<text top="180" left="123" width="650" height="22" font="0">— Nu am de gând să mă lupt pentru dreptul de a vă avertiza și aceasta este o</text>
<text top="211" left="92" width="650" height="22" font="0">continuare a aceleiași replici.</text>
<text top="242" left="123" width="600" height="22" font="0">Ieși înainte ca propoziția să poată fi evaluată ca incident suplimentar.</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "dialogue.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Dialogue", "reader.css", "reader.js", "Dialogue.pdf", {})
        self.assertIn('<p id="page_12">Felix oftă.</p>\n<p>— Nu trebuie', converted)
        self.assertIn("</p>\n<p>— Ethan—</p>\n<p>— Nu am", converted)
        self.assertIn("avertiza și aceasta este o continuare a aceleiași replici.</p>", converted)
        self.assertIn("</p>\n<p>Ieși înainte", converted)

    def test_hybrid_converter_does_not_split_a_slightly_indented_wrapped_line(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="3" width="600" height="800">
<fontspec id="0" size="12" family="Serif"/>
<text top="100" left="72" width="440" height="16" font="0">A physical PDF line can end before a paragraph has finished and the next line</text>
<text top="118" left="82" width="430" height="16" font="0">may be shifted a few pixels by extraction without becoming a new paragraph.</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "slight-indent.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Indent", "reader.css", "reader.js", "Indent.pdf", {})
        self.assertIn("next line may be shifted a few pixels", converted)
        self.assertNotIn("next line</p>\n<p>may be shifted", converted)

    def test_hybrid_converter_preserves_a_recurring_first_line_indent(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="3" width="600" height="800">
<fontspec id="0" size="12" family="Serif"/>
<text top="100" left="90" width="410" height="16" font="0">The first paragraph begins with a repeated first-line indent and continues</text>
<text top="118" left="72" width="440" height="16" font="0">on the normal body margin before reaching its conclusion.</text>
<text top="136" left="90" width="410" height="16" font="0">The second paragraph uses that same first-line indent and must stay distinct.</text>
<text top="154" left="72" width="440" height="16" font="0">Its continuation remains part of the second paragraph.</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "recurring-indent.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Indent", "reader.css", "reader.js", "Indent.pdf", {})
        self.assertIn("conclusion.</p>\n<p>The second paragraph", converted)

    def test_hybrid_converter_joins_wrapped_title_and_removes_footer_number(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="2" width="894" height="1263">
<fontspec id="0" size="51" family="Sans"/><fontspec id="1" size="16" family="Sans"/><fontspec id="2" size="12" family="Sans"/><fontspec id="3" size="19" family="Sans"/><fontspec id="4" size="15" family="Serif"/>
<text top="79" left="77" width="320" height="60" font="0"><b>EXECUTABLE</b></text>
<text top="147" left="77" width="522" height="60" font="0"><b>NATURAL LANGUAGE</b></text>
<text top="288" left="96" width="719" height="20" font="1">A RESEARCH PROGRAMME FOR AUDITABLE KNOWLEDGE REPRESENTATION AND EXECUTABLE</text>
<text top="308" left="77" width="67" height="20" font="1">SCIENCE</text>
<text top="400" left="77" width="580" height="23" font="3"><b>3.6 Security, memory poisoning, and evaluation</b></text>
<text top="424" left="77" width="110" height="23" font="3"><b>uncertainty</b></text>
<text top="500" left="96" width="700" height="18" font="4">A normal body paragraph begins here and establishes the body font size.</text>
<text top="520" left="77" width="700" height="18" font="4">Its wrapped physical line continues here without becoming a heading.</text>
<text top="550" left="96" width="700" height="18" font="4">A second body paragraph provides a stable body-font sample.</text>
<text top="1216" left="437" width="37" height="15" font="2">— 2 —</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "title.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Title", "reader.css", "reader.js", "Title.pdf", {})
        self.assertIn('<h2 id="page_2">EXECUTABLE NATURAL LANGUAGE</h2>', converted)
        self.assertIn("<h2>A RESEARCH PROGRAMME FOR AUDITABLE KNOWLEDGE REPRESENTATION AND EXECUTABLE SCIENCE</h2>", converted)
        self.assertIn("<h2>3.6 Security, memory poisoning, and evaluation uncertainty</h2>", converted)
        self.assertNotIn("— 2 —", converted)

    def test_mixed_font_page_does_not_turn_large_body_prose_into_headings(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="11" width="894" height="1263">
<fontspec id="0" size="14" family="Serif"/><fontspec id="1" size="20" family="Serif"/>
<text top="100" left="99" width="700" height="18" font="0">Introductory material establishes a smaller local font.</text>
<text top="120" left="99" width="700" height="18" font="0">It continues for several lines on this mixed-layout page.</text>
<text top="140" left="99" width="700" height="18" font="0">This section ends before the larger narrative typography.</text>
<text top="500" left="82" width="700" height="24" font="1">The city measured distance in temperature.</text>
<text top="528" left="101" width="700" height="24" font="1">Sunward streets were counted by how quickly water became steam.</text>
<text top="556" left="82" width="700" height="24" font="1">Nightward districts were counted by ice on the door hinges.</text>
<text top="584" left="82" width="700" height="24" font="1">Between them lay a place where rain could fall.</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "mixed-font.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Mixed", "reader.css", "reader.js", "Mixed.pdf", {})
        self.assertNotIn("<h2", converted)
        self.assertIn("<p>The city measured distance in temperature.</p>", converted)

    def test_hybrid_converter_joins_three_line_title_and_keeps_small_display_text(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="8" width="648" height="972">
<fontspec id="0" size="17" family="Serif"/><fontspec id="1" size="33" family="Sans"/><fontspec id="2" size="12" family="Sans"/>
<text top="105" left="101" width="352" height="40" font="1"><b>Encrypted Bricks,</b></text>
<text top="149" left="78" width="259" height="40" font="1"><b>BrickMaps, and</b></text>
<text top="193" left="78" width="255" height="40" font="1"><b>Reconstruction</b></text>
<text top="267" left="78" width="500" height="23" font="0">Normal body text establishes the reading size for this page.</text>
<text top="292" left="78" width="500" height="23" font="0">A second body line supplies another representative font sample.</text>
<text top="317" left="78" width="500" height="23" font="0">A third body line confirms that this is the dominant prose style.</text>
<text top="342" left="78" width="500" height="23" font="0">A final body line completes the paragraph with ordinary prose.</text>
<text top="390" left="110" width="420" height="15" font="2"><b>NO BOUNDARY IS SACRED MERELY BECAUSE IT IS HIDDEN,</b></text>
<text top="406" left="135" width="380" height="15" font="2"><b>AND NO OPENING IS LOVING MERELY BECAUSE IT IS</b></text>
<text top="422" left="290" width="70" height="15" font="2"><b>SHARED.</b></text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "long-title.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Title", "reader.css", "reader.js", "Title.pdf", {})
        self.assertIn("<h2 id=\"page_8\">Encrypted Bricks, BrickMaps, and Reconstruction</h2>", converted)
        self.assertIn("<p><strong>NO BOUNDARY IS SACRED MERELY BECAUSE IT IS HIDDEN, AND NO OPENING IS LOVING MERELY BECAUSE IT IS SHARED.</strong></p>", converted)
        self.assertEqual(converted.count("<h2"), 1)

    def test_hybrid_converter_joins_isolated_display_title_as_level_one_heading(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="13" width="648" height="972">
<fontspec id="0" size="27" family="Sans"/>
<text top="195" left="146" width="410" height="33" font="0"><b>Chapter 1. Ten Minutes Before the </b></text>
<text top="229" left="297" width="80" height="33" font="0"><b>Gods </b></text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "isolated-display-title.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Chapter", "reader.css", "reader.js", "Chapter.pdf", {})
        self.assertIn('<h1 id="page_13">Chapter 1. Ten Minutes Before the Gods</h1>', converted)
        self.assertNotIn("</strong></p>\n<p><strong>Gods", converted)

    def test_hybrid_converter_does_not_merge_a_contents_run_into_one_heading(self):
        entries = [
            "CHAPTER 1 — THE FIRST QUESTION",
            "CHAPTER 2 — THE SECOND QUESTION",
            "CHAPTER 3 — THE THIRD QUESTION",
            "CHAPTER 4 — THE FOURTH QUESTION",
            "CHAPTER 5 — THE FIFTH QUESTION",
        ]
        text_nodes = "".join(
            f'<text top="{100 + index * 37}" left="80" width="430" height="20" font="0"><b>{entry}</b></text>'
            for index, entry in enumerate(entries)
        )
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="2" width="600" height="800">
<fontspec id="0" size="17" family="Sans"/><fontspec id="1" size="14" family="Serif"/>
{text_nodes}
<text top="300" left="80" width="430" height="18" font="1">Ordinary prose establishes the page body size.</text>
<text top="322" left="80" width="430" height="18" font="1">Another ordinary sentence confirms that body style.</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "contents.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Contents", "reader.css", "reader.js", "Contents.pdf", {})
        self.assertNotIn(" ".join(entries), converted)
        self.assertNotIn(f"{entries[0]} {entries[1]}", converted)
        self.assertEqual(sum(converted.count(entry) for entry in entries), len(entries))

    def test_hybrid_converter_keeps_overlapping_margin_label_with_prose_after_heading(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="15" width="648" height="972">
<fontspec id="0" size="20" family="Sans"/><fontspec id="1" size="19" family="Serif"/><fontspec id="2" size="11" family="Sans"/>
<text top="69" left="121" width="427" height="25" font="0"><b>1.1 What the Observer Who Does Not Kneel </b></text>
<text top="94" left="94" width="54" height="25" font="0"><b>Sees </b></text>
<text top="144" left="94" width="115" height="14" font="2"><b>COMPOSITE SCENE </b></text>
<text top="136" left="212" width="362" height="24" font="1">In the same planetary hour, a bell calls a few dozen </text>
<text top="169" left="107" width="466" height="24" font="1">people into an almost empty church in Europe; millions align their bodies toward a sacred place, </text>
<text top="203" left="107" width="466" height="24" font="1">repeat a shared ritual, regulate attention, and bind emotion to a story larger than the person. </text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "overlapping-margin-label.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Label", "reader.css", "reader.js", "Label.pdf", {})
        self.assertIn(
            '<h2 id="page_15">1.1 What the Observer Who Does Not Kneel Sees</h2>',
            converted,
        )
        self.assertIn(
            "<p>COMPOSITE SCENE In the same planetary hour, a bell calls a few dozen people into an almost empty church",
            converted,
        )
        self.assertNotIn("Sees In the same planetary hour", converted)

    def test_hybrid_converter_does_not_absorb_unfinished_prose_after_bold_heading(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="29" width="594" height="891">
<fontspec id="0" size="18" family="Sans"/><fontspec id="1" size="17" family="Serif"/>
<text top="618" left="71" width="384" height="24" font="0"><b>Eden, Dilmun, and the Refusal of Mortality </b></text>
<text top="649" left="71" width="454" height="23" font="1">The biblical garden is planted, watered by a river, and organized around a </text>
<text top="674" left="71" width="455" height="23" font="1">prohibition that continues onto another physical line without sentence-ending </text>
<text top="700" left="71" width="455" height="23" font="1">punctuation because the paragraph itself continues onto the following page </text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "heading-before-unfinished-prose.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Heading", "reader.css", "reader.js", "Heading.pdf", {})
        self.assertIn(
            '<h2 id="page_29">Eden, Dilmun, and the Refusal of Mortality</h2>',
            converted,
        )
        self.assertIn("<p>The biblical garden is planted, watered by a river", converted)
        self.assertNotIn("Mortality The biblical garden", converted)

    def test_hybrid_converter_does_not_absorb_smaller_nonbold_prose_after_heading(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="94" width="612" height="792">
<fontspec id="0" size="17" family="Serif"/><fontspec id="1" size="15" family="Serif"/><fontspec id="2" size="12" family="Serif"/>
<text top="88" left="72" width="150" height="20" font="0">Model Equations </text>
<text top="116" left="72" width="468" height="18" font="1">Innovation raises the growth rate when effort is allocated to discovery and </text>
<text top="138" left="72" width="468" height="18" font="1">coordination remains effective across the institutions described by the model </text>
<text top="160" left="72" width="468" height="18" font="1">on the next page without ending this physical line as a complete sentence </text>
<text top="240" left="72" width="120" height="15" font="2">Parameter</text>
<text top="280" left="72" width="120" height="15" font="2">Baseline</text>
<text top="320" left="72" width="120" height="15" font="2">Lower bound</text>
<text top="360" left="72" width="120" height="15" font="2">Upper bound</text>
<text top="400" left="72" width="120" height="15" font="2">Sensitivity</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "nonbold-heading-before-prose.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Equations", "reader.css", "reader.js", "Equations.pdf", {})
        self.assertIn('<h2 id="page_94">Model Equations</h2>', converted)
        self.assertIn("<p>Innovation raises the growth rate", converted)
        self.assertNotIn("Model Equations Innovation raises", converted)

    def test_hybrid_converter_keeps_large_sentence_like_display_copy_as_prose(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="153" width="612" height="792">
<fontspec id="0" size="17" family="Sans"/><fontspec id="1" size="16" family="Sans"/><fontspec id="2" size="11" family="Sans"/>
<text top="78" left="72" width="180" height="21" font="0"><b>SmoothTrace</b></text>
<text top="106" left="72" width="468" height="20" font="1">A symbolic and contestable layer that compiles source and output into graphs </text>
<text top="128" left="72" width="468" height="20" font="1">and localizes relevant differences. Its reference specification appears in Appendix </text>
<text top="150" left="72" width="20" height="20" font="1">D. </text>
<text top="230" left="72" width="110" height="14" font="2">Field</text>
<text top="270" left="72" width="110" height="14" font="2">Purpose</text>
<text top="310" left="72" width="110" height="14" font="2">Input</text>
<text top="350" left="72" width="110" height="14" font="2">Output</text>
<text top="390" left="72" width="110" height="14" font="2">Constraint</text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "large-display-copy.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Display copy", "reader.css", "reader.js", "Display.pdf", {})
        self.assertIn('<h2 id="page_153">SmoothTrace</h2>', converted)
        self.assertIn(
            "<p>A symbolic and contestable layer that compiles source and output into graphs "
            "and localizes relevant differences. Its reference specification appears in Appendix D.</p>",
            converted,
        )
        self.assertNotIn("<h2>A symbolic and contestable layer", converted)

    def test_hybrid_converter_preserves_unbolded_outline_heading_at_page_boundary(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml>
<page number="94" width="612" height="792">
<fontspec id="0" size="13" family="Serif"/>
<text top="720" left="80" width="360" height="16" font="0">Balance = expertise − capture − staleness − churn </text>
</page>
<page number="95" width="612" height="792">
<fontspec id="0" size="17" family="Serif"/><fontspec id="1" size="15" family="Serif"/>
<text top="70" left="72" width="112" height="21" font="0">E.4 Results </text>
<text top="108" left="72" width="468" height="18" font="1">The comparison reports the complete model runs for each architecture.</text>
<text top="130" left="72" width="468" height="18" font="1">A second sentence establishes the ordinary prose size on this page.</text>
<text top="152" left="72" width="468" height="18" font="1">A third sentence keeps the body font statistically dominant here.</text>
<text top="174" left="72" width="468" height="18" font="1">A final sentence completes the surrounding prose sample.</text>
</page>
</pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "outline-heading-page-boundary.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Outline", "reader.css", "reader.js", "Outline.pdf", {})
        self.assertIn('<h2 id="page_95">E.4 Results</h2>', converted)
        self.assertNotIn("churn E.4 Results", converted)

    def test_hybrid_converter_does_not_hide_outline_heading_inside_same_style_prose(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<pdf2xml><page number="79" width="612" height="792">
<fontspec id="0" size="15" family="Serif"/>
<text top="160" left="96" width="468" height="18" font="0">The model samples a broad parameter space without claiming that every </text>
<text top="179" left="72" width="468" height="18" font="0">point is equally probable in the real world. </text>
<text top="217" left="72" width="100" height="18" font="0">Equations B.3 </text>
<text top="244" left="96" width="468" height="18" font="0">Unit intensity after the efficiency improvement is represented as follows. </text>
<text top="266" left="72" width="468" height="18" font="0">The next sentence continues in the same typeface and at the same size. </text>
</page></pdf2xml>"""
        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            xml_path = Path(temp_dir) / "outline-heading-in-prose-run.xml"
            xml_path.write_text(xml, encoding="utf-8")
            pages = parse_pdf_xml(xml_path)
        converted = hybrid_html(pages, "Outline run", "reader.css", "reader.js", "Outline.pdf", {})
        self.assertIn("<h2>Equations B.3</h2>", converted)
        self.assertNotIn("real world. Equations B.3", converted)


if __name__ == "__main__":
    unittest.main()
