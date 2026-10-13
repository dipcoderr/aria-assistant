  function toggleSidebar() {
    const isOpen = document.body.classList.toggle('sidebar-open');
    document.getElementById('menu-btn').setAttribute('aria-expanded', String(isOpen));
  }

  function closeSidebar() {
    document.body.classList.remove('sidebar-open');
    document.getElementById('menu-btn').setAttribute('aria-expanded', 'false');
  }

  document.getElementById('menu-btn').addEventListener('click', toggleSidebar);
  document.querySelector('.sidebar-backdrop').addEventListener('click', closeSidebar);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeSidebar();
  });

  document.querySelectorAll('[data-prompt]').forEach(button => {
    button.addEventListener('click', () => setPrompt(button.dataset.prompt));
  });
  document.getElementById('tts-toggle').addEventListener('click', toggleTTS);
  document.getElementById('stt-toggle').addEventListener('click', toggleSTT);
  document.querySelector('.file-preview .remove').addEventListener('click', removeFile);
  document.getElementById('file-input').addEventListener('change', event => onFileSelected(event.currentTarget));
  document.querySelector('.attach-btn').addEventListener('click', () => document.getElementById('file-input').click());
  document.getElementById('mic-btn').addEventListener('click', toggleListening);

  document.querySelectorAll('.markdown-content').forEach(el => {
    if (el.querySelector('img')) return;
    el.innerHTML = marked.parse(el.textContent);
  });

  const msgs = document.getElementById('messages');
  msgs.scrollTop = msgs.scrollHeight;

  const ta = document.getElementById('msg-input');
  ta.addEventListener('input', () => {
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
  });

  ta.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const hasFile = document.getElementById('file-input').files.length > 0;
      if (ta.value.trim() || hasFile) submitForm();
    }
  });

  function submitForm() {
    const typing = document.getElementById('typing');
    if (typing) { typing.classList.add('show'); msgs.scrollTop = msgs.scrollHeight; }
    window.speechSynthesis && window.speechSynthesis.cancel();
    document.getElementById('chat-form').submit();
  }
  document.getElementById('chat-form').addEventListener('submit', () => {
    const typing = document.getElementById('typing');
    if (typing) { typing.classList.add('show'); msgs.scrollTop = msgs.scrollHeight; }
    window.speechSynthesis && window.speechSynthesis.cancel();
  });

  function onFileSelected(input) {
    if (input.files && input.files[0]) {
      const name = input.files[0].name;
      document.getElementById('file-name-display').textContent = name;
      document.getElementById('file-preview').classList.add('show');
      updateModeTag('File: ' + name.split('.').pop().toUpperCase());
    }
  }

  function removeFile() {
    document.getElementById('file-input').value = '';
    document.getElementById('file-preview').classList.remove('show');
    updateModeTag('Chat');
  }

  function setPrompt(text) {
    ta.value = text;
    ta.focus();
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
    const labels = {
      'Summarize':'Summarize','Improve':'Improve','Translate':'Translate',
      'Extract':'Extract','Analyze':'Sentiment','Explain':'Explain',
      'Compare':'Compare','pros and cons':'Pros & Cons','Write a short story':'Story',
      'Write a poem':'Poem','Brainstorm':'Brainstorm','quiz':'Quiz',
      'product description':'Creative','JSON':'JSON','report':'Report',
      'Search':'Search','Calculate':'Calculator','time':'Time','Count words':'Word Count'
    };
    for (const [k,v] of Object.entries(labels)) {
      if (text.toLowerCase().includes(k.toLowerCase())) { updateModeTag(v); break; }
    }
  }

  function updateModeTag(label) {
    document.getElementById('mode-tag').textContent = label;
  }

  let recognition = null;
  let isListening = false;

  function setVoiceFeedback(message) {
    document.getElementById('voice-feedback').textContent = message;
  }

  function toggleSTT() {
    if (isListening) {
      stopListening();
      return;
    }
    toggleListening();
  }

  function toggleListening() {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      setVoiceFeedback('Voice input is not supported in this browser. Try Chrome or Edge.');
      return;
    }
    if (isListening) { stopListening(); return; }
    startListening();
  }

  function startListening() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onstart = () => {
      isListening = true;
      document.getElementById('stt-toggle').classList.add('active');
      document.getElementById('mic-btn').classList.add('listening');
      ta.placeholder = '🎤 Listening…';
      setVoiceFeedback('Listening… speak now.');
    };

    recognition.onresult = (e) => {
      const transcript = Array.from(e.results)
        .map(r => r[0].transcript).join('');
      ta.value = transcript;
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
      if (e.results[e.results.length - 1].isFinal) {
        stopListening();
        setTimeout(() => submitForm(), 400);
      }
    };

    recognition.onerror = (e) => {
      const messages = {
        'not-allowed': 'Microphone access is blocked. Allow microphone access in your browser settings.',
        'service-not-allowed': 'The browser speech service is unavailable.',
        'network': 'Speech recognition service unavailable. Check your connection and try again.',
        'no-speech': 'No speech detected. Try again.'
      };
      setVoiceFeedback(messages[e.error] || `Voice input failed: ${e.error}.`);
      stopListening();
    };

    recognition.onend = () => stopListening();
    isListening = true;
    document.getElementById('stt-toggle').classList.add('active');
    document.getElementById('mic-btn').classList.add('listening');
    ta.placeholder = '🎤 Listening…';
    setVoiceFeedback('Starting microphone…');
    try {
      recognition.start();
    } catch (error) {
      recognition = null;
      isListening = false;
      document.getElementById('stt-toggle').classList.remove('active');
      document.getElementById('mic-btn').classList.remove('listening');
      ta.placeholder = 'Ask anything… summarize, translate, search, calculate, write…';
      setVoiceFeedback(`Could not start voice input: ${error.message}`);
    }
  }

  function stopListening() {
    isListening = false;
    document.getElementById('stt-toggle').classList.remove('active');
    document.getElementById('mic-btn').classList.remove('listening');
    ta.placeholder = 'Ask anything… summarize, translate, search, calculate, write…';
    if (recognition) { try { recognition.stop(); } catch(e){} recognition = null; }
  }

  let ttsEnabled = false;

  function toggleTTS() {
    ttsEnabled = !ttsEnabled;
    document.getElementById('tts-toggle').classList.toggle('active', ttsEnabled);
    sessionStorage.setItem('ttsEnabled', String(ttsEnabled));
    if (!ttsEnabled) {
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      document.getElementById('speaking-badge').classList.remove('show');
      setVoiceFeedback('');
      return;
    }
    const replies = document.querySelectorAll('.row.ai .bubble');
    if (replies.length) {
      speakText(replies[replies.length - 1].textContent);
    } else {
      setVoiceFeedback('Speak replies is on. New replies will be read aloud.');
    }
  }

  function speakText(text) {
    if (!ttsEnabled) return;
    if (!window.speechSynthesis || !('SpeechSynthesisUtterance' in window)) {
      setVoiceFeedback('Text-to-speech is not supported in this browser.');
      return;
    }
    window.speechSynthesis.cancel();

    const clean = text
      .replace(/#{1,6}\s/g, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/`{1,3}[^`]*`{1,3}/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/^\s*[-*+]\s/gm, '')
      .replace(/\n{2,}/g, '. ')
      .replace(/\n/g, ' ')
      .trim();

    const utter = new SpeechSynthesisUtterance(clean);
    utter.rate  = 1.0;
    utter.pitch = 1.0;
    utter.volume = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v =>
      /google|natural/i.test(v.name) || v.lang === 'en-US'
    ) || voices.find(v => v.lang && v.lang.toLowerCase().startsWith('en-'));
    if (preferred) utter.voice = preferred;

    const badge = document.getElementById('speaking-badge');
    utter.onstart = () => {
      badge.classList.add('show');
      setVoiceFeedback('');
    };
    utter.onend = () => badge.classList.remove('show');
    utter.onerror = (event) => {
      badge.classList.remove('show');
      setVoiceFeedback(`Speech playback failed: ${event.error || 'unknown error'}.`);
    };

    window.speechSynthesis.speak(utter);
  }

  window.addEventListener('load', () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = () => {};
    }
    ttsEnabled = sessionStorage.getItem('ttsEnabled') === 'true';
    if (ttsEnabled) {
      document.getElementById('tts-toggle').classList.add('active');
      const bubbles = document.querySelectorAll('.row.ai .bubble');
      if (bubbles.length) {
        const last = bubbles[bubbles.length - 1];
        speakText(last.textContent);
      } else {
        setVoiceFeedback('Speak replies is on. New replies will be read aloud.');
      }
    }
  });

  document.getElementById('chat-form').addEventListener('submit', () => {
    sessionStorage.setItem('ttsEnabled', ttsEnabled);
  });

  ta.focus();