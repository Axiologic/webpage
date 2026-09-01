from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "content" / "tools"))

from translate_books import strip_english_pdf_material  # noqa: E402


class TranslateBooksTests(unittest.TestCase):
    def test_removes_the_english_conversion_warning_but_keeps_cited_pdfs(self):
        source = """<html><head></head><body>
        <aside data-pdf-conversion-warning=\"true\">Generated from a PDF.
        <a href=\"../../EN/Book.pdf\">Original PDF</a></aside>
        <p><a href=\"../../EN/Book.pdf\">Download the original PDF</a></p>
        <p>Reference: <a href=\"https://example.test/paper.pdf\">paper</a>.</p>
        </body></html>"""

        translated_source = strip_english_pdf_material(source)

        self.assertNotIn("data-pdf-conversion-warning", translated_source)
        self.assertNotIn("../../EN/Book.pdf", translated_source)
        self.assertIn("https://example.test/paper.pdf", translated_source)


if __name__ == "__main__":
    unittest.main()
