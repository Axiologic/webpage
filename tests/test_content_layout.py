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
ten_minute = load_script("ten_minute")


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

    def test_book_listing_has_balanced_categories_in_editorial_order(self):
        listing = (REPO_ROOT / "docs" / "books.html").read_text(encoding="utf-8")
        labels = [
            "Business &amp; Startups",
            "Executable Science &amp; Research",
            "AI Systems &amp; Infrastructure",
            "Cosmic &amp; Metaphysical SF",
            "Political &amp; Social SF",
            "Human &amp; Philosophical SF",
            "Outfinitist Foundations",
            "Power, Institutions &amp; Society",
            "Experiments and Speculations",
        ]
        positions = [listing.index(label) for label in labels]
        self.assertEqual(positions, sorted(positions))

        catalog = (REPO_ROOT / "docs" / "assets" / "js" / "books.js").read_text(encoding="utf-8")
        expected_counts = {
            "Business & Startups": 10,
            "Executable Science & Research": 9,
            "AI Systems & Infrastructure": 8,
            "Outfinitist Foundations": 9,
            "Power, Institutions & Society": 9,
            "Experiments and Speculations": 10,
        }
        for category, expected in expected_counts.items():
            self.assertEqual(catalog.count(f"category: '{category}'"), expected, category)
        self.assertNotIn("category: 'Experiments'", catalog)
        self.assertRegex(
            catalog,
            r"id: 'Cant_See_the_Forest_for_the_Trees'.*?category: 'Business & Startups'.*?position: 0",
        )
        self.assertRegex(
            catalog,
            r"id: 'The_Animal_That_Prays'.*?category: 'Power, Institutions & Society'.*?position: 1",
        )
        self.assertRegex(
            catalog,
            r"id: 'The_Geometry_of_Becoming'.*?category: 'Cosmic & Metaphysical SF'.*?position: 0",
        )
        self.assertRegex(
            catalog,
            r"id: 'HUNGER_AFTER_ALL_THE_WORLDS'.*?category: 'Human & Philosophical SF'.*?position: 'last'",
        )
        self.assertRegex(catalog, r"id: 'Coherence_Pressure'.*?position: 8")
        self.assertRegex(catalog, r"id: 'SstarLM'.*?position: 9")
        self.assertRegex(catalog, r"(?s)id: 'OpenDSU'.*?position: 11")

    def test_book_pages_do_not_hardcode_edition_availability(self):
        for page in (REPO_ROOT / "docs" / "books").glob("*/index.html"):
            source = page.read_text(encoding="utf-8")
            self.assertNotIn("data-book-language-editions", source, page)
            self.assertNotIn("Available in:", source, page)
            self.assertIsNone(re.search(r"content/[A-Z]{2}/[^\" ]+\.pdf", source), page)
            self.assertIn("data-book-actions", source, page)
            self.assertIn("data-book-availability", source, page)

    def test_english_editions_have_editorial_short_reads(self):
        for book in content_index.discover_books():
            english = next((edition for edition in book["editions"] if edition["language"] == "EN"), None)
            if not english:
                continue
            self.assertIn("tenMinuteHtml", english, book["id"])
            guide = CONTENT_ROOT / english["tenMinuteHtml"]
            self.assertTrue(guide.is_file(), book["id"])
            source = guide.read_text(encoding="utf-8")
            self.assertIn('../../reader/standalone.js', source, book["id"])
            self.assertNotIn('This guided edition selects substantial passages', source, book["id"])
            self.assertNotIn('Editorial synthesis in progress', source, book["id"])

            book_id = Path(english["pdf"]).stem
            summary = ten_minute.load_summary(book_id)
            self.assertEqual([], ten_minute.validate_summary(summary, book_id), book["id"])
            full_edition = (CONTENT_ROOT / english["html"]).read_text(encoding="utf-8")
            opening_chapter = ten_minute.opening_ten_minute_heading(full_edition)
            if opening_chapter:
                self.assertIn("source_excerpt", summary, book["id"])
                self.assertIn('Original opening chapter', source, book["id"])
                self.assertIn('Author’s original text', source, book["id"])
                self.assertNotIn('10-minute synthesis', source, book["id"])
            else:
                self.assertNotIn("source_excerpt", summary, book["id"])
                self.assertIn('10-minute synthesis', source, book["id"])
                self.assertIn('Why read the complete book', source, book["id"])


if __name__ == "__main__":
    unittest.main()
