(() => {
  const editionData = document.querySelector('[data-book-language-editions]');
  if (!editionData) return;

  let editions;
  try {
    editions = JSON.parse(editionData.textContent);
  } catch {
    return;
  }
  if (!Array.isArray(editions) || editions.length < 2) return;

  let menu;
  let activeButton;
  const closeMenu = () => {
    menu?.remove();
    menu = undefined;
    activeButton?.setAttribute('aria-expanded', 'false');
    activeButton = undefined;
  };
  const openMenu = (button, mode) => {
    closeMenu();
    menu = document.createElement('div');
    menu.className = 'language-choice-menu';
    menu.setAttribute('role', 'menu');
    menu.innerHTML = `<p>${mode === 'download' ? 'Download in' : 'Read in'}</p>`;
    editions.forEach(({ language, href }) => {
      const link = document.createElement('a');
      link.href = href;
      link.textContent = language;
      link.setAttribute('role', 'menuitem');
      if (mode === 'download') {
        link.download = '';
        link.title = `Download ${language} edition`;
      } else {
        link.target = '_blank';
        link.rel = 'noreferrer';
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

  document.querySelectorAll('.edition-actions, .book-actions').forEach((actions) => {
    actions.querySelectorAll('a[href*="downloads/books/"]').forEach((button) => {
      const mode = button.hasAttribute('download') ? 'download' : 'read';
      button.setAttribute('aria-haspopup', 'menu');
      button.setAttribute('aria-expanded', 'false');
      button.addEventListener('click', (event) => {
        event.preventDefault();
        openMenu(button, mode);
      });
    });
  });
  document.addEventListener('click', (event) => {
    if (menu && !menu.contains(event.target) && !activeButton?.contains(event.target)) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });
})();
