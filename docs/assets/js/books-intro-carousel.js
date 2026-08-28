(() => {
  const matrixGlyphs = '01<>/\\{}[]*+−=ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const holdDuration = 1200;
  const bookPalette = ['var(--accent)', 'var(--accent-2)', '#8fbaf2', '#f2a38f', '#cd8ff2', '#ffffff', '#f2d58f', '#8fe3d3'];
  const homePalette = ['var(--accent)', 'var(--accent-2)', '#8fbaf2', '#f2a38f', '#cd8ff2', '#ffffff', '#f2d58f', '#8fe3d3'];
  const readAloud = (() => {
    const supported = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
    let enabled = false;
    let activeUtterance = null;
    let utteranceId = 0;
    let sessionVoice = null;
    const availabilityListeners = new Set();
    const voicePreference = 'axiologic-read-aloud-voice-uri';
    let preferredVoiceUri = (() => {
      try { return window.localStorage.getItem(voicePreference); }
      catch { return null; }
    })();
    const localEnglishVoices = () => {
      if (!supported) return [];
      return window.speechSynthesis.getVoices().filter((voice) => (
        voice.localService && voice.lang.toLowerCase().startsWith('en')
      ));
    };
    const chooseLocalVoice = () => {
      const voices = localEnglishVoices();
      if (!voices.length) { sessionVoice = null; return null; }
      const currentVoice = voices.find((voice) => voice.voiceURI === sessionVoice?.voiceURI);
      if (currentVoice) { sessionVoice = currentVoice; return sessionVoice; }
      const score = (voice) => {
        const name = voice.name.toLowerCase();
        const language = voice.lang.toLowerCase();
        let value = language.startsWith('en-us') ? 40 : language.startsWith('en') ? 20 : 0;
        if (/google us english|microsoft (aria|jenny|ava|emma)|samantha|karen|daniel/.test(name)) value += 80;
        else if (/microsoft|google|apple/.test(name)) value += 45;
        else if (/natural|neural|enhanced|premium/.test(name)) value += 30;
        return value;
      };
      const defaultVoice = voices.find((voice) => voice.default);
      const savedVoice = voices.find((voice) => voice.voiceURI === preferredVoiceUri);
      sessionVoice = defaultVoice || savedVoice || voices.sort((left, right) => score(right) - score(left))[0];
      if (sessionVoice) {
        preferredVoiceUri = sessionVoice.voiceURI;
        try { window.localStorage.setItem(voicePreference, preferredVoiceUri); } catch { /* Storage is optional. */ }
      }
      return sessionVoice;
    };
    const pronunciationText = (text) => text
      .replace(/AssistOS\b/g, 'Assist O S')
      .replace(/OpenDSU\b/g, 'Open D S U')
      .replace(/ACHILLES\b/g, 'Achilles')
      .replace(/MRP-VM\b/g, 'M R P V M');
    const stop = () => {
      utteranceId += 1;
      if (!supported || !activeUtterance) return;
      activeUtterance.onend = null;
      activeUtterance.onerror = null;
      activeUtterance = null;
      window.speechSynthesis.cancel();
    };
    const notifyAvailability = () => {
      const available = Boolean(chooseLocalVoice());
      availabilityListeners.forEach((listener) => listener(available));
    };
    if (supported) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.addEventListener?.('voiceschanged', notifyAvailability);
    }
    return {
      enabled: () => enabled,
      speaking: () => Boolean(activeUtterance),
      available: () => Boolean(chooseLocalVoice()),
      onAvailabilityChange: (listener) => {
        availabilityListeners.add(listener);
        listener(Boolean(chooseLocalVoice()));
        return () => availabilityListeners.delete(listener);
      },
      enable: () => { enabled = Boolean(chooseLocalVoice()); return enabled; },
      disable: () => { enabled = false; stop(); },
      stop,
      speak: (text, onEnd, onError) => {
        if (!enabled || !supported || activeUtterance) return false;
        const voice = sessionVoice || chooseLocalVoice();
        if (!voice) { enabled = false; onError?.('no-local-voice'); return false; }
        const id = ++utteranceId;
        const utterance = new SpeechSynthesisUtterance(pronunciationText(text));
        activeUtterance = utterance;
        const settle = (completed, error) => {
          if (id !== utteranceId || activeUtterance !== utterance) return;
          activeUtterance = null;
          utterance.onend = null;
          utterance.onerror = null;
          if (!enabled) return;
          if (completed) onEnd?.();
          else onError?.(error);
        };
        utterance.voice = voice;
        utterance.lang = voice.lang;
        utterance.rate = 1;
        utterance.pitch = 1;
        utterance.onend = () => settle(true);
        utterance.onerror = (event) => settle(false, event.error);
        try {
          window.speechSynthesis.speak(utterance);
        } catch {
          settle(false, 'speak-failed');
        }
        return true;
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
    carousel.className = 'books-intro-carousel';
    carousel.setAttribute('aria-label', source.dataset.textCarouselLabel || 'Introduction');
    const stage = document.createElement('div');
    stage.className = 'books-intro-carousel-stage';
    stage.setAttribute('aria-live', 'off');
    const controls = document.createElement('div');
    controls.className = 'books-intro-controls';
    controls.innerHTML = '<button type="button" data-carousel-previous>← Previous</button><span class="books-intro-counter" aria-live="polite"></span><button type="button" data-carousel-next>Next →</button><button type="button" class="books-intro-icon-button" data-carousel-toggle aria-label="Pause" title="Pause"><span aria-hidden="true">❚❚</span></button><button type="button" class="books-intro-icon-button" data-carousel-reset aria-label="Restart" title="Restart"><span aria-hidden="true">↺</span></button><button type="button" data-carousel-read-aloud>Read aloud</button><button type="button" data-carousel-view-all>View all messages</button><button type="button" data-carousel-mute hidden>Mute voice</button><span class="books-intro-reading"></span>';
    source.insertBefore(carousel, cards[0]);
    carousel.append(stage, controls);
    const previousArrow = document.createElement('button');
    previousArrow.type = 'button';
    previousArrow.className = 'books-intro-card-arrow previous';
    previousArrow.setAttribute('aria-label', 'Previous message');
    previousArrow.textContent = '';
    const nextArrow = document.createElement('button');
    nextArrow.type = 'button';
    nextArrow.className = 'books-intro-card-arrow next';
    nextArrow.setAttribute('aria-label', 'Next message');
    nextArrow.textContent = '';
    stage.append(previousArrow, nextArrow);

    cards.forEach((card, index) => {
      card.dataset.speechText = card.textContent.trim();
      card.classList.add('books-intro-card');
      card.style.setProperty('--intro-card-color', palette[index % palette.length]);
      card.setAttribute('role', 'group');
      card.setAttribute('aria-roledescription', 'slide');
      card.setAttribute('aria-label', `Message ${index + 1} of ${cards.length}`);
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
    const readAloudButton = controls.querySelector('[data-carousel-read-aloud]');
    const viewAllButton = controls.querySelector('[data-carousel-view-all]');
    const muteButton = controls.querySelector('[data-carousel-mute]');
    const counter = controls.querySelector('.books-intro-counter');
    const reading = controls.querySelector('.books-intro-reading');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let active = 0;
    let paused = reducedMotion;
    let revealTimer;
    let advanceTimer;
    let speechAdvanceTimer;
    let voiceTurn = 0;
    let countdownTimer;
    let nextChangeAt = 0;
    let started = false;
    const mutePreference = 'axiologic-read-aloud-muted';
    let voiceMuted = (() => {
      try { return window.localStorage.getItem(mutePreference) === 'true'; }
      catch { return false; }
    })();

    const messageDuration = (card) => {
      const words = Number(card.dataset.wordCount) || 1;
      return Math.max(3200, Math.min(7200, 1500 + words * 120));
    };
    const setWordDelays = (card) => {
      const words = [...card.querySelectorAll('.books-intro-word')];
      const duration = messageDuration(card);
      const emphasisDuration = Math.min(520, Math.max(320, Math.round(duration * 0.1)));
      const interval = Math.max(0, duration - emphasisDuration) / Math.max(1, words.length - 1);
      card.style.setProperty('--message-duration', `${duration}ms`);
      card.style.setProperty('--word-emphasis-duration', `${emphasisDuration}ms`);
      words.forEach((word, index) => word.style.setProperty('--word-delay', `${Math.round(index * interval)}ms`));
    };
    const clearTimers = () => {
      window.clearTimeout(revealTimer);
      window.clearTimeout(advanceTimer);
      window.clearInterval(countdownTimer);
      nextChangeAt = 0;
    };
    const stopSpeech = () => {
      voiceTurn += 1;
      window.clearTimeout(speechAdvanceTimer);
      readAloud.stop();
    };
    const syncVoiceControl = () => {
      muteButton.hidden = !readAloud.enabled();
      muteButton.textContent = voiceMuted ? 'Unmute voice' : 'Mute voice';
      muteButton.setAttribute('aria-pressed', String(voiceMuted));
    };
    const isVoiceMode = () => readAloud.enabled();
    const isVoicePlayback = () => isVoiceMode() && !voiceMuted;
    const syncToggleControl = () => {
      const isPaused = paused;
      const label = isPaused ? 'Resume' : 'Pause';
      toggle.setAttribute('aria-label', label);
      toggle.title = label;
      toggle.innerHTML = `<span aria-hidden="true">${isPaused ? '▶' : '❚❚'}</span>`;
    };
    const updateReading = () => {
      if (isVoiceMode()) {
        if (paused) reading.textContent = 'Paused';
        else if (voiceMuted) reading.textContent = 'Voice muted';
        else reading.textContent = readAloud.speaking() ? 'Reading aloud' : 'Preparing voice';
        return;
      }
      const seconds = Math.max(0, Math.ceil((nextChangeAt - Date.now()) / 1000));
      reading.textContent = paused ? 'Paused' : `Next in ${seconds} sec`;
    };
    const schedule = () => {
      clearTimers();
      if (!started) return;
      if (paused) { updateReading(); return; }
      if (isVoiceMode()) { updateReading(); return; }
      const duration = messageDuration(cards[active]);
      nextChangeAt = Date.now() + duration + holdDuration;
      updateReading();
      countdownTimer = window.setInterval(updateReading, 250);
      revealTimer = window.setTimeout(() => {
        cards[active].classList.add('is-resting');
        advanceTimer = window.setTimeout(() => show(active + 1), holdDuration);
      }, duration);
    };
    const show = (index, restart = false, startVoice = false) => {
      if (!started) return;
      if (startVoice) stopSpeech();
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
      if (startVoice) speakActive();
    };
    const speakActive = () => {
      if (paused || !isVoicePlayback() || readAloud.speaking()) return;
      const turn = ++voiceTurn;
      const spokenCard = active;
      const started = readAloud.speak(cards[spokenCard].dataset.speechText, () => {
        if (turn !== voiceTurn || spokenCard !== active || paused || !isVoicePlayback()) return;
        reading.textContent = 'Next message…';
        speechAdvanceTimer = window.setTimeout(() => {
          if (turn !== voiceTurn || spokenCard !== active || paused || !isVoicePlayback()) return;
          show(spokenCard + 1);
          speakActive();
        }, 700);
      }, (error) => {
        if (turn !== voiceTurn || spokenCard !== active || paused || !isVoicePlayback()) return;
        const detail = error ? ` (${error})` : '';
        reading.textContent = `Voice interrupted${detail} — press Read aloud to retry`;
      });
      if (started) updateReading();
    };
    const navigate = (index) => {
      stopSpeech();
      show(index);
      if (isVoicePlayback() && !paused) speakActive();
    };
    const setPaused = (value) => {
      paused = value;
      if (paused) stopSpeech();
      syncToggleControl();
      schedule();
      if (!paused && isVoicePlayback()) speakActive();
    };
    const messageDialog = document.createElement('div');
    messageDialog.className = 'books-intro-message-dialog';
    messageDialog.hidden = true;
    messageDialog.innerHTML = '<div class="books-intro-message-dialog-backdrop" data-message-dialog-close></div><section class="books-intro-message-dialog-panel" role="dialog" aria-modal="true" aria-labelledby="all-messages-title" tabindex="-1"><div class="books-intro-message-dialog-head"><h2 id="all-messages-title">All messages</h2><button type="button" class="books-intro-message-dialog-close" data-message-dialog-close aria-label="Close all messages">×</button></div><div class="books-intro-message-dialog-copy"></div></section>';
    document.body.append(messageDialog);
    const messageDialogPanel = messageDialog.querySelector('.books-intro-message-dialog-panel');
    const messageDialogCopy = messageDialog.querySelector('.books-intro-message-dialog-copy');
    const messages = cards.map((card) => card.dataset.speechText);
    for (let index = 0; index < messages.length; index += 4) {
      const message = document.createElement('p');
      message.textContent = messages.slice(index, index + 4).join(' ');
      messageDialogCopy.append(message);
    }
    let resumeAfterDialog = false;
    const closeAllMessages = () => {
      messageDialog.hidden = true;
      viewAllButton.focus();
      if (resumeAfterDialog) setPaused(false);
      resumeAfterDialog = false;
    };
    const openAllMessages = () => {
      resumeAfterDialog = !paused;
      if (resumeAfterDialog) setPaused(true);
      messageDialog.hidden = false;
      messageDialogPanel.focus();
    };
    messageDialog.querySelectorAll('[data-message-dialog-close]').forEach((button) => button.addEventListener('click', closeAllMessages));

    const choice = document.createElement('div');
    choice.className = 'books-intro-reading-choice';
    choice.innerHTML = '<div><span class="eyebrow">A short introduction</span><h2>Here is a brief presentation of this page.</h2><p>You can read it yourself or have it read aloud.</p><div class="books-intro-reading-choice-actions"><button type="button" data-choice-text>Start text presentation</button><button type="button" data-choice-voice>Read aloud</button></div></div>';
    carousel.classList.add('is-awaiting-choice');
    stage.append(choice);
    const choiceTitle = choice.querySelector('h2');
    const choiceDescription = choice.querySelector('p');
    const choiceVoiceButton = choice.querySelector('[data-choice-voice]');
    readAloud.onAvailabilityChange((available) => {
      readAloudButton.hidden = !available;
      choiceVoiceButton.hidden = !available;
      choiceTitle.textContent = available
        ? 'Here is a brief presentation of this page.'
        : 'Read aloud is unavailable on this device.';
      choiceDescription.textContent = available
        ? 'You can read it yourself or have it read aloud.'
        : 'No compatible local English voice was detected. You can still start the text presentation.';
      if (!available && isVoiceMode()) {
        stopSpeech();
        readAloud.disable();
        syncVoiceControl();
        schedule();
      }
    });
    const closeChoice = () => {
      choice.remove();
      carousel.classList.remove('is-awaiting-choice');
    };
    const startText = () => {
      started = true;
      closeChoice();
      readAloud.disable();
      paused = false;
      syncToggleControl();
      syncVoiceControl();
      show(0, true);
    };
    const startVoice = () => {
      if (!readAloud.enable()) { startText(); return; }
      started = true;
      closeChoice();
      voiceMuted = false;
      try { window.localStorage.setItem(mutePreference, 'false'); } catch { /* Storage is optional. */ }
      paused = false;
      syncToggleControl();
      syncVoiceControl();
      show(0, true, true);
    };
    choice.querySelector('[data-choice-text]').addEventListener('click', startText);
    choiceVoiceButton.addEventListener('click', startVoice);

    previous.addEventListener('click', () => navigate(active - 1));
    next.addEventListener('click', () => navigate(active + 1));
    previousArrow.addEventListener('click', () => navigate(active - 1));
    nextArrow.addEventListener('click', () => navigate(active + 1));
    toggle.addEventListener('click', () => setPaused(!paused));
    reset.addEventListener('click', () => {
      paused = false;
      syncToggleControl();
      show(0, true, isVoicePlayback());
    });
    readAloudButton.addEventListener('click', () => {
      if (!readAloud.enable()) return;
      voiceMuted = false;
      try { window.localStorage.setItem(mutePreference, 'false'); } catch { /* Storage is optional. */ }
      paused = false;
      syncToggleControl();
      syncVoiceControl();
      show(active, true, true);
    });
    viewAllButton.addEventListener('click', openAllMessages);
    muteButton.addEventListener('click', () => {
      voiceMuted = !voiceMuted;
      try { window.localStorage.setItem(mutePreference, String(voiceMuted)); } catch { /* Storage is optional. */ }
      if (voiceMuted) stopSpeech();
      schedule();
      if (!voiceMuted && !paused) speakActive();
      syncVoiceControl();
      updateReading();
    });
    carousel.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') { event.preventDefault(); navigate(active - 1); }
      if (event.key === 'ArrowRight') { event.preventDefault(); navigate(active + 1); }
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !messageDialog.hidden) closeAllMessages();
    });
    document.addEventListener('visibilitychange', () => {
      if (isVoiceMode()) return;
      if (document.hidden) clearTimers();
      else schedule();
    });
    window.addEventListener('pagehide', () => { clearTimers(); stopSpeech(); });
    window.addEventListener('beforeunload', () => { clearTimers(); stopSpeech(); });
  };

  document.querySelectorAll('[data-text-carousel]').forEach(initCarousel);
})();
