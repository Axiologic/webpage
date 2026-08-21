(() => {
  const matrixGlyphs = '01<>/\\{}[]*+−=ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const holdDuration = 4000;
  const choiceDuration = 30000;
  const bookPalette = ['var(--accent)', 'var(--accent-2)', '#8fbaf2', '#f2a38f', '#cd8ff2', '#ffffff'];
  const homePalette = ['var(--accent)', 'var(--accent-2)', '#8fbaf2', '#f2a38f', '#ffffff'];
  const readAloud = (() => {
    const supported = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
    let enabled = false;
    let speechId = 0;
    const voicePreference = 'axiologic-read-aloud-voice-uri';
    let preferredVoiceUri = (() => {
      try { return window.localStorage.getItem(voicePreference); }
      catch { return null; }
    })();
    const chooseVoice = () => {
      const score = (voice) => {
        const name = voice.name.toLowerCase();
        const language = voice.lang.toLowerCase();
        let value = language.startsWith('en-us') ? 40 : language.startsWith('en') ? 20 : 0;
        if (/google us english|microsoft (aria|jenny|ava|emma)|samantha|karen|daniel/.test(name)) value += 80;
        else if (/microsoft|google|apple/.test(name)) value += 45;
        else if (/natural|neural|enhanced|premium/.test(name)) value += 30;
        return value;
      };
      const voices = window.speechSynthesis.getVoices()
        .filter((voice) => voice.lang.toLowerCase().startsWith('en'));
      const savedVoice = voices.find((voice) => voice.voiceURI === preferredVoiceUri);
      if (savedVoice) return savedVoice;
      const selectedVoice = voices.sort((left, right) => score(right) - score(left))[0];
      if (selectedVoice) {
        preferredVoiceUri = selectedVoice.voiceURI;
        try { window.localStorage.setItem(voicePreference, preferredVoiceUri); } catch { /* Storage is optional. */ }
      }
      return selectedVoice;
    };
    const pronunciationText = (text) => text
      .replace(/AssistOS\b/g, 'Assist O S')
      .replace(/OpenDSU\b/g, 'Open D S U')
      .replace(/ACHILLES\b/g, 'Achilles')
      .replace(/MRP-VM\b/g, 'M R P V M');
    const stop = () => {
      speechId += 1;
      if (supported) window.speechSynthesis.cancel();
    };
    return {
      enabled: () => enabled,
      enable: () => { enabled = supported; return enabled; },
      disable: () => { enabled = false; stop(); },
      stop,
      speak: (text, onEnd) => {
        if (!enabled || !supported) return;
        stop();
        const id = speechId;
        const utterance = new SpeechSynthesisUtterance(pronunciationText(text));
        const voice = chooseVoice();
        if (voice) {
          utterance.voice = voice;
          utterance.lang = voice.lang;
        } else utterance.lang = 'en-US';
        utterance.rate = 1.25;
        utterance.pitch = 1;
        utterance.onend = () => { if (id === speechId && enabled) onEnd?.(); };
        window.speechSynthesis.speak(utterance);
      }
    };
  })();

  const decorateWords = (card) => {
    const textNodes = [];
    const walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) => /\S/.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
    });
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    let wordIndex = 0;
    textNodes.forEach((node) => {
      const fragment = document.createDocumentFragment();
      node.nodeValue.split(/(\s+)/).forEach((part) => {
        if (!part) return;
        if (/^\s+$/.test(part)) fragment.append(part);
        else {
          const word = document.createElement('span');
          word.className = 'books-intro-word';
          word.textContent = part;
          fragment.append(word);
          wordIndex += 1;
        }
      });
      node.replaceWith(fragment);
    });
    return wordIndex;
  };

  const addMatrixRain = (card) => {
    const rain = document.createElement('span');
    rain.className = 'books-intro-matrix-rain';
    rain.setAttribute('aria-hidden', 'true');
    for (let column = 0; column < 10; column += 1) {
      const stream = document.createElement('span');
      stream.textContent = Array.from({ length: 24 }, () => matrixGlyphs[Math.floor(Math.random() * matrixGlyphs.length)]).join('\n');
      stream.style.left = `${6 + column * 10}%`;
      stream.style.setProperty('--rain-speed', `${0.8 + Math.random() * 0.8}s`);
      stream.style.setProperty('--rain-delay', `${-Math.random() * 1.5}s`);
      rain.append(stream);
    }
    card.append(rain);
  };

  const initCarousel = (source) => {
    const cards = [...source.querySelectorAll(':scope > p')];
    if (cards.length < 2) return;
    const palette = source.classList.contains('books-intro') ? bookPalette : homePalette;

    const carousel = document.createElement('section');
    carousel.className = 'books-intro-carousel is-awaiting-choice';
    carousel.setAttribute('aria-label', source.dataset.textCarouselLabel || 'Introduction');
    const stage = document.createElement('div');
    stage.className = 'books-intro-carousel-stage';
    stage.setAttribute('aria-live', 'off');
    const controls = document.createElement('div');
    controls.className = 'books-intro-controls';
    controls.innerHTML = '<button type="button" data-carousel-previous>← Previous</button><span class="books-intro-counter" aria-live="polite"></span><button type="button" data-carousel-next>Next →</button><button type="button" data-carousel-toggle>Pause</button><button type="button" data-carousel-reset>Reset</button><button type="button" data-carousel-show>Show</button><button type="button" data-carousel-read-aloud>Read aloud</button><button type="button" data-carousel-mute hidden>Mute voice</button><span class="books-intro-reading"></span>';
    source.insertBefore(carousel, cards[0]);
    carousel.append(stage, controls);
    const previousArrow = document.createElement('button');
    previousArrow.type = 'button';
    previousArrow.className = 'books-intro-card-arrow previous';
    previousArrow.setAttribute('aria-label', 'Previous paragraph');
    previousArrow.textContent = '';
    const nextArrow = document.createElement('button');
    nextArrow.type = 'button';
    nextArrow.className = 'books-intro-card-arrow next';
    nextArrow.setAttribute('aria-label', 'Next paragraph');
    nextArrow.textContent = '';
    stage.append(previousArrow, nextArrow);

    cards.forEach((card, index) => {
      card.dataset.speechText = card.textContent.trim();
      card.classList.add('books-intro-card');
      card.style.setProperty('--intro-card-color', palette[index % palette.length]);
      card.setAttribute('role', 'group');
      card.setAttribute('aria-roledescription', 'slide');
      card.setAttribute('aria-label', `Paragraph ${index + 1} of ${cards.length}`);
      const copy = document.createElement('span');
      copy.className = 'books-intro-card-copy';
      while (card.firstChild) copy.append(card.firstChild);
      card.append(copy);
      card.dataset.wordCount = decorateWords(copy);
      addMatrixRain(card);
      card.hidden = true;
      stage.append(card);
    });

    const previous = controls.querySelector('[data-carousel-previous]');
    const next = controls.querySelector('[data-carousel-next]');
    const toggle = controls.querySelector('[data-carousel-toggle]');
    const reset = controls.querySelector('[data-carousel-reset]');
    const showButton = controls.querySelector('[data-carousel-show]');
    const readAloudButton = controls.querySelector('[data-carousel-read-aloud]');
    const muteButton = controls.querySelector('[data-carousel-mute]');
    const counter = controls.querySelector('.books-intro-counter');
    const reading = controls.querySelector('.books-intro-reading');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let active = 0;
    let paused = reducedMotion;
    let revealTimer;
    let advanceTimer;
    let voiceTimer;
    let countdownTimer;
    let choiceTimer;
    let nextChangeAt = 0;
    const mutePreference = 'axiologic-read-aloud-muted';
    let voiceMuted = (() => {
      try { return window.localStorage.getItem(mutePreference) === 'true'; }
      catch { return false; }
    })();

    const readingTime = (card) => {
      const words = Number(card.dataset.wordCount) || 1;
      return Math.max(8, Math.ceil((words / 240) * 60));
    };
    const setWordDelays = (card) => {
      const words = [...card.querySelectorAll('.books-intro-word')];
      const duration = readingTime(card) * 1000;
      const interval = duration / Math.max(1, words.length);
      words.forEach((word, index) => word.style.setProperty('--word-delay', `${Math.round(index * interval)}ms`));
    };
    const revealAllWords = (card) => card.querySelectorAll('.books-intro-word').forEach((word) => {
      word.style.animation = 'none';
      word.style.opacity = '1';
      word.style.filter = 'none';
      word.style.transform = 'none';
    });
    const clearWordOverrides = () => cards.forEach((card) => card.querySelectorAll('.books-intro-word').forEach((word) => {
      word.style.removeProperty('animation');
      word.style.removeProperty('opacity');
      word.style.removeProperty('filter');
      word.style.removeProperty('transform');
    }));
    const clearTimers = () => {
      window.clearTimeout(revealTimer);
      window.clearTimeout(advanceTimer);
      window.clearTimeout(voiceTimer);
      window.clearInterval(countdownTimer);
      nextChangeAt = 0;
    };
    const syncVoiceControl = () => {
      muteButton.hidden = !readAloud.enabled();
      muteButton.textContent = voiceMuted ? 'Unmute voice' : 'Mute voice';
      muteButton.setAttribute('aria-pressed', String(voiceMuted));
    };
    const updateReading = () => {
      const seconds = Math.max(0, Math.ceil((nextChangeAt - Date.now()) / 1000));
      reading.textContent = paused ? 'Paused' : `Next in ${seconds} sec`;
    };
    const schedule = () => {
      clearTimers();
      if (paused) { updateReading(); return; }
      const duration = readingTime(cards[active]) * 1000;
      nextChangeAt = Date.now() + duration + 500 + holdDuration;
      updateReading();
      countdownTimer = window.setInterval(updateReading, 250);
      revealTimer = window.setTimeout(() => {
        cards[active].classList.add('is-resting');
        advanceTimer = window.setTimeout(() => show(active + 1), holdDuration);
      }, duration + 500);
    };
    const show = (index, restart = false) => {
      readAloud.stop();
      const nextActive = (index + cards.length) % cards.length;
      if (restart && nextActive === active) {
        cards[active].classList.remove('is-active', 'is-resting');
        void cards[active].offsetWidth;
      }
      active = nextActive;
      cards.forEach((card, cardIndex) => {
        const selected = cardIndex === active;
        card.hidden = !selected;
        card.classList.toggle('is-active', selected);
        card.classList.remove('is-resting');
      });
      setWordDelays(cards[active]);
      counter.textContent = `${active + 1} / ${cards.length}`;
      updateReading();
      schedule();
      if (readAloud.enabled() && !voiceMuted) {
        voiceTimer = window.setTimeout(() => speakActive(), 240);
      }
    };
    const speakActive = () => {
      if (!readAloud.enabled() || voiceMuted) return;
      readAloud.speak(cards[active].dataset.speechText);
    };
    const navigate = (index) => {
      readAloud.stop();
      show(index);
    };
    const setPaused = (value) => {
      paused = value;
      if (paused) readAloud.stop();
      toggle.textContent = paused ? 'Resume' : 'Pause';
      updateReading();
      if (!paused && readAloud.enabled() && !voiceMuted) speakActive();
      schedule();
    };
    const showAllWords = () => {
      paused = true;
      toggle.textContent = 'Resume';
      clearTimers();
      readAloud.disable();
      syncVoiceControl();
      cards[active].classList.add('is-resting');
      revealAllWords(cards[active]);
      updateReading();
    };
    const choice = document.createElement('div');
    choice.className = 'books-intro-reading-choice';
    choice.innerHTML = '<div><span class="eyebrow">Browser voice</span><h2>Would you like this text read aloud?</h2><p>Choose a mode, or wait 30 seconds to show the text.</p><div class="books-intro-reading-choice-actions"><button type="button" data-choice-voice>Read aloud</button><button type="button" data-choice-text>Show text</button></div></div>';
    stage.append(choice);
    const closeChoice = () => {
      window.clearTimeout(choiceTimer);
      choice.remove();
      carousel.classList.remove('is-awaiting-choice');
    };
    const startText = () => {
      closeChoice();
      readAloud.disable();
      syncVoiceControl();
      paused = false;
      toggle.textContent = 'Pause';
      clearWordOverrides();
      show(0, true);
    };
    const startVoice = () => {
      closeChoice();
      if (!readAloud.enable()) { startText(); return; }
      paused = false;
      toggle.textContent = 'Pause';
      syncVoiceControl();
      clearWordOverrides();
      show(0, true);
    };
    choice.querySelector('[data-choice-voice]').addEventListener('click', startVoice);
    choice.querySelector('[data-choice-text]').addEventListener('click', startText);
    choiceTimer = window.setTimeout(startText, choiceDuration);

    previous.addEventListener('click', () => navigate(active - 1));
    next.addEventListener('click', () => navigate(active + 1));
    previousArrow.addEventListener('click', () => navigate(active - 1));
    nextArrow.addEventListener('click', () => navigate(active + 1));
    toggle.addEventListener('click', () => setPaused(!paused));
    reset.addEventListener('click', () => {
      readAloud.stop();
      paused = false;
      toggle.textContent = 'Pause';
      clearWordOverrides();
      show(0, true);
    });
    showButton.addEventListener('click', showAllWords);
    readAloudButton.addEventListener('click', () => {
      if (!readAloud.enable()) return;
      voiceMuted = false;
      try { window.localStorage.setItem(mutePreference, 'false'); } catch { /* Storage is optional. */ }
      paused = false;
      toggle.textContent = 'Pause';
      syncVoiceControl();
      clearWordOverrides();
      show(active, true);
    });
    muteButton.addEventListener('click', () => {
      voiceMuted = !voiceMuted;
      try { window.localStorage.setItem(mutePreference, String(voiceMuted)); } catch { /* Storage is optional. */ }
      window.clearTimeout(voiceTimer);
      if (voiceMuted) readAloud.stop();
      else if (!paused && readAloud.enabled()) speakActive();
      syncVoiceControl();
      updateReading();
    });
    carousel.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') { event.preventDefault(); navigate(active - 1); }
      if (event.key === 'ArrowRight') { event.preventDefault(); navigate(active + 1); }
    });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) { clearTimers(); readAloud.stop(); }
      else schedule();
    });
  };

  document.querySelectorAll('[data-text-carousel]').forEach(initCarousel);
})();
