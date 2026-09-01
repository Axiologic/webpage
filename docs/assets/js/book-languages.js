(() => {
  const actions = document.querySelector('.edition-actions');
  const availability = document.querySelector('[data-book-availability]');
  const cover = document.querySelector('.edition-cover');
  if (!actions || !availability || !cover) return;

  const indexUrl = new URL('../../content/index.json?v=20260901-2', window.location.href);
  const title = document.querySelector('.edition-hero h1, h1')?.textContent?.trim() || 'Axiologic Reader';
  const segments = window.location.pathname.split('/').filter(Boolean);
  const bookId = decodeURIComponent(new URL(cover.currentSrc || cover.src).pathname.split('/').pop()).replace(/\.[^.]+$/, '');
  const slug = segments.at(-1) === 'index.html' ? segments.at(-2) : segments.at(-1);

  const absoluteEdition = (edition) => ({
    ...edition,
    ...(edition.html ? { html: new URL(edition.html, indexUrl).href } : {}),
    ...(edition.pdf ? { pdf: new URL(edition.pdf, indexUrl).href } : {}),
    ...(edition.tenMinuteHtml ? { tenMinuteHtml: new URL(edition.tenMinuteHtml, indexUrl).href } : {}),
    ...(edition.epub ? { epub: new URL(edition.epub, indexUrl).href } : {}),
    ...(edition.audio ? { audio: new URL(edition.audio, indexUrl).href } : {}),
  });

  const absolutePdfEdition = (edition) => ({
    ...edition,
    pdf: new URL(edition.pdf, indexUrl).href,
  });

  const readerUrl = (edition, mode = 'full') => {
    const tenMinute = mode === 'ten-minute' && edition.tenMinuteHtml;
    const html = tenMinute ? edition.tenMinuteHtml : edition.html;
    const reader = new URL('../../reader/index.html', window.location.href);
    reader.searchParams.set('id', `${tenMinute ? 'ten-minute' : 'edition'}:${new URL(html).pathname}`);
    reader.searchParams.set('title', `${title} · ${tenMinute ? 'short read' : edition.label}`);
    if (edition.pdf) reader.searchParams.set('pdf', edition.pdf);
    reader.searchParams.set('html', html);
    if (tenMinute) reader.searchParams.set('mode', 'ten-minute');
    if (edition.epub) reader.searchParams.set('epub', edition.epub);
    if (edition.audio) reader.searchParams.set('audio', edition.audio);
    reader.searchParams.set('back', window.location.href);
    return reader.href;
  };

  let menu;
  let activeButton;
  const closeMenu = () => {
    menu?.remove();
    menu = undefined;
    activeButton?.setAttribute('aria-expanded', 'false');
    activeButton = undefined;
  };

  const openMenu = (button, mode, editions) => {
    closeMenu();
    menu = document.createElement('div');
    menu.className = 'language-choice-menu';
    menu.setAttribute('role', 'menu');
    menu.innerHTML = `<p>${mode === 'download' ? 'Choose PDF edition' : 'Read in'}</p>`;
    editions.forEach((edition) => {
      const link = document.createElement('a');
      link.href = mode === 'download' ? edition.pdf : readerUrl(edition, mode);
      link.textContent = edition.label;
      link.setAttribute('role', 'menuitem');
      if (mode === 'download') {
        link.download = '';
        link.title = `Download ${edition.label}`;
      } else {
        link.title = `Read ${edition.label} edition in the adaptable online reader`;
      }
      menu.append(link);
    });
    document.body.append(menu);
    const bounds = button.getBoundingClientRect();
    const left = Math.max(8, Math.min(bounds.left + window.scrollX, window.scrollX + window.innerWidth - menu.offsetWidth - 8));
    menu.style.left = `${left}px`;
    menu.style.top = `${bounds.bottom + window.scrollY + 8}px`;
    button.setAttribute('aria-expanded', 'true');
    activeButton = button;
  };

  const render = (book) => {
    const editions = book.editions.map(absoluteEdition);
    const fullEditions = editions.filter((edition) => edition.html);
    const defaultEdition = fullEditions.find((edition) => edition.language === 'EN') || fullEditions[0];
    const downloadableEditions = (book.pdfEditions?.length
      ? book.pdfEditions.map(absolutePdfEdition)
      : editions.filter((edition) => edition.pdf));
    const defaultDownload = downloadableEditions.find((edition) => edition.language === 'EN') || downloadableEditions[0];
    actions.innerHTML = '';

    const read = document.createElement('a');
    read.className = 'btn primary';
    read.href = readerUrl(defaultEdition);
    read.innerHTML = 'Read online <span>→</span>';
    read.title = `Read ${defaultEdition.label} edition in the adaptable online reader`;

    const download = defaultDownload && document.createElement('a');
    if (download) {
      download.className = 'btn ghost';
      download.href = defaultDownload.pdf;
      download.download = '';
      download.textContent = 'Download PDF';
      download.title = 'Download ' + defaultDownload.label + ' edition';
    }

    const tenMinuteEditions = editions.filter((edition) => edition.tenMinuteHtml);
    const tenMinuteEdition = tenMinuteEditions.find((edition) => edition.language === 'EN') || tenMinuteEditions[0];
    const tenMinute = tenMinuteEdition && document.createElement('a');
    if (tenMinute) {
      tenMinute.className = 'btn ghost';
      tenMinute.href = readerUrl(tenMinuteEdition, 'ten-minute');
      tenMinute.textContent = 'Read in 10 min';
      tenMinute.title = `Read the short ${tenMinuteEdition.label} edition in the adaptable online reader`;
    }

    if (fullEditions.length > 1) {
      read.setAttribute('aria-haspopup', 'menu');
      read.setAttribute('aria-expanded', 'false');
      read.addEventListener('click', (event) => {
        event.preventDefault();
        openMenu(read, 'read', fullEditions);
      });
    }

    if (tenMinuteEditions.length > 1 && tenMinute) {
      tenMinute.setAttribute('aria-haspopup', 'menu');
      tenMinute.setAttribute('aria-expanded', 'false');
      tenMinute.addEventListener('click', (event) => {
        event.preventDefault();
        openMenu(tenMinute, 'ten-minute', tenMinuteEditions);
      });
    }

    if (downloadableEditions.length > 1 && download) {
      download.setAttribute('aria-haspopup', 'menu');
      download.setAttribute('aria-expanded', 'false');
      download.addEventListener('click', (event) => {
        event.preventDefault();
        openMenu(download, 'download', downloadableEditions);
      });
    }

    if (tenMinute) actions.append(tenMinute);
    actions.append(read);
    if (download) actions.append(download);
    availability.textContent = `Available in: ${editions.map((edition) => edition.label).join(' · ')}`;
  };

  const loadFileManifest = () => new Promise((resolve, reject) => {
    if (globalThis.__AXIOLOGIC_CONTENT_INDEX__) {
      resolve(globalThis.__AXIOLOGIC_CONTENT_INDEX__);
      return;
    }
    const script = document.createElement('script');
    script.src = new URL('../../content/index.js?v=20260901-2', window.location.href).href;
    script.onload = () => globalThis.__AXIOLOGIC_CONTENT_INDEX__
      ? resolve(globalThis.__AXIOLOGIC_CONTENT_INDEX__)
      : reject(new Error('local content manifest did not define an index'));
    script.onerror = () => reject(new Error('local content manifest could not be loaded'));
    document.head.append(script);
  });

  const loadIndex = window.location.protocol === 'file:'
    ? loadFileManifest()
    : fetch(indexUrl)
    .then((response) => {
      if (!response.ok) throw new Error(`content index returned ${response.status}`);
      return response.json();
    });

  loadIndex
    .then((index) => {
      const book = index.books?.find((candidate) => candidate.id === bookId)
        || index.books?.find((candidate) => candidate.slug === slug);
      if (!book?.editions?.length) throw new Error(`no indexed editions for ${bookId}`);
      render(book);
    })
    .catch((error) => {
      actions.textContent = 'Book editions are temporarily unavailable.';
      availability.textContent = 'Availability could not be loaded.';
      console.error(error);
    });

  document.addEventListener('click', (event) => {
    if (menu && !menu.contains(event.target) && !activeButton?.contains(event.target)) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });
})();
