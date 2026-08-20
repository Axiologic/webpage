# Website requirements

## Analytics

Every public HTML page under `docs/` must include the Umami analytics script exactly once inside its `<head>` section. This applies to all top-level pages, legacy pages and every book edition page under `docs/books/`.

```html
<script defer src="https://cloud.umami.is/script.js" data-website-id="e252999d-4479-42d7-9526-5f778846d4f6"></script>
```

When creating a new HTML page, add the script before the closing `</head>` tag. When modifying or generating pages in bulk, verify that every public HTML page still contains this script in `<head>` exactly once.
