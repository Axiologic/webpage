# Website requirements

## Analytics

Every public HTML page under `docs/` must include the Umami analytics script exactly once inside its `<head>` section. This applies to all top-level pages, legacy pages and every book edition page under `docs/books/`.

```html
<script defer src="https://cloud.umami.is/script.js" data-website-id="e252999d-4479-42d7-9526-5f778846d4f6"></script>
```

When creating a new HTML page, add the script before the closing `</head>` tag. When modifying or generating pages in bulk, verify that every public HTML page still contains this script in `<head>` exactly once.

## English PDF editions and text translations for the inline reader

English is the sole canonical PDF source. Supported PDF-derived HTML editions are exact basename pairs across `docs/content/EN/*.pdf` and `docs/content/htmls/EN/*.html`; no PDF may live in `docs/content/RO/`, `PL/`, `IT/`, `ES/`, `PT/`, `DE/`, or `FR/`. Romanian (RO), Polish (PL), Italian (IT), Spanish (ES), Portuguese (PT), German (DE), and French (FR) are text translations of the English editions, not separate PDF editions. Translate both the full reflow HTML and the 10-minute HTML from the current English text, preserve reader assets, and write `docs/content/htmls/<LANG>/` plus `docs/content/10minutes/<LANG>/`. Translations never include a PDF-conversion warning or a language-specific PDF download. Do not run the PDF repair tooling over translations or other website pages. Full-size PNG covers live in `docs/content/covers/`, listing thumbnails in `docs/content/thumbnails/`, and `docs/content/index.json` inventories every content file. The index is also the single source of truth for each summary page's available languages and PDF/HTML/EPUB/audio URLs; never hardcode edition lists, download links, reader links, or `Available in` text in `docs/books/*/index.html`.

### Content tools

All utilities dedicated to book content live in `docs/content/tools/`; do not add duplicate content-maintenance scripts under the repository-level `scripts/` directory. Run them from the repository root:

- `book_html.py` detects stale English PDF/HTML pairs, repairs generated English reflow HTML and audits supported English editions.
- `convert_book_pdf.py` converts one English PDF, or the full English collection, into reflowable HTML and extracted assets. It requires Poppler's `pdftohtml` command.
- `generate-book-thumbnails.mjs` reads full-size images from `docs/content/covers/` and regenerates WebP files in `docs/content/thumbnails/`. It requires ImageMagick's `magick` command.
- `content_index.py` builds or checks the public content manifest. `docs/content/tools/` is intentionally excluded from that manifest.

Whenever a cover is added or changed, remove only external page margins (never cover artwork), regenerate all thumbnails and then rebuild the index:

```bash
node docs/content/tools/generate-book-thumbnails.mjs
python3 docs/content/tools/content_index.py build
```

Use the following workflow whenever an English book PDF is added or changed:

1. Detect editions requiring conversion:

   ```bash
   python3 docs/content/tools/book_html.py stale
   ```

2. Convert each reported PDF to its matching reflowable HTML file:

   ```bash
   python3 docs/content/tools/convert_book_pdf.py docs/content/EN/Book.pdf
   ```

   The converter uses Poppler `pdftohtml -xml` as a layout-aware source. It reflows text from coordinates, reconstructs repeated aligned columns as semantic HTML tables, extracts PDF raster images into a matching `Book.assets/` directory, retains page anchors, removes repeated page furniture, adds the required English conversion warning and PDF link, adds the reader assets and Umami analytics, then runs the repair/integrity pass. Unique full-page raster/scanned pages are preserved as page facsimiles. Byte-identical images found on at least three different pages are omitted only when their geometry also identifies them as full-page backgrounds or small page-edge ornaments; repeated figures in the document body remain intact. Use `--force` only when an explicit reconversion of an otherwise up-to-date pair is required.

   To reconvert the entire English collection in parallel after a converter change:

   ```bash
   python3 docs/content/tools/convert_book_pdf.py --all --force --jobs 4
   ```

3. Repair newly introduced unmarked generated HTML and report any still-stale pairs:

   ```bash
   python3 docs/content/tools/book_html.py fix
   ```

   Regenerate the content inventory after adding, removing, or renaming any content file:

   ```bash
   python3 docs/content/tools/content_index.py build
   ```

4. Run the tests and final audit:

   ```bash
   python3 -m unittest discover -s tests -v
   python3 docs/content/tools/book_html.py audit
   python3 docs/content/tools/content_index.py check
   ```

The repair pass joins PDF line-wrap fragments even across empty layout paragraphs and page anchors, joins sentences interrupted by page furniture, removes plain or ornamented page-number paragraphs and empty layout paragraphs, restores missing dialogue line breaks, verifies that no visible book-text token was lost, and adds `<meta content="4" name="pdf-reflow-repair"/>`. The converter uses indentation together with vertical spacing to distinguish wrapped physical lines from real prose/dialogue paragraphs; it must not create a paragraph break merely because a continuation line is slightly indented. It also splits em-dash and multilingual quoted dialogue from narration; combines two-or-more adjacent same-style title lines into one heading; keeps smaller all-caps display quotations out of the heading hierarchy; removes table-of-contents dot leaders and their page numbers; and divides extraction-created walls of prose only at complete sentence boundaries. Files with the current repair marker must not be scanned or rewritten again; later routine runs only compare their HTML/PDF modification times. A marked HTML file older than its PDF requires conversion, not another repair. Repairing an unmarked file preserves its original modification time so it cannot hide an already-stale conversion.

Use `python3 docs/content/tools/book_html.py fix --force` only for an explicit full cleanup when already-marked editions must be reprocessed after a repair-rule change. Force mode retains one conversion warning and analytics script, rather than duplicating either one.

Every English PDF-derived edition begins with an English warning explaining that figures or formatting may be missing or simplified and linking to the matching PDF. Keep this warning, the repair marker, the standalone reader CSS/JavaScript and the analytics script exactly once. Translated text editions have no PDF warning and keep the standalone reader CSS/JavaScript and analytics script exactly once.
