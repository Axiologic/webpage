import importlib.util
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "docs" / "content"


def load_script(name: str):
    path = CONTENT_ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


content_index = load_script("content_index")


class ContentLayoutTests(unittest.TestCase):
    def test_pdf_and_html_editions_are_exact_language_pairs(self):
        pdfs = {
            path.relative_to(CONTENT_ROOT).with_suffix("")
            for path in CONTENT_ROOT.glob("[A-Z][A-Z]/*.pdf")
        }
        htmls = {
            path.relative_to(CONTENT_ROOT / "htmls").with_suffix("")
            for path in (CONTENT_ROOT / "htmls").glob("[A-Z][A-Z]/*.html")
        }
        self.assertEqual(pdfs, htmls)

    def test_content_index_is_current(self):
        index_path = CONTENT_ROOT / "index.json"
        self.assertTrue(index_path.is_file())
        self.assertEqual(index_path.read_text(encoding="utf-8"), content_index.serialize())
        index_script_path = CONTENT_ROOT / "index.js"
        self.assertTrue(index_script_path.is_file())
        self.assertEqual(index_script_path.read_text(encoding="utf-8"), content_index.serialize_script())
        self.assertFalse(any(record["path"].startswith("tools/") for record in content_index.inventory()["files"]))

    def test_every_book_page_is_backed_by_manifest_editions(self):
        books = content_index.discover_books()
        pages = list((REPO_ROOT / "docs" / "books").glob("*/index.html"))
        self.assertEqual(len(books), len(pages))
        self.assertTrue(all(book["editions"] for book in books))

    def test_book_pages_do_not_hardcode_edition_availability(self):
        for page in (REPO_ROOT / "docs" / "books").glob("*/index.html"):
            source = page.read_text(encoding="utf-8")
            self.assertNotIn("data-book-language-editions", source, page)
            self.assertNotIn("Available in:", source, page)
            self.assertIsNone(re.search(r"content/[A-Z]{2}/[^\" ]+\.pdf", source), page)
            self.assertIn("data-book-actions", source, page)
            self.assertIn("data-book-availability", source, page)

    def test_english_editions_have_ten_minute_reading_guides(self):
        for book in content_index.discover_books():
            english = next((edition for edition in book["editions"] if edition["language"] == "EN"), None)
            if not english:
                continue
            self.assertIn("tenMinuteHtml", english, book["id"])
            guide = CONTENT_ROOT / english["tenMinuteHtml"]
            self.assertTrue(guide.is_file(), book["id"])
            self.assertIn('../../reader/standalone.js', guide.read_text(encoding="utf-8"), book["id"])


if __name__ == "__main__":
    unittest.main()
