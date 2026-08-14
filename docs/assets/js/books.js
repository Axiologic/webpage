const books = [
  {
    id: 'Outfinitism_Meta_Rationality', category: 'Outfinitist Philosophy & Experiments', title: 'Outfinitism', subtitle: 'Meta-Rationality and the Limits of Finite Human Reason', position: 1,
    staticUrl: './books/outfinitism-meta-rationality/index.html',
    description: 'An introduction to Outfinitism as a practice of reasoning that keeps human models, institutions and ambitions open to criticism, revision and further possibility.', color: 'linear-gradient(145deg, #49433b, #171613 74%)'
  },
  {
    id: 'Metacult', category: 'Outfinitist Philosophy & Experiments', title: 'Metacult', subtitle: 'Modernizing Humanity’s Oldest Social Technology: How to Build Collective Power Without Crushing the Individual', position: 2,
    staticUrl: './books/metacult/index.html',
    description: 'An inquiry into collective power, shared meaning and the institutional safeguards that let a culture coordinate without demanding the surrender of the individual.', color: 'linear-gradient(145deg, #3c3932, #121513 74%)'
  },
  {
    id: 'THE_LICENCE_AND_THE_SHARED_NAME', category: 'Technology', title: 'The Licence and the Shared Name', subtitle: 'How to Give an Idea Away Without Letting It Be Captured', position: 5,
    staticUrl: './books/the-licence-and-the-shared-name/index.html',
    description: 'A proposal for sharing an idea while preserving its conditions of openness, correction and resistance to capture by an owner, faction or institution.', color: 'linear-gradient(145deg, #4a3d2d, #171411 74%)'
  },
  {
    id: 'The_Captured_Internet', category: 'Technology', title: 'The Captured Internet', subtitle: 'Personal Data, Algorithmic Power, and the Coming Constitutional Crisis', position: 6,
    staticUrl: './books/the-captured-internet/index.html',
    description: 'An examination of personal data, algorithmic power and the constitutional questions that emerge when the public sphere is shaped by private infrastructures.', color: 'linear-gradient(145deg, #3f4c4c, #111617 74%)'
  },
  {
    id: 'The_Founder_Lottery', category: 'Outfinitist Philosophy & Experiments', title: 'The Founder Lottery', subtitle: 'Why We Mistake Historical Accidents for Merit', position: 16,
    staticUrl: './books/the-founder-lottery/index.html',
    description: 'A challenge to the stories through which historical luck becomes merit, authority and inherited legitimacy—and a search for more accountable alternatives.', color: 'linear-gradient(145deg, #51342c, #1a1110 74%)'
  },
  {
    id: 'Decentralised_Brands', category: 'Outfinitist Philosophy & Experiments', title: 'Decentralised Brands', subtitle: 'How Communities Can Own What They Build', position: 17,
    staticUrl: './books/decentralised-brands/index.html',
    description: 'A study of the conditions under which communities can share identity, value and governance without placing their common work beyond revision.', color: 'linear-gradient(145deg, #424743, #131615 74%)'
  },
  {
    id: 'Investing_in_an_AI_Dominated_Economy', category: 'Outfinitist Philosophy & Experiments', title: 'Investing in an AI-Dominated Economy', subtitle: 'The Outfinity Investment Thesis', position: 18,
    staticUrl: './books/investing-in-an-ai-dominated-economy/index.html',
    description: 'A practical inquiry into investment, value creation and strategic judgment in an economy reshaped by artificial intelligence.', color: 'linear-gradient(145deg, #4c4130, #17140f 74%)'
  },
  {
    id: 'AssistOS', category: 'Technology', title: 'AssistOS',
    staticUrl: './books/assistos/index.html',
    subtitle: '',
    description: 'AssistOS presents a product, market and research vision for an open operating layer where local models, agents, tools, files and people can work together. It examines how intelligence can become installable, governable, portable and useful across devices, organisations and models—without pretending that every long-term ambition is already complete.',
    color: 'linear-gradient(145deg, #17433c, #0c1619 72%)'
  },
  {
    id: 'Agentic_AI_2026', category: 'Technology', title: 'Agentic AI 2026',
    staticUrl: './books/agentic-ai-2026/index.html',
    subtitle: '',
    description: 'The first wave of language-model applications was organised around prompts; the next is organised around delegated action. This book studies the runtime that allocates authority among models, tools, memory, validators and human reviewers, and asks how bounded delegation can turn uncertain model competence into useful, controlled work.',
    color: 'linear-gradient(145deg, #28365c, #10151f 72%)'
  },
  {
    id: 'OpenDSU', category: 'Technology', title: 'OpenDSU', subtitle: 'Essential Philosophy',
    fileId: 'OpenDSU_Essential_Philosophy',
    description: 'OpenDSU is presented as a conceptual framework for controlled, reconstructable and verifiable digital objects. It examines the relationship among bounded data, cryptographic authority, protected storage, verifiable history, provenance, validation, discovery and governance—while keeping its concepts independent of any single implementation.',
    color: 'linear-gradient(145deg, #25454d, #0f171b 72%)'
  },
  {
    id: 'MRP_VM_Book', category: 'Technology', title: 'MRP-VM', subtitle: 'Automating the Construction of Trustworthy Custom Agentic Harnesses',
    description: 'MRP-VM is an architecture for automating the construction and controlled improvement of custom agentic harnesses. It gives powerful models a disciplined environment in which purpose, source authority, tool permissions, qualification, traceability, version identity and human control can be preserved.',
    color: 'linear-gradient(145deg, #3c3153, #15121c 72%)'
  },
  {
    id: 'OMNIS', category: 'Literature', title: 'OMNIS', subtitle: 'The Dark One · The Mirror Above · The Architecture of Longing', position: 3,
    description: 'A speculative trilogy about the price of being made. When a one-dimensional world discovers an Outside, OMNIS reopens the oldest questions: is there a Demiurge above the visible order, are we mistaking a cave for the whole of reality, and can a created mind discover a meaning for existence without becoming the prisoner of its creator’s purpose?',
    color: 'linear-gradient(145deg, #312a46, #101019 74%)'
  },
  {
    id: 'The_Basilisks_Internal_Critique_of_Outfinitism', category: 'Literature', title: "The Basilisk's Internal Critique of Outfinitism", position: 19,
    fileId: 'The_Basilisk_Internal_Critique_of_Outfinitism',
    subtitle: '',
    description: 'The Basilisk is not dead; it has merely lost the right to turn a conclusion into an event. As beings from the Outside conduct its autopsy, they discover the thought it could not contain: a world that continues without becoming a province of any central intelligence.',
    color: 'linear-gradient(145deg, #41263c, #111117 74%)'
  },
  {
    id: 'The_Cascade_of_the_New_VOL_I', category: 'Literature', title: 'The Cascade of the New — The Aster File', position: 1,
    subtitle: '',
    description: 'Dimensions are not merely directions in space: they measure how many kinds of freedom a reality can preserve at once. The Aster File enters the Cascade, a chain of worlds within worlds where creators may themselves be the creations of someone else.',
    color: 'linear-gradient(145deg, #243d5a, #12131d 74%)'
  },
  {
    id: 'Predator_in_the_Name_of_the_Dead', category: 'Literature', title: 'Predator in the Name of the Dead', position: 2,
    subtitle: '',
    description: 'A measurement error of 7.3 milligrams becomes a continent’s unfinished catastrophe. From a planet orbiting an orange star, an observer sends home a report that becomes a precise instrument for measuring guilt across time.',
    color: 'linear-gradient(145deg, #604033, #171313 74%)'
  },
  {
    id: 'Concordia_Universe', category: 'Literature', title: 'Concordia Series', position: 4,
    subtitle: '',
    description: 'A cycle of linked speculative novellas about intelligence, care, power and the fragile conditions of human freedom. Concordia does not arrive with an army: it arrives through medicine, protection and a world made safer before anyone can ask whether safety is still freedom.',
    color: 'linear-gradient(145deg, #443c70, #15131f 74%)'
  },
  {
    id: 'Oriven_Origaya_Universe', category: 'Literature', title: 'Oriven–Origaya Universe', position: 5,
    subtitle: '',
    description: 'The first killing in Orivenian history happened on another world. On Aethon, a people who measure consequences in centuries receive news carried across the stars—a signal that unsettles a civilisation built on deliberate, shared thought.',
    color: 'linear-gradient(145deg, #315052, #101918 74%)'
  },
  {
    id: 'The_Sovereignty_Archipelago', category: 'Literature', title: 'The Sovereignty Archipelago', position: 7,
    subtitle: '',
    description: 'A work of speculative literature about systems, authority and the choices hidden beneath their promises.',
    color: 'linear-gradient(145deg, #294b5a, #101619 74%)'
  },
  {
    id: 'The_Silicon_Shadows_and_I', category: 'Literature', title: 'The Silicon Shadows and I', position: 8,
    subtitle: '',
    description: 'A work of speculative literature about freedom, care and the right to refuse rescue.',
    color: 'linear-gradient(145deg, #40365a, #12121b 74%)'
  },
  {
    id: 'The_Museum_of_Good_Reasons', category: 'Literature', title: 'The Museum of Good Reasons', subtitle: 'A Catalogue of Things That Disappear by Themselves', position: 6,
    description: 'A work of speculative literature, available here to read.',
    color: 'linear-gradient(145deg, #54432d, #18140f 74%)'
  },
  {
    id: 'A_Balance_of_Iron_and_Salt', category: 'Literature', title: 'A Balance of Iron and Salt', subtitle: 'SF Novel', position: 9,
    description: 'A science-fiction novel, available here to read.', color: 'linear-gradient(145deg, #4c3c2e, #171617 74%)'
  },
  {
    id: 'Anatomy_Of_An_Echo', category: 'Literature', title: 'Anatomy Of An Echo', subtitle: '', position: 10,
    description: 'A work of literature, available here to read.', color: 'linear-gradient(145deg, #304252, #11161b 74%)'
  },
  {
    id: 'Me_and_My_Robots', category: 'Literature', title: 'Me and My Robots', subtitle: '', position: 11,
    description: 'A work of literature, available here to read.', color: 'linear-gradient(145deg, #543d56, #171219 74%)'
  },
  {
    id: 'Holding_the_Dirty_Thing_by_the_Clean_Side', category: 'Outfinitist Philosophy & Experiments', title: 'Holding the Dirty Thing by the Clean Side', subtitle: 'A History of Strategies for Social Success and a Search for Theoretical Legitimacy', position: 3,
    description: 'An inquiry into the ways societies persuade people to carry a cost while calling it duty, order, opportunity or virtue—and a search for social technologies that make burden, voice, exit and accountability more inspectable.', color: 'linear-gradient(145deg, #4e332a, #181312 74%)'
  },
  {
    id: 'ANTI_IDIOCRACY', category: 'Outfinitist Philosophy & Experiments', title: 'Anti-Idiocracy', subtitle: 'The Outfinitist Metacult Investigation', position: 4,
    description: 'A study of the dangerous configuration in which weak models, confidence disproportionate to evidence, refusal of correction and power combine. It develops the Outfinitist metacult as a culture of correction rather than superiority.', color: 'linear-gradient(145deg, #3e304e, #15131a 74%)'
  },
  {
    id: 'The_History_and_Future_of_Social_Technologies', category: 'Executable Science', title: 'The History and Future of Social Technologies', subtitle: 'The Yin-Yang of Civilisation',
    description: 'An interpretive synthesis of the symbols, roles, rules, procedures and incentives by which societies coordinate across time and distance—and a disciplined exploration of their possible futures.', color: 'linear-gradient(145deg, #243e42, #101817 74%)'
  },
  {
    id: 'Memes_for_2030', category: 'Outfinitist Philosophy & Experiments', title: 'Memes for 2030', subtitle: 'Ten Ideas Whose Time Is Coming',
    description: 'A study of the ideas that become culturally contagious when historical pressure, emotional need, technological possibility and narrative simplicity converge. The book maps ten memes for a changing moral architecture.', color: 'linear-gradient(145deg, #5b4424, #19150e 74%)'
  },
  {
    id: 'Too_Convinced_to_Stop', category: 'Outfinitist Philosophy & Experiments', title: 'Too Convinced to Stop', subtitle: '',
    description: 'A light, experimental analysis of how celebrated entrepreneurs persist through risk and uncertainty—sometimes with the force of an elephant in a china shop. It may offer occasional insight into the conviction that helps people build, and the collateral damage that conviction can create.', color: 'linear-gradient(145deg, #4d394d, #17131a 74%)'
  },
  {
    id: 'The_Zodiac_on_Trial', category: 'Outfinitist Philosophy & Experiments', title: 'The Zodiac on Trial', subtitle: '',
    description: 'An experiment with AI that assembles arguments for treating the zodiac as more than superstition. It is written for readers drawn to destiny and astrology, but also for sceptics willing to practise a more open-minded encounter with beliefs they do not share.', color: 'linear-gradient(145deg, #403852, #12131b 74%)'
  },
  {
    id: 'The_Thousand_Handed_Devil', category: 'Outfinitist Philosophy & Experiments', title: 'The Thousand-Handed Devil', subtitle: '', position: 5,
    description: 'A search for a new metaphor for modern evil. The book asks whether the moral responsibilities of AI must expand the idea of absolute evil beyond violence and lying, toward the immense and often unmeasurable complexity of the systems that shape human lives. It is compatible with Outfinitist philosophy without relying on its terminology.', color: 'linear-gradient(145deg, #53352e, #191211 74%)'
  },
  {
    id: 'The_Right_to_Help', category: 'Outfinitist Philosophy & Experiments', title: 'The Right to Help', subtitle: '', position: 15,
    staticUrl: './books/the-right-to-help/index.html',
    description: 'A human confession voiced through an AI, and a courtroom for the good that may sometimes be done by force. This reflective book examines care, responsibility and the troubling possibilities that can hide behind the language of doing good.', color: 'linear-gradient(145deg, #294b4b, #101817 74%)'
  },
  {
    id: 'Revocable_Nobility', category: 'Outfinitist Philosophy & Experiments', title: 'Revocable Nobility', subtitle: '', position: 6,
    description: 'A creative philosophical experiment using AI-generated theoretical models and simulations to explore nobility and possible forms of neo-feudalism. Rather than a settled scientific claim, it is part of a wider effort to test how AI might contribute to executable science—and to ask whether, if new hierarchies are coming, we can still choose their form.', color: 'linear-gradient(145deg, #55432d, #18140f 74%)'
  },
  {
    id: 'Cones_of_Meaning', category: 'Executable Science', title: 'Cones of Meaning', subtitle: '', position: 3,
    description: 'A book between technology and contemporary science, proposing that the way LLMs are built may contain more than simple statistics can explain. Through the geometry of cosine-distance cones, it develops intuitions about AI alignment and about why Outfinitism can acquire global coherence across many perspectives, sciences and lived experiences.', color: 'linear-gradient(145deg, #2e4d58, #10171a 74%)'
  },
  {
    id: 'An_Autopsy_of_a_Digital_Mind', category: 'Executable Science', title: 'An Autopsy of a Digital Mind', subtitle: '',
    description: 'Four experiments from the Achilles research project on what AI may reveal about forgiveness, human nature, meaning and justice. The results are surprising and meme-like in their density: ideas worth exploring, whose scientific and social verification is itself a demanding research challenge.', color: 'linear-gradient(145deg, #44354b, #151219 74%)'
  },
  {
    id: 'THE_CIVILIZED_MIND', category: 'Outfinitist Philosophy & Experiments', title: 'The Civilized Mind', subtitle: 'Truth, Power, and the Survival of Plural Democracies in the Age of Extremes', position: 8,
    description: 'An invitation to cultivate a way of thinking that seeks truth without cruelty, exercises power without arrogance and meets the future with enough ambition to build—and enough humility to learn.', color: 'linear-gradient(145deg, #28354e, #11131b 74%)'
  },
  {
    id: 'Aspirin_Viagra_and_Coffins', category: 'Outfinitist Philosophy & Experiments', title: 'Aspirin, Viagra, and Coffins', subtitle: 'The Impolite Manual of Inevitable Opportunities',
    description: 'An explicit experiment in research and writing with artificial intelligence, examining modern suffering as human tragedy, research object and market signal—without confusing entrepreneurial opportunity with moral permission.', color: 'linear-gradient(145deg, #582f39, #1a1215 74%)'
  },
  {
    id: 'The_Ultimate_Sense_of_Life', category: 'Outfinitist Philosophy & Experiments', title: 'The Ultimate Sense of Life', subtitle: 'A Serious Comedy of Gods, Ants, Consciousness, Saints, Sinners, and the Universe Trying to Understand Itself',
    staticUrl: './books/the-ultimate-sense-of-life/index.html',
    description: 'A human–AI inquiry that takes the oldest question seriously enough to let it become strange again. Through comedy, philosophy and a proposed map of meaning, it asks what remains when the universe refuses to issue a final verdict.', color: 'linear-gradient(145deg, #534226, #17140d 74%)'
  },
  {
    id: 'The_Tao_of_OMIS', category: 'Literature', title: 'The Tao of OMIS', subtitle: 'The Open Knot · The Gods Who Took Notes · The Soul Between',
    staticUrl: './books/the-tao-of-omis/index.html',
    description: 'Three speculative spirals through love, identity and return. In the OMNIS ontology, intimacy is not the conquest of another soul but the small interval left open inside every knot—the right to revise, refuse and remain surprising.', color: 'linear-gradient(145deg, #3e3157, #12111b 74%)'
  },
  {
    id: 'The_Great_Decoupling', category: 'Outfinitist Philosophy & Experiments', title: 'The Great Decoupling', subtitle: 'Humans, Work, and Culture After the Externalization of Cognition',
    staticUrl: './books/the-great-decoupling/index.html',
    description: 'What happens when thinking ceases to be the scarce human contribution around which work and status were built? This inquiry follows the fault line through work, culture and dignity, where liberation and dispossession can begin to look alarmingly alike.', color: 'linear-gradient(145deg, #254452, #10171a 74%)'
  },
  {
    id: 'The_Fragmented_Future', category: 'Outfinitist Philosophy & Experiments', title: 'The Fragmented Future', subtitle: 'AI, City-Regions, and New Forms of Human Civilization',
    staticUrl: './books/the-fragmented-future/index.html',
    description: 'AI may make small polities more viable just as it gives large systems unprecedented reach. This book enters the resulting field of futures: computational empires, city-regions, new elites and the quiet institutional choices that decide which world arrives.', color: 'linear-gradient(145deg, #314461, #11141e 74%)'
  },
  {
    id: 'Autopsy_of_Future_Emotions', category: 'Outfinitist Philosophy & Experiments', title: 'Autopsy of Future Emotions', subtitle: '',
    staticUrl: './books/autopsy-of-future-emotions/index.html',
    description: 'Before automation changes what we do, it may change what it feels like to be someone among others. A cautious atlas of status, attachment, work and simulated feeling, written for a world in which emotions become part of the infrastructure.', color: 'linear-gradient(145deg, #53354a, #17121a 74%)'
  },
  {
    id: 'The_Schizoid_and_the_Oracle_RO', category: 'Outfinitist Philosophy & Experiments', title: 'The Schizoid and the Oracle', subtitle: 'Outfinitism, Initiation, and the Design of a Capture-Resistant Ideological Seed',
    staticUrl: './books/the-schizoid-and-the-oracle/index.html',
    description: 'A philosophical investigation of ideas that promise liberation and end up captured. Between withdrawal, initiation and the oracle machine, it searches for a cultural seed that keeps its limits even when predators read it.', color: 'linear-gradient(145deg, #49364e, #17121a 74%)'
  },
  {
    id: 'THE_NECESSARY_MASK', category: 'Outfinitist Philosophy & Experiments', title: 'The Necessary Mask', subtitle: 'The Justification of Hypocrisy in a Finite World', position: 7,
    fileId: 'The_Necessary_Mask',
    description: 'A constructive argument about hypocrisy, moral psychology, unequal power and institutional life. It asks which adaptive function a hypocrisy performs, and how its deception or transferred harm can be reduced.', color: 'linear-gradient(145deg, #3d4d39, #131713 74%)'
  },
  {
    id: 'Executable_Natural_Language', category: 'Executable Science', title: 'Executable Natural Language', subtitle: '', position: 2,
    description: 'A survey and proposal for auditable chains from source language to grounded symbols, executable formal objects and verified results. It studies how language models and symbolic systems can work together without turning generated explanation into uncheckable authority.', color: 'linear-gradient(145deg, #5a4030, #171519 74%)'
  },
  {
    id: 'The_Frontier_Is_Correction', category: 'Executable Science', title: 'The Frontier Is Correction', subtitle: 'Novelty, Executable Science, and the Human-AI Research System', position: 1,
    staticUrl: './books/the-frontier-is-correction/index.html',
    description: 'Candidate science is becoming abundant before justification becomes scalable. This book argues that the real frontier is correction: the quality-adjusted rate at which claims acquire support, are narrowed by better explanations, or are rejected before they consume scarce attention.', color: 'linear-gradient(145deg, #263d52, #10161d 74%)'
  }
];

const collectionName = 'Axiologic Research Editions';
const assetBase = './downloads/assets/';
const pdfBase = './downloads/books/';
const escapeHtml = (value) => value.replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]);

function cover(book, className = '') {
  return `<div class="book-cover ${className}" style="--cover:${book.color}"><div class="book-cover-copy"><span>${collectionName}</span><strong>${escapeHtml(book.title)}</strong><span>${book.category}</span></div><img alt="${escapeHtml(book.title)} cover" data-cover="${book.fileId || book.id}"></div>`;
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

function renderListing() {
  ['Outfinitist Philosophy & Experiments', 'Science Fiction Literature', 'Technology & Executable Science'].forEach(category => {
    const grid = document.getElementById(`${category.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-grid`);
    if (!grid) return;
    grid.innerHTML = books.filter(book => {
      if (category === 'Science Fiction Literature') return book.category === 'Literature';
      if (category === 'Technology & Executable Science') return book.category === 'Technology' || book.category === 'Executable Science';
      return book.category === category;
    }).sort((a, b) => (a.position || Number.MAX_SAFE_INTEGER) - (b.position || Number.MAX_SAFE_INTEGER)).map(book => `
      <article class="book-card">
        <a href="${book.staticUrl || `./books/${book.id.toLowerCase().replaceAll('_', '-')}/index.html`}" aria-label="View ${escapeHtml(book.title)}">${cover(book)}</a>
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
  detail.innerHTML = `<a class="book-cover-link" href="${pdfBase}${book.fileId || book.id}.pdf" target="_blank" rel="noreferrer" aria-label="Read ${escapeHtml(book.title)} in a new tab">${cover(book, 'detail-cover')}</a><div class="book-detail-copy"><span class="eyebrow">${book.category} · ${collectionName}</span><h1>${escapeHtml(book.title)}</h1>${book.subtitle ? `<p class="book-subtitle">${escapeHtml(book.subtitle)}</p>` : ''}<p>${escapeHtml(book.description)}</p><div class="book-actions"><a class="btn primary" href="${pdfBase}${book.fileId || book.id}.pdf" target="_blank" rel="noreferrer">Read online <span>→</span></a><a class="btn ghost" href="${pdfBase}${book.fileId || book.id}.pdf" download>Download PDF</a></div></div>`;
  detail.querySelectorAll('[data-cover]').forEach(locateCover);
}

renderListing();
renderDetail();
