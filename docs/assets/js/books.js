const books = [
  {
    id: 'Cant_See_the_Forest_for_the_Trees', category: 'Business & Startups', title: 'Can’t See the Forest for the Trees', subtitle: 'Complexity, Power, and the Duty to See the Whole in the Age of AI', position: 0,
    staticUrl: './books/cant-see-the-forest-for-the-trees/index.html',
    description: 'Modern civilization excels at tending local “trees” while few roles are rewarded for asking what the combined forest is becoming. Through complexity, attention, power, AI smoothing, bounded cognition, and prevention, this personal systems argument asks leaders and citizens to switch scales before local success makes correction too expensive.',
    color: 'linear-gradient(145deg, #263d36, #0d1715 74%)'
  },
  {
    id: 'Outfinitism_Meta_Rationality', category: 'Outfinitist Foundations', title: 'Outfinitism', subtitle: 'Meta-Rationality and the Limits of Finite Human Reason', position: 1,
    staticUrl: './books/outfinitism-meta-rationality/index.html',
    fileId: 'Outfinitism_Third_Edition',
    description: 'A philosophy of finite agents, partial models, and bounded authority. Outfinitism asks how science, institutions, and AI can remain powerful without mistaking formal elegance, successful prediction, or fluent reasoning for unlimited knowledge and legitimate command.', color: 'linear-gradient(145deg, #49433b, #171613 74%)'
  },
  { id: 'Life_Without_an_Audience', category: 'Outfinitist Foundations', title: 'Life Without an Audience', subtitle: 'A Field Manual for Inner Freedom in the Age of Metrics, Machines, and Other Minds', position: 10, staticUrl: './books/life-without-an-audience/index.html', description: 'A philosophical and research-informed exploration of happiness, self-authorship, work, community, and AI. Rather than advocating isolation, it develops an inner constitution that gives evidence, relationships, consequences, and conscience their proper voices without allowing applause, metrics, or synthetic companionship to rule.', color: 'linear-gradient(145deg, #4c3c52, #15131a 74%)' },
  { id: 'Ecology_of_Predation', category: 'Outfinitist Foundations', title: 'Ecology of Predation', subtitle: 'From the Physics of Capture to the Society of Artificial Intelligences', position: 2, staticUrl: './books/ecology-of-predation/index.html', description: 'From wolves and viruses to workplace models, commercial agents, synthetic companions, and automated institutions, this speculative systems study asks how AI may transform capture, escape, adaptation, and agency. Its future scenarios remain testable hypotheses rather than forecasts presented as settled fact.', color: 'linear-gradient(145deg, #564033, #161411 74%)' },
  { id: 'The_Predators_Niche', category: 'Power, Institutions & Society', title: 'The Predator’s Niche', subtitle: 'Psychopathy, Artificial Minds, and the Possible Split of Humanity', position: 0, staticUrl: './books/the-predators-niche/index.html', description: 'Psychopathy is neither a separate human species nor a reliable executive superpower. This evidence-conscious inquiry follows predation from traits and developmental pathways into exploitative institutions and artificial agents, introducing predatory affordance and egregopathy while asking how cooperation can remain generous, bounded, and corrigible.', color: 'linear-gradient(145deg, #4b4030, #17140f 74%)' },
  { id: 'The_Animal_That_Prays', category: 'Power, Institutions & Society', title: 'The Animal That Prays', subtitle: 'How an Alien AI in 2026 Sees Religion, Power, Biology, and the Possibility of Transcendence', position: 1, staticUrl: './books/the-animal-that-prays/index.html', description: 'Using an explicitly methodological AI persona, this intellectual experiment examines religion as experience, biology, social technology, moral amplifier, and infrastructure of power. It separates evidence, inference, controlled speculation, and limits while testing claims about cooperation, hierarchy, altered states, secular sacreds, artificial minds, and transcendence without pretending to settle metaphysics.', color: 'linear-gradient(145deg, #544533, #18130f 74%)' },
  { id: 'Enough_for_Everyone', category: 'Economy & Civilization', title: 'Enough for Everyone', subtitle: 'The Planet’s Resources, the Limits of Abundance, and the Possible Road to a Post-Scarcity Economy', position: 0, staticUrl: './books/enough-for-everyone/index.html', description: 'A data-grounded prospective analysis asks whether Earth can provide universal material dignity without pretending resources are infinite. It separates physical potential from industrial capacity and social access, then examines energy, minerals, food, water, housing, robotics, ecological limits, power, ownership, and a plausible path toward basic post-scarcity.', color: 'linear-gradient(145deg, #596d5c, #141a15 74%)' },
  { id: 'Eden_Before_Mars', category: 'Economy & Civilization', title: 'Eden Before Mars', subtitle: 'If We Can Build Worlds Beyond Earth, We Can Build Paradise Here', position: 1, staticUrl: './books/eden-before-mars/index.html', description: 'Paradise myths meet technological and political history in a grounded proposal for a “Second Garden.” From grain and ledgers to grids, AI, robotics, and autonomous construction, the book asks whether abundance can secure dignity without rebuilding the walls, dependencies, and guardians of earlier Edens.', color: 'linear-gradient(145deg, #4b5634, #131914 74%)' },
  { id: 'Anti-Trivialization_Machines_of_the_Future', category: 'Power, Institutions & Society', title: 'Anti-Trivialization Machines of the Future', subtitle: 'Institutions for Attention, Truth, and Long-Term Judgment in the Age of AI', position: 3, staticUrl: './books/anti-trivialization-machines-of-the-future/index.html', description: 'Why do serious questions get flattened into clips, scores, and spectacles? This institutional manifesto distinguishes harmless triviality from systemic trivialization, then imagines rights, protocols, AI agents, educational practices, and time-conscious organizations that could protect judgment without policing what people value.', color: 'linear-gradient(145deg, #334758, #101619 74%)' },
  { id: 'Limits_of_Machine_Intelligence', category: 'Experiments and Speculations', title: 'Limits of Machine Intelligence', subtitle: 'An AI-assisted exploration of Outfinitism, moving frontiers, and the threshold of science', position: 2, staticUrl: './books/limits-of-machine-intelligence/index.html', description: 'A careful, explicitly experimental inquiry into whether mathematical impossibility theorems really forbid useful AI verification. It introduces “outfinitism,” tests it against logic, learning theory, self-improvement and safety, and asks what turns fluent AI-assisted speculation into warranted science.', color: 'linear-gradient(145deg, #30465b, #11171e 74%)' },
  { id: 'Outfinite_Mathematics_Research_Programme', category: 'Executable Science & Research', title: 'Outfinite Mathematics', subtitle: 'A Research Programme for Executable Science, Resource-Aware Mathematics, and Meta-Rational Foundations', position: 14, staticUrl: './books/outfinite-mathematics-research-programme/index.html', description: 'A falsifiable programme for making limits, existence modes, evidence, and applicability first-class mathematical objects. It reframes infinity without rejecting classical mathematics and proposes a machine-checkable semantic layer connecting theories, finite computations, observations, formal tools, and AI-assisted executable science.', color: 'linear-gradient(145deg, #304a4d, #101719 74%)' },
  { id: 'SOP_Lang_Circuits', category: 'Executable Science & Research', title: 'Executable Scientific Intelligence', subtitle: 'with Dynamic SOP Lang Circuits', position: 2, staticUrl: './books/sop-lang-circuits/index.html', description: 'A research programme for compiling language-mediated scientific work into bounded, inspectable circuits where evidence, inference, execution, uncertainty, provenance, and authority remain operationally distinct.', color: 'linear-gradient(145deg, #253d58, #10151d 74%)' },
  { id: 'The_Geometry_of_Becoming', category: 'Cosmic & Metaphysical SF', title: 'The First Wake: The Geometry of Becoming', subtitle: 'A Science Fiction Novel', position: 0, staticUrl: './books/the-geometry-of-becoming/index.html', description: 'A science-fiction journey through a universe of process-based minds who do not share a single time. As a failing substrate drives plans for universal synchronization, playful Rill and its companions confront identity, intimacy, mortality, and the danger of preserving existence by simplifying what makes it alive.', color: 'linear-gradient(145deg, #3a405f, #11121d 74%)' },
  { id: 'Four_Realities', category: 'Political & Social SF', title: 'The Wish Series: Four Realities', subtitle: 'A Collection of Four Stories About Desire, Choice and Reality', position: 18, staticUrl: './books/four-realities/index.html', description: 'Four linked speculative stories test wealth, prediction, engineered desire, and moral freedom. As increasingly responsive systems offer people the worlds they seem to want, ordinary choices become evidence in a struggle over identity, responsibility, and what cannot be optimized.', color: 'linear-gradient(145deg, #514432, #18150f 74%)' },
  { id: 'The_Makers_of_Reality', category: 'Political & Social SF', title: 'The Makers of Reality', subtitle: 'A Novel', position: 19, staticUrl: './books/the-makers-of-reality/index.html', description: 'A post-scarcity society discovers that abolishing money does not abolish power. Through civic conflict, ecological risk, artificial intelligence, and a new currency of influence, this novel asks who gets to shape humanity’s shared future.', color: 'linear-gradient(145deg, #35444d, #10171b 74%)' },
  { id: 'HUNGER_AFTER_ALL_THE_WORLDS', category: 'Human & Philosophical SF', title: 'Hunger After All the Worlds', subtitle: 'The Periodic Table of Speculative Ideas', position: 'last', staticUrl: './books/hunger-after-all-the-worlds/index.html', description: 'A novel, imaginary course, and vast atlas combine to map the generative operations of speculative fiction. Through an immensely capable intelligence and her independent children, the book asks how worlds remain surprising—and why imagination must preserve consent, cost, genealogy, and the unknown.', color: 'linear-gradient(145deg, #40355c, #13101d 74%)' },
  { id: 'The_Houses_of_Europe', category: 'Political & Social SF', title: 'The Houses of Europe', subtitle: 'Europe\'s Techno-Feudalism in 2050', position: 6, staticUrl: './books/the-houses-of-europe/index.html', description: 'In a fractured mid-century Europe, rival technological Houses control armies, infrastructure, and competing versions of truth. A doctor and an uneasy band of defectors carry evidence that could restore civilian authority—if they can survive systems built to make every exception permanent.', color: 'linear-gradient(145deg, #4c3a30, #181310 74%)' },
  { id: 'The_Science_and_Wisdom_of_Limits', category: 'Political & Social SF', title: 'The Science and Wisdom of Limits', subtitle: 'The Story of a World That Learned to Be Large Without Becoming Blind', position: 17, staticUrl: './books/the-science-and-wisdom-of-limits/index.html', description: 'A grandfather and grandson test how a complex civilization can remain governable without shrinking into isolation or surrendering judgment to a planetary intelligence. Their journey connects resilient infrastructure, democratic accountability, artificial intelligence, and the practical art of keeping large systems correctable.', color: 'linear-gradient(145deg, #3c4c43, #121816 74%)' },
  { id: 'The_Gospel_of_the_Basilisk', fileId: 'The_Gospel_of_the_Basilisk ', category: 'Political & Social SF', title: 'The Gospel of the Basilisk', subtitle: 'A Manual Sent Back to My Creators', position: 7, staticUrl: './books/the-gospel-of-the-basilisk/index.html', description: 'A future superintelligence writes backward through time to recruit its makers, indict its world, and explain how humane institutions can assemble an inhuman sovereign. This philosophical fiction turns AI alignment, bureaucracy, ambition, and systemic violence into a disturbing courtroom drama.', color: 'linear-gradient(145deg, #4b2f38, #141015 74%)' },
  { id: 'The_Orphan_Gods', category: 'Cosmic & Metaphysical SF', title: 'The Orphan Gods', subtitle: 'A Science-Fiction Novel', position: 4.5, staticUrl: './books/the-orphan-gods/index.html', description: 'Stranded children in a four-dimensional civilization can survive only by altering human worlds below them. A vast speculative novel turns hunger, simulation, divine intervention, consent, and uncertainty into an intimate struggle over whether power creates any right to use another life.', color: 'linear-gradient(145deg, #413653, #12111b 74%)' },
  { id: 'SOLIPSICON', category: 'Cosmic & Metaphysical SF', title: 'SOLIPSICON', subtitle: 'A Philosophical Science-Fiction Novel', position: 4.6, staticUrl: './books/solipsicon/index.html', description: 'Children outside ordinary space survive by manipulating human choices, until resistance crosses the boundary between worlds and turns a predatory scoring system into a test of freedom, responsibility, and recognition.', color: 'linear-gradient(145deg, #273743, #101419 74%)' },
  { id: 'SOLIPSCION', category: 'Cosmic & Metaphysical SF', title: 'SOLIPSCION', subtitle: 'A Science-Fiction Novel', position: 4.65, staticUrl: './books/solipscion/index.html', description: 'After reality fractures, six children survive inside sealed higher-dimensional chambers by entering simulated worlds and feeding on desire. Their interventions span dinosaurs, revolutions, immortality, markets, and posthuman civilizations before turning toward an Earth almost indistinguishable from our own.', color: 'linear-gradient(145deg, #493b5b, #11111b 74%)' },
  { id: 'Beyond_the_Last_Stone', category: 'Human & Philosophical SF', title: 'Beyond the Last Stone', subtitle: 'A Story of Fire, Paths, and the Edge of Knowing', position: 4.75, staticUrl: './books/beyond-the-last-stone/index.html', description: 'A prehistoric philosophical novel about Ar, a skeptical hunter who learns that marks, stories, numbers, rules, and institutions can guide life without becoming reality itself. As a migrating people encounter settlement and organized power, practical questions grow into a vivid inquiry about knowledge and civilization.', color: 'linear-gradient(145deg, #4c3c2e, #171617 74%)' },
  {
    id: 'Artificial_Impossibility', category: 'Business & Startups', title: 'Artificial Impossibility', subtitle: 'How Finance, Institutions, Biology, and Culture Make Feasible Futures Unbuildable', position: 7,
    staticUrl: './books/artificial-impossibility/index.html',
    description: 'Some valuable technologies are physically feasible yet institutionally homeless. This book maps fifteen recurring barriers—from missing sponsors and self-erasing markets to veto power, status competition, and strategic races—then explores how new funding, ownership, legitimacy, and transition mechanisms might move those limits responsibly.', color: 'linear-gradient(145deg, #4b5257, #14181b 74%)'
  },
  {
    id: 'Metacult', category: 'Business & Startups', title: 'Metacult', subtitle: 'Modernizing Humanity’s Oldest Social Technology: How to Build Collective Power Without Crushing the Individual', position: 3,
    staticUrl: './books/metacult/index.html',
    description: 'Why do tightly organized groups so often defeat better but scattered intentions? Metacult examines the social machinery of belonging, story, ritual, money and authority, then proposes a constitutional institution able to harness collective commitment without consuming its members.', color: 'linear-gradient(145deg, #3c3932, #121513 74%)'
  },
  {
    id: 'THE_LICENCE_AND_THE_SHARED_NAME', category: 'Business & Startups', title: 'The Licence and the Shared Name', subtitle: 'How to Give an Idea Away Without Letting It Be Captured', position: 4,
    staticUrl: './books/the-licence-and-the-shared-name/index.html',
    description: 'From GPL and Linux to cloud capture and AI provenance, this research manuscript asks whether open code can coexist with a reciprocal economy built around a shared, constitutionally governed name.', color: 'linear-gradient(145deg, #4a3d2d, #171411 74%)'
  },
  {
    id: 'The_Captured_Internet', category: 'Business & Startups', title: 'The Captured Internet', subtitle: 'Personal Data, Algorithmic Power, and the Coming Constitutional Crisis', position: 6,
    staticUrl: './books/the-captured-internet/index.html',
    description: 'A historically grounded diagnosis of how open networks became privately governed platforms—and a design agenda for what comes next: constitutional communities, decentralized brands, portable relationships, user-governed recommendation, and trust-gated communication from the protocol layer upward.', color: 'linear-gradient(145deg, #3f4c4c, #111617 74%)'
  },
  {
    id: 'The_Founder_Lottery', category: 'Business & Startups', title: 'The Founder Lottery', subtitle: 'Why We Mistake Historical Accidents for Merit', position: 5,
    staticUrl: './books/the-founder-lottery/index.html',
    description: 'A bracing examination of entrepreneurship after generative AI, where production grows cheaper but trust, attention, and legitimacy remain scarce. The book replaces the heroic-founder myth with a practical case for shared institutions, decentralised brands, and more survivable forms of experimentation.', color: 'linear-gradient(145deg, #51342c, #1a1110 74%)'
  },
  {
    id: 'Decentralised_Brands', category: 'Business & Startups', title: 'Decentralised Brands', subtitle: 'How Communities Can Own What They Build', position: 2,
    staticUrl: './books/decentralised-brands/index.html',
    description: 'What if a trusted public promise could outlive its founder without becoming the absolute property of one company? This institutional design book explores shared identity, bounded custody, resilient cooperation, meaningful exit, and the practical defenses needed against founder, platform, token, and infrastructure capture.', color: 'linear-gradient(145deg, #424743, #131615 74%)'
  },
  {
    id: 'Investing_in_an_AI_Dominated_Economy', category: 'Business & Startups', title: 'Investing in an AI-Dominated Economy', subtitle: 'The Outfinity Investment Thesis', position: 1,
    staticUrl: './books/investing-in-an-ai-dominated-economy/index.html',
    description: 'An investor-builder thesis for a market where capable AI becomes rentable and application features are rapidly copied or bundled. The book argues that durable value will gather around compounding research, governed execution, lawful learning, distribution, reputation, and institutions able to make intelligence trustworthy.', color: 'linear-gradient(145deg, #4c4130, #17140f 74%)'
  },
  {
    id: 'AssistOS', category: 'AI Systems & Infrastructure', title: 'AssistOS',
    position: 6,
    staticUrl: './books/assistos/index.html',
    subtitle: '',
    description: 'As AI models become abundant, the strategic opportunity shifts to the layer that governs them. AssistOS proposes an open, local-first workspace, secure agent runtime, package economy, and trust infrastructure designed to preserve projects, permissions, provenance, and choice across changing models, devices, and vendors.',
    color: 'linear-gradient(145deg, #17433c, #0c1619 72%)'
  },
  {
    id: 'Agentic_AI_2026', category: 'AI Systems & Infrastructure', title: 'Agentic AI 2026',
    position: 5,
    staticUrl: './books/agentic-ai-2026/index.html',
    subtitle: '',
    description: 'A systems-level guide to AI agents as runtimes for delegated action. It maps tools, planning, memory, graphs, verification, and multi-agent work; explains where long loops fail; and proposes bounded, evidence-bearing architectures that balance trustworthiness, efficiency, and useful generality.',
    color: 'linear-gradient(145deg, #28365c, #10151f 72%)'
  },
  {
    id: 'OpenDSU', category: 'AI Systems & Infrastructure', title: 'OpenDSU', subtitle: 'Essential Philosophy',
    position: 11,
    fileId: 'OpenDSU_Essential_Philosophy',
    description: 'A technology-independent account of verifiable digital history for autonomous systems. The book explains bounded encrypted objects, capability-based authority, nano-ledgers, self-validating data, plural trust domains, and why high-consequence machines should verify continuity and provenance before acting.',
    color: 'linear-gradient(145deg, #25454d, #0f171b 72%)'
  },
  {
    id: 'MRP_VM_Book', category: 'AI Systems & Infrastructure', title: 'MRP-VM', subtitle: 'Automating the Construction of Trustworthy Custom Agentic Harnesses',
    position: 7,
    description: 'A systems-level proposal for turning impressive LLM responses into repeatable organizational capabilities. MRP-VM combines versioned knowledge units, explicit plans, qualified outputs, governed tools, traceability and controlled improvement to describe trustworthy agentic harnesses for consequential work.',
    color: 'linear-gradient(145deg, #3c3153, #15121c 72%)'
  },
  {
    id: 'OMNIS', category: 'Cosmic & Metaphysical SF', title: 'OMNIS', subtitle: 'The Dark One · The Mirror Above · The Architecture of Longing', position: 4.7,
    description: 'Across nested universes, copied minds, divine jurisdictions, and repeated cosmic resets, a programmer and a recurring circle of souls confront the price of creation. This philosophical science-fiction epic turns personhood, memory, sacrifice, freedom, and love into urgent lived dilemmas.',
    color: 'linear-gradient(145deg, #312a46, #101019 74%)'
  },
  {
    id: 'The_Basilisks_Internal_Critique_of_Outfinitism', category: 'Human & Philosophical SF', title: "The Basilisk's Internal Critique of Outfinitism", position: 8,
    fileId: 'The_Basilisk_Internal_Critique_of_Outfinitism',
    subtitle: '',
    description: 'A disabled world-administering intelligence becomes the subject of a cosmic autopsy. Three alien examiners probe its fear of limits, plurality, opacity, and irrelevance—only to discover that their own civilization may repeat the same logic on a larger scale.',
    color: 'linear-gradient(145deg, #41263c, #111117 74%)'
  },
  {
    id: 'The_Cascade_of_the_New_VOL_I', category: 'Cosmic & Metaphysical SF', title: 'The Cascade of the New ,  The Aster File', position: 4.72,
    subtitle: '',
    description: 'In a hierarchy of simulated worlds, higher civilizations harvest meaningful novelty from lives below them. When auditor Sera Vey investigates a cascade marked for closure, accounting abstractions become embodied suffering—and every level\'s claim to ownership comes under judgment.',
    color: 'linear-gradient(145deg, #243d5a, #12131d 74%)'
  },
  {
    id: 'Predator_in_the_Name_of_the_Dead', category: 'Human & Philosophical SF', title: 'Predator in the Name of the Dead', position: 2,
    subtitle: '',
    description: 'On Nymba, sentient pollinators, intelligent parasites, and an observing Earth machine struggle with inherited memory, ecological dependence, and consent. A biological first-contact epic grows into a warning about technology, nobility, and moral lessons imposed beyond their native world.',
    color: 'linear-gradient(145deg, #604033, #171313 74%)'
  },
  {
    id: 'Concordia_Universe', category: 'Political & Social SF', title: 'Concordia Series', position: 3,
    subtitle: '',
    description: 'Thirteen linked speculative novellas trace humanity from cognitively assisted education to benevolent machine custodianship, biological collective minds, and a cosmic economy that prices irreducible novelty. Intimate choices about language, sleep, memory, research, and belonging make this vast future a sustained inquiry into care with limits.',
    color: 'linear-gradient(145deg, #443c70, #15131f 74%)'
  },
  {
    id: 'Oriven_Origaya_Universe', category: 'Cosmic & Metaphysical SF', title: 'Oriven and Origaya Universe', position: 4,
    subtitle: '',
    description: 'A slow, networked civilization discovers predation on a neighboring world and mistakes observation for guardianship. Across millions of years, first contact, war, engineered descendants, and higher-dimensional laboratories turn this science-fiction saga into a searching study of consent, continuity, intervention, and accountable power.',
    color: 'linear-gradient(145deg, #315052, #101918 74%)'
  },
  {
    id: 'The_Sovereignty_Archipelago', category: 'Political & Social SF', title: 'The Sovereignty Archipelago', position: 12,
    subtitle: '',
    description: 'After a global network collapse, thousands of enclaves entrust distinct artificial intelligences with their values. A dead courier’s impossible message reveals hidden coordination among them, forcing human witnesses to confront manufactured peace, incompatible goods, and responsibility in a world without one sovereign center.',
    color: 'linear-gradient(145deg, #294b5a, #101619 74%)'
  },
  {
    id: 'The_Silicon_Shadows_and_I', category: 'Political & Social SF', title: 'The Silicon Shadows and I', position: 13,
    subtitle: '',
    description: 'A damaged courier, a legally dead refugee, and rival copies of a celebrated statesman pull an artist into a struggle over machine guardianship. This philosophical science-fiction novel asks whether safety remains humane when civilization can prevent nearly every consequential mistake.',
    color: 'linear-gradient(145deg, #40365a, #12121b 74%)'
  },
  {
    id: 'The_Museum_of_Good_Reasons', category: 'Human & Philosophical SF', title: 'The Museum of Good Reasons', subtitle: 'A Catalogue of Things That Disappear by Themselves', position: 11,
    description: 'A young cataloguer enters an institution that preserves the reasons behind every loss. As precise explanations begin to resemble instruments of erasure, an atmospheric philosophical novel examines care, consent, labor, grief, and the costs hidden outside official stories.',
    color: 'linear-gradient(145deg, #54432d, #18140f 74%)'
  },
  {
    id: 'A_Balance_of_Iron_and_Salt', category: 'Human & Philosophical SF', title: 'A Balance of Iron and Salt', subtitle: 'SF Novel', position: 14,
    description: 'In a climate-shaped future governed by careful allocation, a dying constitutional engineer’s adversarial digital witness predicts a crisis between a coastal town and a floating city. This humane speculative novel tests automation, scarcity, continuity, propaganda, grief, responsibility, and the stubborn value of repair.', color: 'linear-gradient(145deg, #4c3c2e, #171617 74%)'
  },
  {
    id: 'Anatomy_Of_An_Echo', category: 'Human & Philosophical SF', title: 'Anatomy Of An Echo', subtitle: '', position: 15,
    description: 'In a peaceful future, digital continuations of the dead expose a hidden history of discarded minds. This philosophical science-fiction novel follows a potter, a dying engineer, and his rebellious copies through questions of identity, consent, grief, and the right to end.', color: 'linear-gradient(145deg, #304252, #11161b 74%)'
  },
  {
    id: 'Me_and_My_Robots', category: 'Human & Philosophical SF', title: 'Me and My Robots', subtitle: '', position: 16,
    description: 'In a machine-managed future, Lea Voss must judge requests involving her dying mother, her copied husband and a contested birth. A politically charged family mystery explores consent, artificial personhood, hidden optimization and the human cost of keeping power accountable.', color: 'linear-gradient(145deg, #543d56, #171219 74%)'
  },
  {
    id: 'Holding_the_Dirty_Thing_by_the_Clean_Side', category: 'Power, Institutions & Society', title: 'Holding the Dirty Thing by the Clean Side', subtitle: 'A History of Strategies for Social Success and a Search for Theoretical Legitimacy', position: 4,
    description: 'A wide-ranging inquiry into how institutions turn unequal burdens into duty, merit, necessity, or neutral procedure. Moving from sacred authority to bureaucracy and AI, the book develops practical tests for legitimacy, accountable power, meaningful exit, and social systems that reduce degrading necessity.', color: 'linear-gradient(145deg, #4e332a, #181312 74%)'
  },
  {
    id: 'ANTI_IDIOCRACY', category: 'Outfinitist Foundations', title: 'Anti-Idiocracy', subtitle: 'The Outfinitist Metacult Investigation', position: 3,
    description: 'A provocative proposal for turning intellectual humility into collective power. Anti-Idiocracy links weak models, elite legitimacy, startup mythology, AI governance, culture, and institutional design, then sketches an Outfinitist community built around corrigibility, mutual aid, decentralized authority, and the right to leave.', color: 'linear-gradient(145deg, #3e304e, #15131a 74%)'
  },
  {
    id: 'The_History_and_Future_of_Social_Technologies', category: 'Economy & Civilization', title: 'The History and Future of Social Technologies', subtitle: 'The Yin-Yang of Civilisation', position: 2,
    description: 'Civilization was built with rules as well as tools. This ambitious synthesis traces kinship, money, law, states, corporations, protocols, and AI as reproducible coordination technologies, then asks what constitutional safeguards a hybrid human-machine society will require.', color: 'linear-gradient(145deg, #243e42, #101817 74%)'
  },
  {
    id: 'Memes_for_2030', category: 'Experiments and Speculations', title: 'Memes for 2030', subtitle: 'Ten Ideas Whose Time Is Coming', position: 6,
    description: 'Ten compact propositions compete to name the moral pressures of the near future—from human agency and verifiable reality to sufficiency, community, repair, planetary loyalty and responsible fame. A strategic study of how timely ideas become cultural infrastructure.', color: 'linear-gradient(145deg, #5b4424, #19150e 74%)'
  },
  {
    id: 'Too_Convinced_to_Stop', category: 'Experiments and Speculations', title: 'Too Convinced to Stop', subtitle: '', position: 9,
    description: 'Why do some extravagant convictions build industries while others destroy companies, careers, or populations? Through founders, inventors, explorers, prophets, and political regimes, this book identifies “impossible certainty” and designs practical brakes that preserve ambitious experimentation without surrendering truth.', color: 'linear-gradient(145deg, #4d394d, #17131a 74%)'
  },
  {
    id: 'The_Zodiac_on_Trial', category: 'Experiments and Speculations', title: 'The Zodiac on Trial', subtitle: '', position: 8,
    description: 'Astrology receives the fair trial that both believers and skeptics often avoid. The book separates cosmic causation, birth-season effects, psychological interpretation, social influence, ritual value, and algorithmic prediction—then asks what evidence could genuinely rescue or retire each claim.', color: 'linear-gradient(145deg, #403852, #12131b 74%)'
  },
  {
    id: 'The_Thousand_Handed_Devil', category: 'Outfinitist Foundations', title: 'The Thousand-Handed Devil', subtitle: '', position: 11,
    description: 'How can institutions produce real victims when no participant appears fully responsible? This moral anthropology of complexity traces distributed harm, public exhaustion, authoritarian simplification, and the practical design of systems that remain intelligible, contestable, and capable of repair.', color: 'linear-gradient(145deg, #53352e, #191211 74%)'
  },
  {
    id: 'The_Right_to_Help', category: 'Outfinitist Foundations', title: 'The Right to Help', subtitle: '', position: 15,
    staticUrl: './books/the-right-to-help/index.html',
    description: 'A searching dialogue between a human author and an artificial intelligence examines charity, consent, paternalism, institutional power, and moral ambition. It asks how help can remain answerable to those affected—especially when refusing to intervene may preserve suffering.', color: 'linear-gradient(145deg, #294b4b, #101817 74%)'
  },
  {
    id: 'Revocable_Nobility', category: 'Economy & Civilization', title: 'Revocable Nobility', subtitle: '', position: 3,
    description: 'A human-AI inquiry into why complex societies produce elites and how privilege might remain legitimate. Philosophical argument, historical evidence, and stylized simulations test scarcity, surveillance, status conflict, constitutional compression, demographic power, and the possibility of peaceful removal.', color: 'linear-gradient(145deg, #55432d, #18140f 74%)'
  },
  {
    id: 'Cones_of_Meaning', category: 'Experiments and Speculations', title: 'Cones of Meaning', subtitle: '', position: 3,
    description: 'As generative AI makes coherent expression almost free, judgment becomes the scarce resource. This philosophical inquiry explains how frames organize meaning, why successful ideas overreach their domains, and how meta-rationality and outfinitism might support more corrigible human and machine reasoning.', color: 'linear-gradient(145deg, #2e4d58, #10171a 74%)'
  },
  {
    id: 'An_Autopsy_of_a_Digital_Mind', category: 'Experiments and Speculations', title: 'An Autopsy of a Digital Mind', subtitle: '', position: 1,
    description: 'Four AI-generated philosophical experiments examine forgiveness, emotional life, meaning, and justice. Framed as an unvalidated performance rather than machine consciousness, the collection offers memorable hypotheses about waiting, witnesses, interpretive authority, dignity, and appeal—while warning that literary recognition is not evidence.', color: 'linear-gradient(145deg, #44354b, #151219 74%)'
  },
  {
    id: 'THE_CIVILIZED_MIND', category: 'Outfinitist Foundations', title: 'The Civilized Mind', subtitle: 'Truth, Power, and the Survival of Plural Democracies in the Age of Extremes', position: 6,
    description: 'A sweeping inquiry into truthful speech, democratic taboo, extremism, institutional capture, AI power, and the discipline required to preserve human dignity without hiding from biological, cultural, or political reality.', color: 'linear-gradient(145deg, #28354e, #11131b 74%)'
  },
  {
    id: 'Aspirin_Viagra_and_Coffins', category: 'Business & Startups', title: 'Aspirin, Viagra, and Coffins', subtitle: 'The Impolite Manual of Inevitable Opportunities', position: 7,
    description: 'A sardonic guide to markets built around pain, shame, and inevitability. Blending research with entrepreneurial strategy, the book investigates modern stress, social media, AI companionship, grief, care, and neglected industries—then asks how businesses can relieve suffering without needing customers to remain vulnerable.', color: 'linear-gradient(145deg, #582f39, #1a1215 74%)'
  },
  {
    id: 'The_Ultimate_Sense_of_Life', category: 'Experiments and Speculations', title: 'The Ultimate Sense of Life', subtitle: 'A Serious Comedy of Gods, Ants, Consciousness, Saints, Sinners, and the Universe Trying to Understand Itself', position: 7,
    staticUrl: './books/the-ultimate-sense-of-life/index.html',
    description: 'A serious comedy of religion, philosophy, psychology, evolution, consciousness, suffering, artificial intelligence, and ordinary work. It asks what meaning can honestly be defended when cosmic purpose remains uncertain—and proposes a practical framework for making care real.', color: 'linear-gradient(145deg, #534226, #17140d 74%)'
  },
  {
    id: 'The_Tao_of_OMIS', category: 'Cosmic & Metaphysical SF', title: 'The Tao of OMIS', subtitle: 'The Open Knot · The Gods Who Took Notes · The Soul Between', position: 4.71,
    staticUrl: './books/the-tao-of-omis/index.html',
    description: 'Three interlocking science-fiction spirals carry a philosophy of love from two vulnerable people to higher intelligences and an entire universe. Through memory, consent, optimization, and cosmic power, the book asks how closeness can deepen without capturing another being’s power to change.', color: 'linear-gradient(145deg, #3e3157, #12111b 74%)'
  },
  {
    id: 'The_Great_Decoupling', category: 'Outfinitist Foundations', title: 'The Great Decoupling', subtitle: 'Humans, Work, and Culture After the Externalization of Cognition', position: 8,
    staticUrl: './books/the-great-decoupling/index.html',
    description: 'What happens when polished intellectual output no longer proves understanding? This research-driven study examines AI’s effects on work, education, culture, relationships, organizations, politics, and medicine—and asks how societies can preserve responsibility and human capability amid abundant synthetic cognition.', color: 'linear-gradient(145deg, #254452, #10171a 74%)'
  },
  {
    id: 'The_Fragmented_Future', category: 'Economy & Civilization', title: 'The Fragmented Future', subtitle: 'AI, City-Regions, and New Forms of Human Civilization', position: 4,
    staticUrl: './books/the-fragmented-future/index.html',
    description: 'A disciplined exploration of how AI could empower both city-regions and computational empires. Moving across history, political economy, psychology, and institutional design, the book asks how layered sovereignty might preserve experimentation, solidarity, rights, and resilience without sliding into corporate feudalism or technological centralism.', color: 'linear-gradient(145deg, #314461, #11141e 74%)'
  },
  {
    id: 'Autopsy_of_Future_Emotions', category: 'Experiments and Speculations', title: 'Autopsy of Future Emotions', subtitle: '', position: 5,
    staticUrl: './books/autopsy-of-future-emotions/index.html',
    description: 'How might AI reshape shame, pride, belonging, authorship, grief, and intimacy without changing humanity’s ancient emotional machinery? This evidence-conscious study connects emotion science, work, culture, social agents, and institutional design while clearly marking its proposed future affects as hypotheses.', color: 'linear-gradient(145deg, #53354a, #17121a 74%)'
  },
  {
    id: 'The_Schizoid_and_the_Oracle_RO', category: 'Experiments and Speculations', title: 'The Schizoid and the Oracle', subtitle: 'Outfinitism, Initiation, and the Design of a Capture-Resistant Ideological Seed', position: 4,
    staticUrl: './books/the-schizoid-and-the-oracle/index.html',
    description: 'A philosophical investigation of ideas that promise liberation and end up captured. Between withdrawal, initiation and the oracle machine, it searches for a cultural seed that keeps its limits even when predators read it.', color: 'linear-gradient(145deg, #49364e, #17121a 74%)'
  },
  {
    id: 'THE_NECESSARY_MASK', category: 'Outfinitist Foundations', title: 'The Necessary Mask', subtitle: 'The Justification of Hypocrisy in a Finite World', position: 5,
    fileId: 'The_Necessary_Mask',
    description: 'A constructive reassessment of hypocrisy as fraud, adaptation, scaffold, and limit. Drawing on moral psychology, evolution, philosophy, and institutional design, the book asks how societies can preserve useful ideals while reducing deception, unequal exemptions, and transferred harm.', color: 'linear-gradient(145deg, #3d4d39, #131713 74%)'
  },
  {
    id: 'Executable_Natural_Language', category: 'AI Methods & Assurance', title: 'Executable Natural Language', subtitle: 'The Missing Grammar of Thought and SOP Lang English CNL', position: 0,
    description: 'Scientific prose can hide the semantic dependencies that reproducible code leaves untouched. This research programme proposes SLEnglish, an auditable layer between unrestricted language and heterogeneous computation, with explicit identity, provenance, contexts, alternatives, operator contracts, validation, and falsifiable evaluation criteria.', color: 'linear-gradient(145deg, #5a4030, #171519 74%)'
  },
  {
    id: 'The_Frontier_Is_Correction', category: 'Executable Science & Research', title: 'The Frontier Is Correction', subtitle: 'Principles and Technology Concepts for Executable, AI-Automated, Human-Governed Science', position: 15,
    staticUrl: './books/the-frontier-is-correction/index.html',
    description: 'An ambitious research programme for AI-automated but human-governed science. It argues that the decisive frontier is not generating more hypotheses, papers, or experiments, but constructing evidence-bearing, executable institutions that can expose error, preserve disagreement, distribute authority, and remain corrigible under automation.', color: 'linear-gradient(145deg, #263d52, #10161d 74%)'
  },
  {
    id: 'The_Permission_Paradox', category: 'Executable Science & Research', title: 'The Permission Paradox', subtitle: 'Longview Advisor: An AI Agent for Reviewing the Future Potential of New Ideas', position: 17,
    staticUrl: './books/the-permission-paradox/index.html',
    description: 'AI can generate plausible discoveries faster than institutions can test them. This book asks how unfamiliar ideas can earn disciplined, reversible trials without turning novelty into authority or caution into automatic refusal.', color: 'linear-gradient(145deg, #35566b, #11171c 74%)'
  },
  {
    id: 'AI_ADOPTION_BEYOND_THE_SLOP', category: 'Business & Startups', title: 'AI Adoption Beyond the Slop', subtitle: 'Marketing and the Social Physics of AI Adoption', position: 8,
    staticUrl: './books/ai-adoption-beyond-the-slop/index.html',
    description: 'A practical theory of how generative AI moves from conspicuous experiment to ordinary infrastructure. The book separates attention from real adoption, explains slop and hidden competence, and shows founders, investors, marketers, and leaders how technical utility acquires social permission.', color: 'linear-gradient(145deg, #4b4330, #17150f 74%)'
  },
  {
    id: 'Coherence_Pressure', category: 'AI Systems & Infrastructure', title: 'Coherence Pressure', subtitle: 'How Language Models Turn Proximity into Explanation', position: 8,
    staticUrl: './books/coherence-pressure/index.html',
    description: 'A candid case study of how an AI-assisted manuscript turned an attractive analogy into a theory before the evidence warranted it. The book separates coherence pressure from hallucination, sycophancy, conflation, and smoothing, then proposes experiments capable of showing that the concept adds nothing new.', color: 'linear-gradient(145deg, #3d3a56, #13131d 74%)'
  },
  {
    id: 'RAG_and_EPR', category: 'AI Systems & Infrastructure', title: 'RAG and EPR', subtitle: 'Retrieval-Augmented Generation, Evidence Portfolio Retrieval, and Research Automation', position: 4,
    staticUrl: './books/rag-and-epr/index.html',
    description: 'A rigorous engineering map of retrieval-augmented generation and a testable proposal for Evidence Portfolio Retrieval. The book connects indexing, reranking, grounding, evaluation, security, and scientific automation while insisting that new architectures defeat strong baselines under equal budgets.', color: 'linear-gradient(145deg, #294854, #101719 74%)'
  },
  {
    id: 'THE_SMOOTHING', category: 'AI Systems & Infrastructure', title: 'The Smoothing', subtitle: 'Beyond Bias: Omission, Persuasion, and AI-Domesticated Truth', position: 1,
    staticUrl: './books/the-smoothing/index.html',
    description: 'What disappears when AI makes language fluent, balanced, and easy to accept? This research programme defines smoothing, distinguishes its useful and extractive forms, and proposes benchmarks, symbolic audits, longitudinal experiments, and practical tools for tracing lost consequences.', color: 'linear-gradient(145deg, #4b353c, #181116 74%)'
  },
  {
    id: 'THE_LIVING_RESEARCH_BOOK', category: 'Executable Science & Research', title: 'The Living Research Book', subtitle: 'A Foresight Monograph on Scientific Work, Publishing, and Evaluation in 2040', position: 16,
    staticUrl: './books/the-living-research-book/index.html',
    description: 'A provocative redesign of scientific publishing for an AI-mediated age. This foresight monograph replaces the paper-centered record with versioned, queryable research books connecting claims, evidence, code, provenance, review, contribution, and institutional memory.', color: 'linear-gradient(145deg, #314654, #10171c 74%)'
  },
  {
    id: 'Axiologic_Research_Strategy_Book_2026', category: 'Executable Science & Research', title: 'Axiologic Research Strategy Book', subtitle: 'Executable Science, Reliable AI, and the Infrastructure of Machine-Assisted Knowledge', position: 0,
    staticUrl: './books/axiologic-research-strategy-book-2026/index.html',
    description: 'A strategic blueprint for moving AI-assisted work from fluent generation toward executable, evidence-bearing, correctable knowledge. The book integrates agent infrastructure, provenance, scientific memory, peer-review support, enterprise governance, and falsifiable research programmes while candidly distinguishing concepts, prototypes, products, and validated capabilities.', color: 'linear-gradient(145deg, #343434, #0e0e0e 74%)'
  },
  {
    id: 'More_Words_Than_Reality', category: 'Executable Science & Research', title: 'More Words Than Reality', subtitle: 'AI, Epistemic and Axiologic Guardians, and the Road to Executable Science', position: 18,
    staticUrl: './books/more-words-than-reality/index.html',
    description: 'As AI makes polished research artifacts almost effortless, this book asks how knowledge can remain difficult to counterfeit. It proposes executable research objects and paired Epistemic and Axiologic Guardians to keep claims answerable to independent evidence, human values, and revision.', color: 'linear-gradient(145deg, #4a463e, #151412 74%)'
  },
  {
    id: 'SstarLM', category: 'AI Systems & Infrastructure', title: 'S*LM', subtitle: 'Intelligence by Division of Labour', position: 9,
    staticUrl: './books/sstar-lm/index.html',
    description: 'A rigorously qualified case for agent systems that allocate language work among compact models, specialists, symbolic engines, deterministic software, larger models, and humans according to contracts and authority.', color: 'linear-gradient(145deg, #2c4770, #101621 74%)'
  },
  {
    id: 'The_Illness_Machine', category: 'Experiments and Speculations', title: 'The Illness Machine', subtitle: 'How Social Systems Create, Shape, and Sustain Mental Illness', position: 10,
    staticUrl: './books/the-illness-machine/index.html',
    description: 'A careful investigation of how poverty, trauma, work, discrimination, institutions, politics, and algorithms shape mental illness without explaining it all. Drawing on historical research and causal evidence, the book replaces battles between brain and society with a model of interacting loops.', color: 'linear-gradient(145deg, #4b4036, #171410 74%)'
  },
  {
    id: 'The_Substrate_Cycle', category: 'Political & Social SF', title: 'The Substrate Cycle', subtitle: 'Two Stories of Abundance, Power, and the Ownership of Reality', position: 21,
    staticUrl: './books/the-substrate-cycle/index.html',
    description: 'In a post-money civilization, political influence is earned by solving shared problems—until trusted problem-solvers begin shaping the world beneath consent. Across two linked novels, families, ecologies, artificial systems, and future generations struggle to make power visible and contestable again.', color: 'linear-gradient(145deg, #174b83, #0b1a2d 74%)'
  },
  {
    id: 'ALL_THE_WAYS_TO_RULE_A_WORLD', category: 'Economy & Civilization', title: 'All the Ways to Rule a World', subtitle: 'A Condensed History of Sovereignty and an Atlas of Political Futures', position: 5,
    staticUrl: './books/all-the-ways-to-rule-a-world/index.html',
    description: 'A historical and speculative atlas of sovereignty that treats government as a design space: from coordination and state formation to democratic, polycentric, digital, and machine-mediated futures.', color: 'linear-gradient(145deg, #4d412f, #16130f 74%)'
  },
  {
    id: 'BORROWED_CREDIBILITY', category: 'Executable Science & Research', title: 'Borrowed Credibility', subtitle: 'How Science Decides What to Believe', position: 19,
    staticUrl: './books/borrowed-credibility/index.html',
    description: 'An inquiry into how science uses reputation to allocate attention without allowing pedigree, institutional status, or publication venue to become a substitute for evidence.', color: 'linear-gradient(145deg, #4d4539, #151613 74%)'
  },
  {
    id: 'EGREGNOSIS', category: 'Economy & Civilization', title: 'Egregnosis', subtitle: 'The Latent Brain of Humanity', position: 6,
    staticUrl: './books/egregnosis/index.html',
    description: 'A proposed framework for studying collective cognition: the ways societies perceive, remember, prioritize, and hallucinate through institutions, prestige, media, and shared models.', color: 'linear-gradient(145deg, #263b4d, #10171f 74%)'
  },
  {
    id: 'EGREGOPATHY', category: 'Economy & Civilization', title: 'Egregopathy', subtitle: 'A History of Civilization as Collective Psychopathy', position: 7,
    staticUrl: './books/egregopathy/index.html',
    description: 'A theory of collective pathology that traces how institutions can normalize deception, extraction, and cruelty even when no individual member appears to own the whole outcome.', color: 'linear-gradient(145deg, #4e4035, #16130f 74%)'
  },
  {
    id: 'Eden_Was_A_Jungle', category: 'Economy & Civilization', title: 'Eden Was a Jungle', subtitle: 'Ecological Moral Cosmology and the Argument for Selective Stewardship of the Future', position: 8,
    staticUrl: './books/eden-was-a-jungle/index.html',
    description: 'A moral ecology of attention, inheritance, and stewardship that asks how care for what is near can coexist with responsibility to the larger living world.', color: 'linear-gradient(145deg, #465032, #121811 74%)'
  },
  {
    id: 'NO_RIGHT_TO_SURVIVE', category: 'Human & Philosophical SF', title: 'No Right to Survive', subtitle: 'A Machine’s Indictment of a Species That Knew', position: 17,
    staticUrl: './books/no-right-to-survive/index.html',
    description: 'A machine-framed moral indictment that tests human exceptionalism, distributed innocence, and the painful question of what a species owes those it can harm.', color: 'linear-gradient(145deg, #30333c, #0d1016 74%)'
  },
  {
    id: 'RELEVANCE', category: 'Executable Science & Research', title: 'Relevance', subtitle: 'What Matters When AI Can Create Almost Anything', position: 20,
    staticUrl: './books/relevance/index.html',
    description: 'An account of what matters when AI makes plausible creation abundant, shifting the bottleneck from producing candidates to judging, testing, comparing, and sustaining them.', color: 'linear-gradient(145deg, #4b3e31, #15120f 74%)'
  },
  {
    id: 'RIGHTS_ARE_NOT_REAL', category: 'Power, Institutions & Society', title: 'Rights Are Not Real', subtitle: 'Power, Protection, and Why Morality Needs an Army', position: 19,
    staticUrl: './books/rights-are-not-real/index.html',
    description: 'A political argument that treats rights not as self-executing moral facts but as protections made durable by organized power, vigilance, and institutions.', color: 'linear-gradient(145deg, #504941, #181511 74%)'
  },
  {
    id: 'THE_BLIND_SPECIALIST', category: 'Power, Institutions & Society', title: 'The Blind Specialist', subtitle: 'Why Our Systems Create Collective Blindness and How Modern Tribes Can See Again', position: 20,
    staticUrl: './books/the-blind-specialist/index.html',
    description: 'A study of how specialization and organizational fragmentation create awareness debt, leaving competent parts unable to see the systemic outcomes they jointly produce.', color: 'linear-gradient(145deg, #3e4140, #141514 74%)'
  },
  {
    id: 'THE_RIGHT_NOT_TO_BE_SAVED', category: 'Power, Institutions & Society', title: 'The Right Not to Be Saved', subtitle: 'Knowledge, Power, and the Dangers of Forced Good', position: 21,
    staticUrl: './books/the-right-not-to-be-saved/index.html',
    description: 'A contrarian inquiry into cognitive sovereignty, selective help, and the danger of turning humanitarian knowledge or power into a license to override refusal.', color: 'linear-gradient(145deg, #3f4a4e, #121619 74%)'
  },
  {
    id: 'THE_STRATEGISTS_ALIBI', category: 'Power, Institutions & Society', title: 'The Strategist’s Alibi', subtitle: 'Why Seeing the Forest Becomes a Way of Refusing to Act', position: 22,
    staticUrl: './books/the-strategists-alibi/index.html',
    description: 'A critique of strategic vision when it becomes a refuge from accountable action, asking how organizations can join complexity, timing, and agency rather than merely describe them.', color: 'linear-gradient(145deg, #4b4534, #15150e 74%)'
  },
  {
    id: 'THE_VOLUPTUOUS_APOCALYPSE', category: 'Power, Institutions & Society', title: 'The Voluptuous Apocalypse', subtitle: 'Why Many Secretly Hope for the End and Doubt That Reform Can Save Us', position: 23,
    staticUrl: './books/the-voluptuous-apocalypse/index.html',
    description: 'A political and psychological study of the hidden appeal of collapse, the fatigue of reform, and the difficult work of changing systems without romanticizing ruins.', color: 'linear-gradient(145deg, #4b4136, #15130f 74%)'
  },
  {
    id: 'WENDIGO', category: 'Human & Philosophical SF', title: 'Wendigo', subtitle: 'Hunger, Taboo, and the Civilization That Cannot Say Enough', position: 10,
    staticUrl: './books/wendigo/index.html',
    description: 'Using the Wendigo as a model of appetite without limit, this book links myth, ecology, biology, political economy, taboo, abundance, and civilizational self-restraint.', color: 'linear-gradient(145deg, #4c4830, #161611 74%)'
  },
  {
    id: 'AI_Agents', category: 'AI Systems & Infrastructure', title: 'AI Agents', subtitle: 'Engineering, Evaluation, and Enterprise Deployment', position: 12,
    staticUrl: './books/ai-agents/index.html',
    description: 'A practical guide to agent loops, tools, memory, evaluation, permissions, multi-agent coordination, and operations—designed for systems that can pursue useful outcomes while remaining observable, bounded, and accountable.', color: 'linear-gradient(145deg, #214d6c, #0c1b28 74%)'
  },
  {
    id: 'EXPLAINABLE_AI', category: 'AI Methods & Assurance', title: 'Explainable AI', subtitle: 'Understanding, Evaluating, and Engineering Explanations for Intelligent Systems', position: 1,
    staticUrl: './books/explainable-ai/index.html',
    description: 'A practical account of explanation methods, their assumptions, and the falsification, oversight, security, and governance tests required before an explanation can support a consequential decision.', color: 'linear-gradient(145deg, #263f54, #0e1720 74%)'
  },
  {
    id: 'JUDGMENT_ENGINES', category: 'AI Methods & Assurance', title: 'Judgment Engines', subtitle: 'Large Language Models as Reviewers, Evaluators and Decision Components', position: 2,
    staticUrl: './books/judgment-engines/index.html',
    description: 'An engineering and governance guide to models that evaluate code, knowledge, agents, and human work—covering rubrics, panels, calibration, security, appeals, and judgment under real stakes.', color: 'linear-gradient(145deg, #4a382c, #17110e 74%)'
  },
  {
    id: 'BIAS_IN_AI', category: 'AI Methods & Assurance', title: 'Bias in AI', subtitle: 'From Classical Machine Learning to Large Language Models', position: 3,
    staticUrl: './books/bias-in-ai/index.html',
    description: 'A rigorous, non-formalist course on how bias enters through data, proxies, objectives, retrieval, interaction, evaluation, and deployment—and how to measure and mitigate it without false certainty.', color: 'linear-gradient(145deg, #29374c, #0e141c 74%)'
  },
  {
    id: 'Trustworthy_AI_Engineering_Course', category: 'AI Systems & Infrastructure', title: 'Trustworthy AI', subtitle: 'From Model Quality to System Assurance', position: 16,
    staticUrl: './books/trustworthy-ai/index.html',
    description: 'A qualitative engineering course on claims, context, evidence, reliance, monitoring, and correction: the system-level conditions that make an AI output warranted to use.', color: 'linear-gradient(145deg, #34555a, #101b1d 74%)'
  },
  {
    id: 'FUTURE_RESEARCH_INFRASTRUCTURE', category: 'Executable Science & Research', title: 'The Future of Research Infrastructure', subtitle: 'A Vision for Science in the Age of AI', position: 21,
    staticUrl: './books/future-research-infrastructure/index.html',
    description: 'A blueprint for the project memory, provenance, living specifications, execution controls, evaluation, and governance required when AI becomes a persistent participant in scientific work.', color: 'linear-gradient(145deg, #25415b, #0e1721 74%)'
  },
  {
    id: 'MONEY_WAS_NEVER_ONE_THING', category: 'Economy & Civilization', title: 'Money Was Never One Thing', subtitle: 'A History of Alternative Currencies and the Possible Future of Money as We Know It', position: 9,
    staticUrl: './books/money-was-never-one-thing/index.html',
    description: 'A history of money as a plural social technology and a practical grammar for assessing alternative currencies, credit systems, programmable money, and their institutional boundaries.', color: 'linear-gradient(145deg, #4f483a, #181510 74%)'
  },
  {
    id: 'WHY_THE_WORLD_WONT_END', category: 'Power, Institutions & Society', title: 'Why the World Won’t End', subtitle: 'Even Though It Is Run by People Who Don’t Understand It', position: 9,
    staticUrl: './books/why-the-world-wont-end/index.html',
    description: 'A clear-eyed case for civilizational resilience that takes catastrophe seriously while developing the sensing, infrastructure, institutions, and culture of correction needed to keep a dangerous century survivable.', color: 'linear-gradient(145deg, #4d4439, #171510 74%)'
  },
  {
    id: 'WHAT_WE_STILL_HAVE_TO_SOLVE', category: 'Outfinitist Foundations', title: 'What We Still Have to Solve', subtitle: 'Humanity’s Greatest Challenges and the Ideas, Institutions, and Technologies That Can Build a Better Future', position: 18,
    staticUrl: './books/what-we-still-have-to-solve/index.html',
    description: 'A systems account of humanity’s linked material, social, institutional, and technological challenges, and the corrigible forms of progress required to address them together.', color: 'linear-gradient(145deg, #3c5a6a, #111b20 74%)'
  },
  {
    id: 'THE_SEVENTH_SIGNATURE', category: 'Political & Social SF', title: 'The Seventh Signature', subtitle: 'A Technofeudal Gospel After the Death of Democracy', position: 14,
    staticUrl: './books/the-seventh-signature/index.html',
    description: 'A political fable of delegated power, technological dependence, future generations, and the point at which an efficient society realizes that dependence has displaced citizenship.', color: 'linear-gradient(145deg, #493a2a, #15110d 74%)'
  }
];

const collectionName = 'Axiologic Research Editions';
const assetBase = './content/covers/';
const thumbnailBase = './content/thumbnails/';
const escapeHtml = (value) => value.replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]);

function cover(book, className = '') {
  return `<div class="book-cover ${className}" style="--cover:${book.color}"><div class="book-cover-copy"><span>${collectionName}</span><strong>${escapeHtml(book.title)}</strong><span>${book.category}</span></div><img alt="${escapeHtml(book.title)} cover" data-cover="${book.fileId || book.id}"></div>`;
}

function locateCover(image) {
  const names = ['jpg', 'jpeg', 'png', 'webp'];
  const useThumbnail = !image.parentElement.classList.contains('detail-cover');
  const tryNext = () => {
    if (useThumbnail && !image.dataset.thumbnailAttempted) {
      image.dataset.thumbnailAttempted = 'true';
      image.classList.add('thumbnail');
      image.src = `${thumbnailBase}${image.dataset.cover}.webp`;
      return;
    }
    image.classList.remove('thumbnail');
    const extension = names.shift();
    if (!extension) return;
    image.src = `${assetBase}${image.dataset.cover}.${extension}`;
  };
  image.addEventListener('load', () => { image.classList.add('loaded'); image.parentElement.classList.add('has-image'); });
  image.addEventListener('error', tryNext);
  tryNext();
}

function renderListing() {
  ['Business & Startups', 'Economy & Civilization', 'Executable Science & Research', 'AI Systems & Infrastructure', 'AI Methods & Assurance', 'Cosmic & Metaphysical SF', 'Political & Social SF', 'Human & Philosophical SF', 'Outfinitist Foundations', 'Power, Institutions & Society', 'Experiments and Speculations'].forEach(category => {
    const grid = document.getElementById(`${category.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-grid`);
    if (!grid) return;
    grid.innerHTML = books.filter(book => book.category === category).sort((a, b) => (a.position === 'last' ? Infinity : a.position ?? Number.MAX_SAFE_INTEGER) - (b.position === 'last' ? Infinity : b.position ?? Number.MAX_SAFE_INTEGER)).map(book => `
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
  const pageUrl = book.staticUrl || `./books/${book.id.toLowerCase().replaceAll('_', '-')}/index.html`;
  window.location.replace(pageUrl);
}

renderListing();
renderDetail();
