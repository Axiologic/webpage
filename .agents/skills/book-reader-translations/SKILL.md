---
name: book-reader-translations
description: Translate book-reader HTML directly in stable chunks and rebuild full and 10-minute editions, without creating translated PDFs or using an external translation service.
---

# Book reader translations

Use this skill when the website's inline book readers need to be translated or
their multilingual coverage needs repair. Translate the chunk JSON directly as
the agent; do not call an external translation service. The English reader
edition is the canonical source; never translate PDFs or create non-English
PDF editions.

Prepare a source reader as stable chunks from the repository root:

```bash
python3 docs/content/tools/html_translation_chunks.py prepare \
  docs/content/htmls/EN/EXPLAINABLE_AI.html --language RO \
  --destination docs/content/htmls/RO/EXPLAINABLE_AI_RO.html \
  --workdir docs/content/.translation-work/RO/EXPLAINABLE_AI/full
```

Each `chunks/*.json` file has ordered `source` strings. Translate each one to
its `translation` string, retaining names, identifiers, URLs, code, and
citations exactly where they belong. Then rebuild only when every segment is
filled:

```bash
python3 docs/content/tools/html_translation_chunks.py check \
  docs/content/.translation-work/RO/EXPLAINABLE_AI/full
python3 docs/content/tools/html_translation_chunks.py assemble \
  docs/content/.translation-work/RO/EXPLAINABLE_AI/full
python3 docs/content/tools/content_index.py build
```

To queue all still-missing files for a language group, use:

```bash
python3 docs/content/tools/html_translation_chunks.py prepare-missing \
  --language RO --language PL --maximum-words 700
```

Prepare and assemble both the complete reader in `docs/content/htmls/<LANG>/`
and the 10-minute reader in `docs/content/10minutes/<LANG>/`. The tool leaves
tags, assets, analytics, citations, and reader code untouched; it removes the
English PDF conversion notice and source download link before chunking.

Before publishing, run:

```bash
python3 docs/content/tools/translate_books.py check
python3 docs/content/tools/content_index.py check
```

For a partial repair, pass one or more `--book BOOK_ID` values. Existing files
are left untouched unless `--force` is explicitly requested.
