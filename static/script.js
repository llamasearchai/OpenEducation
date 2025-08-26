const form = document.getElementById('upload-form');
const filesInput = document.getElementById('files');
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const deckLink = document.getElementById('deck-link');
const noteCount = document.getElementById('note-count');
const titleInput = document.getElementById('title');
const maxTokensInput = document.getElementById('max_tokens');
const overlapTokensInput = document.getElementById('overlap_tokens');
const charSizeInput = document.getElementById('char_size');
const charOverlapInput = document.getElementById('char_overlap');
const collectionInput = document.getElementById('collection');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const files = filesInput.files;
  if (!files || !files.length) {
    alert('Please choose at least one file');
    return;
  }
  statusEl.textContent = 'Uploading and processing… this can take a bit';
  resultEl.classList.add('hidden');
  const fd = new FormData();
  for (const f of files) fd.append('files', f);
  if (titleInput.value.trim()) fd.append('title', titleInput.value.trim());
  if (maxTokensInput.value) fd.append('max_tokens', String(maxTokensInput.value));
  if (overlapTokensInput.value) fd.append('overlap_tokens', String(overlapTokensInput.value));
  if (charSizeInput.value) fd.append('char_size', String(charSizeInput.value));
  if (charOverlapInput.value) fd.append('char_overlap', String(charOverlapInput.value));
  if (collectionInput.value.trim()) fd.append('collection', collectionInput.value.trim());
  // server toggles GPT via env; UI checkbox is informative for now
  try {
    const resp = await fetch('/api/upload', { method: 'POST', body: fd });
    if (!resp.ok) throw new Error(await resp.text());
    const json = await resp.json();
    deckLink.href = json.deck_path;
    deckLink.download = `${json.deck_id}.apkg`;
    noteCount.textContent = `${json.notes} notes generated.`;
    resultEl.classList.remove('hidden');
    statusEl.textContent = 'Done! You can download your deck.';
    await loadDecks();
    if (json.deck_id) {
      deckSelect.value = json.deck_id;
      askDeckSelect.value = json.deck_id;
      // wire sources export links
      document.getElementById('sources-json').href = `/api/decks/${json.deck_id}/sources?fmt=json`;
      document.getElementById('sources-csv').href = `/api/decks/${json.deck_id}/sources?fmt=csv`;
    }
  } catch (err) {
    console.error(err);
    statusEl.textContent = 'Error: ' + (err?.message || err);
  }
});

// Deck list
const deckSelect = document.getElementById('deck-select');
const askDeckSelect = document.getElementById('ask-deck-select');

async function loadDecks() {
  try {
    const resp = await fetch('/api/decks');
    const json = await resp.json();
    const decks = json.decks || [];
    const opts = decks.map(d => `<option value="${d.deck_id}">${d.title} — ${d.deck_id}</option>`).join('');
    deckSelect.innerHTML = `<option value="">All decks</option>` + opts;
    askDeckSelect.innerHTML = `<option value="">All decks</option>` + opts;
  } catch (e) {
    console.warn('Failed to load decks', e);
  }
}

loadDecks();

// Config-driven UI toggles
(async function initConfig(){
  try {
    const resp = await fetch('/api/config');
    const cfg = await resp.json();
    if (!cfg.expose_ask) {
      document.getElementById('ask')?.classList.add('hidden');
    }
  } catch (e) {}
})();

// Semantic search
const searchBtn = document.getElementById('search-btn');
const qInput = document.getElementById('q');
const resultsList = document.getElementById('results');

searchBtn?.addEventListener('click', async () => {
  const q = qInput.value.trim();
  if (!q) return;
resultsList.innerHTML = '<li>Searching…</li>';
  try {
    const deckId = deckSelect.value || '';
    const url = new URL('/api/search', window.location.origin);
    url.searchParams.set('query', q);
    if (deckId) url.searchParams.set('deck_id', deckId);
    const resp = await fetch(url);
    const json = await resp.json();
    if (!resp.ok) throw new Error(JSON.stringify(json));
    resultsList.innerHTML = '';
    for (const r of json.results) {
      const li = document.createElement('li');
      const snippet = (r.text || '').slice(0, 200).replace(/\n/g, ' ');
      li.textContent = `${r.score.toFixed(3)} — ${snippet}${r.text?.length > 200 ? '…' : ''}`;
      resultsList.appendChild(li);
    }
    if (!json.results?.length) resultsList.innerHTML = '<li>No results</li>';
  } catch (err) {
    resultsList.innerHTML = `<li>Error: ${err?.message || err}</li>`;
  }
});

// RAG answer
const askBtn = document.getElementById('ask-btn');
const askInput = document.getElementById('ask-q');
const answerEl = document.getElementById('answer');
const answerSourcesEl = document.getElementById('answer-sources');
const askK = document.getElementById('ask-k');
const askMaxCtx = document.getElementById('ask-maxctx');
const sourcesOnly = document.getElementById('sources-only');

askBtn?.addEventListener('click', async () => {
  const q = askInput.value.trim();
  if (!q) return;
  answerEl.textContent = 'Thinking…';
  answerSourcesEl.innerHTML = '';
  try {
    const deckId = askDeckSelect.value || '';
    const url = new URL('/api/answer', window.location.origin);
    url.searchParams.set('query', q);
    if (askK.value) url.searchParams.set('k', String(askK.value));
    if (askMaxCtx.value) url.searchParams.set('max_ctx', String(askMaxCtx.value));
    if (deckId) url.searchParams.set('deck_id', deckId);
    if (sourcesOnly.checked) url.searchParams.set('sources_only', 'true');
    const resp = await fetch(url);
    const json = await resp.json();
    if (!resp.ok) throw new Error(JSON.stringify(json));
    renderAnswer(answerEl, json.answer || '');
    for (const s of json.sources || []) {
      const li = document.createElement('li');
      const snip = (s.text || '').slice(0, 160).replace(/\n/g, ' ');
      li.textContent = `[${s.index}] ${snip}${(s.text || '').length > 160 ? '…' : ''}`;
      answerSourcesEl.appendChild(li);
    }
  } catch (err) {
    answerEl.textContent = `Error: ${err?.message || err}`;
  }
});

// Minimal markdown-ish rendering for bold/italics and line breaks
function renderAnswer(el, text) {
  if (!text) { el.textContent = ''; return; }
  let html = text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');
  el.innerHTML = `<p>${html}</p>`;
}
