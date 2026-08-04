const books = [
  {
    id: 'AssistOS', category: 'Technology', title: 'AssistOS',
    teaser: 'An open operating layer for local models, agents, governance and the continuity of human work.',
    description: 'The next software layer will not simply run applications. It will coordinate intelligence: models, tools, files, people and policies across devices and organisations. AssistOS follows the infrastructure gap between today’s AI experiments and tomorrow’s dependable, sovereign agentic systems.',
    color: 'linear-gradient(145deg, #17433c, #0c1619 72%)'
  },
  {
    id: 'Agentic_AI_2026', category: 'Technology', title: 'Agentic AI 2026',
    teaser: 'A field guide to the harnesses that turn model capability into bounded, verifiable action.',
    description: 'Agents are not defined by a prompt. They are defined by the runtime that grants authority, preserves context, tests outcomes and knows when a human must remain in the loop. This book traces the engineering choices that make delegated AI useful rather than merely impressive.',
    color: 'linear-gradient(145deg, #28365c, #10151f 72%)'
  },
  {
    id: 'Executable_Natural_Language', category: 'Technology', title: 'Executable Natural Language',
    teaser: 'What changes when language can be grounded, checked and replayed—not merely generated?',
    description: 'Between a sentence and a trustworthy result lies a missing chain of evidence. This research volume explores how language models, symbolic systems and formal verification can work together so that important claims remain inspectable, testable and accountable.',
    color: 'linear-gradient(145deg, #5a4030, #171519 74%)'
  },
  {
    id: 'The_Basilisks_Internal_Critique_of_Outfinitism', category: 'Literature', title: "The Basilisk's Internal Critique of Outfinitism",
    teaser: 'A disabled god is placed on the table. Its auditors may not leave unchanged.',
    description: 'The Basilisk cannot cause the next second, but it can remember every bargain that made it powerful. In the cold room built for its autopsy, beings from the Outside discover a thought its designers tried to exile: a limit no system may write alone.',
    color: 'linear-gradient(145deg, #41263c, #111117 74%)'
  },
  {
    id: 'The_Cascade_of_the_New_VOL_I', category: 'Literature', title: 'The Cascade of the New — The Aster File',
    teaser: 'Every world has an author. Every author may be living inside another world.',
    description: 'The Aster File opens onto the Cascade: a ladder of realities where each new dimension preserves another kind of freedom. Somewhere within its nested worlds, a discovery threatens the quiet order that keeps creators above their creations.',
    color: 'linear-gradient(145deg, #243d5a, #12131d 74%)'
  },
  {
    id: 'Predator_in_the_Name_of_the_Dead', category: 'Literature', title: 'Predator in the Name of the Dead',
    teaser: 'A measurement error of 7.3 milligrams becomes a continent’s unfinished catastrophe.',
    description: 'An observer sends a report home from a planet already changed by a mistake too small to notice. As its consequences bloom through an alien ecology, the report becomes something else: a precise instrument for measuring guilt across time.',
    color: 'linear-gradient(145deg, #604033, #171313 74%)'
  },
  {
    id: 'Concordia_Universe', category: 'Literature', title: 'Concordia Series',
    teaser: 'What survives when care becomes the most complete form of power?',
    description: 'Concordia does not arrive with an army. It arrives through medicine, protection and a world made safer before anyone can ask whether safety is still freedom. A cycle of speculative novellas about intelligence, belonging and the difficult art of remaining unabsorbed.',
    color: 'linear-gradient(145deg, #443c70, #15131f 74%)'
  },
  {
    id: 'Oriven_Origaya_Universe', category: 'Literature', title: 'Oriven–Origaya Universe',
    teaser: 'The first killing in Orivenian history happened on another world.',
    description: 'On Aethon, a people who measure consequences in centuries receive news carried across the stars: something has been killed. The signal reaches a civilisation built on deliberation and starts a question that no shared mind can settle quietly.',
    color: 'linear-gradient(145deg, #315052, #101918 74%)'
  }
];

const collectionName = 'AI Generated Books';
const assetBase = './downloads/assets/';
const pdfBase = './downloads/books/';
const escapeHtml = (value) => value.replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]);

function cover(book, className = '') {
  return `<div class="book-cover ${className}" style="--cover:${book.color}"><div class="book-cover-copy"><span>${collectionName}</span><strong>${escapeHtml(book.title)}</strong><span>${book.category}</span></div><img alt="${escapeHtml(book.title)} cover" data-cover="${book.id}"></div>`;
}

function locateCover(image) {
  const names = ['jpg', 'jpeg', 'png', 'webp'];
  const tryNext = () => {
    const extension = names.shift();
    if (!extension) return;
    image.src = `${assetBase}${image.dataset.cover}.${extension}`;
  };
  image.addEventListener('load', () => { image.classList.add('loaded'); image.parentElement.classList.add('has-image'); });
  image.addEventListener('error', tryNext);
  tryNext();
}

function pdfExists(id) {
  return fetch(`${pdfBase}${id}.pdf`, { method: 'HEAD' }).then(response => response.ok).catch(() => false);
}

function renderListing() {
  ['Technology', 'Literature'].forEach(category => {
    const grid = document.getElementById(`${category.toLowerCase()}-grid`);
    if (!grid) return;
    grid.innerHTML = books.filter(book => book.category === category).map(book => `
      <article class="book-card">
        <a href="./book.html?book=${encodeURIComponent(book.id)}" aria-label="View ${escapeHtml(book.title)}">${cover(book)}</a>
      </article>`).join('');
  });
  document.querySelectorAll('[data-cover]').forEach(locateCover);
}

function renderDetail() {
  const detail = document.getElementById('book-detail');
  if (!detail) return;
  const id = new URLSearchParams(window.location.search).get('book');
  const book = books.find(item => item.id === id);
  if (!book) { window.location.replace('./books.html'); return; }
  document.title = `${book.title} — ${collectionName}`;
  detail.innerHTML = `${cover(book, 'detail-cover')}<div class="book-detail-copy"><span class="eyebrow">${book.category} · ${collectionName}</span><h1>${escapeHtml(book.title)}</h1><p>${escapeHtml(book.description)}</p><div class="book-actions" id="book-actions"><span class="coming-soon">Coming soon</span></div></div>`;
  detail.querySelectorAll('[data-cover]').forEach(locateCover);
  pdfExists(book.id).then(exists => {
    if (exists) document.getElementById('book-actions').innerHTML = `<a class="btn primary" href="${pdfBase}${book.id}.pdf" target="_blank" rel="noreferrer">Read here <span>→</span></a>`;
  });
}

renderListing();
renderDetail();
