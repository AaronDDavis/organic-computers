(function () {
  'use strict';

  /* ── Live date in topbar ─────────────────────────── */
  const dateEl = document.getElementById('d-today-date');
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-GB', {
      weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
    });
  }

  /* ── Sidebar collapse toggle ─────────────────────── */
  const shell   = document.getElementById('page-doctor');
  const toggleBtn = document.getElementById('d-sidebar-toggle');

  const STORAGE_KEY = 'pcosense_sidebar_collapsed';

  // Restore preference
  if (shell && localStorage.getItem(STORAGE_KEY) === '1') {
    shell.classList.add('sidebar-collapsed');
  }

  if (toggleBtn && shell) {
    toggleBtn.addEventListener('click', () => {
      const collapsed = shell.classList.toggle('sidebar-collapsed');
      localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0');
    });
  }

  /* ── Toast helper ────────────────────────────────── */
  let toastTimer = null;

  window.dShowToast = function (message, type = 'success') {
    let toast = document.getElementById('d-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'd-toast';
      toast.className = 'd-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = 'd-toast ' + type;
    // Force reflow so transition fires
    void toast.offsetWidth;
    toast.classList.add('show');

    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  };

  /* ── Patient queue: live search & risk filter ────── */
  const searchInput  = document.getElementById('d-patient-search');
  const riskFilter   = document.getElementById('d-risk-filter');
  const tableBody    = document.querySelector('.d-patient-table tbody');

  function filterTable() {
    if (!tableBody) return;
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const risk  = riskFilter  ? riskFilter.value.toLowerCase() : '';
    const rows  = tableBody.querySelectorAll('tr[data-patient]');

    let visible = 0;
    rows.forEach(row => {
      const name     = (row.dataset.patient  || '').toLowerCase();
      const riskVal  = (row.dataset.risk     || '').toLowerCase();
      const matchQ   = !query || name.includes(query);
      const matchR   = !risk  || riskVal === risk;
      const show     = matchQ && matchR;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    // Show empty-state row if nothing matches
    let emptyRow = tableBody.querySelector('.d-table-empty');
    if (!emptyRow) {
      emptyRow = document.createElement('tr');
      emptyRow.className = 'd-table-empty';
      emptyRow.innerHTML = '<td colspan="8" style="text-align:center;padding:2rem;color:var(--slate-400);font-size:0.84rem;">No patients match your filter.</td>';
      tableBody.appendChild(emptyRow);
    }
    emptyRow.style.display = visible === 0 ? '' : 'none';
  }

  if (searchInput) searchInput.addEventListener('input', filterTable);
  if (riskFilter)  riskFilter.addEventListener('change', filterTable);

  /* ── Clinical note: save button ──────────────────── */
  const saveNoteBtn = document.getElementById('d-save-note');
  if (saveNoteBtn) {
    saveNoteBtn.addEventListener('click', () => {
      // Actual POST is handled by Django view via form submit.
      // This provides immediate UI feedback while the form submits.
      saveNoteBtn.textContent = 'Saving…';
      saveNoteBtn.disabled = true;
    });
  }

  /* ── Stage 3 form: clear button ──────────────────── */
  const clearStage3Btn = document.getElementById('d-clear-stage3');
  if (clearStage3Btn) {
    clearStage3Btn.addEventListener('click', () => {
      const form = document.getElementById('d-stage3-form');
      if (form) {
        form.querySelectorAll('input[type="number"]').forEach(inp => {
          inp.value = '';
        });
      }
    });
  }

  /* ── Row click → patient detail navigation ───────── */
  // Rows should have data-href="/patients/<id>/" for real navigation.
  // Using event delegation so it works after any dynamic updates.
  document.addEventListener('click', function (e) {
    const row = e.target.closest('tr[data-href]');
    if (row) {
      window.location.href = row.dataset.href;
    }
  });

  /* ── Form validation: stage 3 ────────────────────── */
  const stage3Form = document.getElementById('d-stage3-form');
  if (stage3Form) {
    stage3Form.addEventListener('submit', function (e) {
      const inputs = stage3Form.querySelectorAll('input[type="number"][required]');
      let valid = true;
      inputs.forEach(inp => {
        inp.style.borderColor = '';
        if (inp.value.trim() === '' || isNaN(parseFloat(inp.value))) {
          inp.style.borderColor = 'var(--risk-high)';
          valid = false;
        }
      });
      if (!valid) {
        e.preventDefault();
        dShowToast('Please fill in all ultrasound fields.', 'error');
      }
    });
  }

})();
