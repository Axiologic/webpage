(() => {
  const actions = document.querySelector('.edition-actions');
  const availability = document.querySelector('[data-book-availability]');
  const cover = document.querySelector('.edition-cover');
  if (!actions || !availability || !cover) return;

  const indexUrl = new URL('../../content/index.json', window.location.href);
  const title = document.querySelector('.edition-hero h1, h1')?.textContent?.trim() || 'Axiologic Reader';
  const segments = window.location.pathname.split('/').filter(Boolean);
  const bookId = decodeURIComponent(new URL(cover.currentSrc || cover.src).pathname.split('/').pop()).replace(/\.[^.]+$/, '');
  const slug = segments.at(-1) === 'index.html' ? segments.at(-2) : segments.at(-1);

  const absoluteEdition = (edition) => ({
    ...edition,
    pdf: new URL(edition.pdf, indexUrl).href,
    html: new URL(edition.html, indexUrl).href,
    ...(edition.epub ? { epub: new URL(edition.epub, indexUrl).href } : {}),
    ...(edition.audio ? { audio: new URL(edition.audio, indexUrl).href } : {}),
  });

  const readerUrl = (edition) => {
    const reader = new URL('../../reader/index.html', window.location.href);
    reader.searchParams.set('id', `edition:${new URL(edition.pdf).pathname}`);
    reader.searchParams.set('title', `${title} · ${edition.label}`);
    reader.searchParams.set('pdf', edition.pdf);
    reader.searchParams.set('html', edition.html);
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
    menu.innerHTML = `<p>${mode === 'download' ? 'Download in' : 'Read in'}</p>`;
    editions.forEach((edition) => {
      const link = document.createElement('a');
      link.href = mode === 'download' ? edition.pdf : readerUrl(edition);
      link.textContent = edition.label;
      link.setAttribute('role', 'menuitem');
      if (mode === 'download') {
        link.download = '';
        link.title = `Download ${edition.label} edition`;
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
    const defaultEdition = editions.find((edition) => edition.language === 'EN') || editions[0];
    actions.innerHTML = '';

    const read = document.createElement('a');
    read.className = 'btn primary';
    read.href = readerUrl(defaultEdition);
    read.innerHTML = 'Read online <span>→</span>';
    read.title = `Read ${defaultEdition.label} edition in the adaptable online reader`;

    const download = document.createElement('a');
    download.className = 'btn ghost';
    download.href = defaultEdition.pdf;
    download.download = '';
    download.textContent = 'Download PDF';
    download.title = `Download ${defaultEdition.label} edition`;

    if (editions.length > 1) {
      [read, download].forEach((button) => {
        button.setAttribute('aria-haspopup', 'menu');
        button.setAttribute('aria-expanded', 'false');
      });
      read.addEventListener('click', (event) => {
        event.preventDefault();
        openMenu(read, 'read', editions);
      });
      download.addEventListener('click', (event) => {
        event.preventDefault();
        openMenu(download, 'download', editions);
      });
    }

    actions.append(read, download);
    availability.textContent = `Available in: ${editions.map((edition) => edition.label).join(' · ')}`;
  };

  fetch(indexUrl)
    .then((response) => {
      if (!response.ok) throw new Error(`content index returned ${response.status}`);
      return response.json();
    })
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
