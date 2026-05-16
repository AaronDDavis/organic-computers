// ── Notes accordion ──────────────────────────────────────────────────
function toggleNotes(stage) {
  const panel = document.getElementById('notes-panel-' + stage);
  const btn = panel.previousElementSibling;
  panel.hidden = !panel.hidden;
  btn.classList.toggle('open', !panel.hidden);
}

// Per-stage note index tracker
const noteIndex = {};

function prevNote(stage) {
  const slides = document.querySelectorAll('#notes-panel-' + stage + ' .p-note-slide');
  if (!slides.length) return;
  noteIndex[stage] = noteIndex[stage] || 0;
  slides[noteIndex[stage]].style.display = 'none';
  noteIndex[stage] = (noteIndex[stage] - 1 + slides.length) % slides.length;
  slides[noteIndex[stage]].style.display = '';
  updateCounter(stage, slides.length);
}

function nextNote(stage, total) {
  const slides = document.querySelectorAll('#notes-panel-' + stage + ' .p-note-slide');
  if (!slides.length) return;
  noteIndex[stage] = noteIndex[stage] || 0;
  slides[noteIndex[stage]].style.display = 'none';
  noteIndex[stage] = (noteIndex[stage] + 1) % slides.length;
  slides[noteIndex[stage]].style.display = '';
  updateCounter(stage, slides.length);
}

function updateCounter(stage, total) {
  const counter = document.getElementById('notes-counter-' + stage);
  if (counter) counter.textContent = (noteIndex[stage] + 1) + ' / ' + total;
}
