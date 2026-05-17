/* clinician.js — PCOSense Clinician Portal */

(function () {
  'use strict';

  /* ── Live date in topbar ─────────────────────────── */
  const dateEl = document.getElementById('c-today-date');
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-GB', {
      weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
    });
  }

  /* ── Sidebar collapse toggle ─────────────────────── */
  const shell     = document.getElementById('page-clinician');
  const toggleBtn = document.getElementById('c-sidebar-toggle');
  const STORAGE_KEY = 'pcosense_clinician_sidebar_collapsed';

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
  window.cShowToast = function (message, type = 'success') {
    let toast = document.getElementById('c-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'c-toast';
      toast.className = 'c-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = 'c-toast ' + type;
    void toast.offsetWidth;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
  };

  /* ── Patient queue: live search & filter ─────────── */
  const searchInput = document.getElementById('c-patient-search');
  const stageFilter = document.getElementById('c-stage-filter');
  const tableBody   = document.querySelector('.c-patient-table tbody');

  function filterTable() {
    if (!tableBody) return;
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const stage = stageFilter  ? stageFilter.value : '';
    const rows  = tableBody.querySelectorAll('tr[data-patient]');
    let visible = 0;

    rows.forEach(row => {
      const name      = (row.dataset.patient || '').toLowerCase();
      const rowStage  = (row.dataset.pending  || '');
      const matchQ    = !query || name.includes(query);
      const matchS    = !stage || rowStage === stage;
      const show      = matchQ && matchS;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    let emptyRow = tableBody.querySelector('.c-table-empty');
    if (!emptyRow) {
      emptyRow = document.createElement('tr');
      emptyRow.className = 'c-table-empty';
      emptyRow.innerHTML = '<td colspan="8" style="text-align:center;padding:2rem;color:var(--slate-400);font-size:0.84rem;">No patients match your filter.</td>';
      tableBody.appendChild(emptyRow);
    }
    emptyRow.style.display = visible === 0 ? '' : 'none';
  }

  if (searchInput) searchInput.addEventListener('input', filterTable);
  if (stageFilter) stageFilter.addEventListener('change', filterTable);

  /* ── Row click → patient detail ──────────────────── */
  document.addEventListener('click', function (e) {
    const row = e.target.closest('tr[data-href]');
    if (row) window.location.href = row.dataset.href;
  });

  /* ── Stage 2 form validation ─────────────────────── */
  const stage2Form = document.getElementById('c-stage2-form');
  if (stage2Form) {
    stage2Form.addEventListener('submit', function (e) {
      const inputs = stage2Form.querySelectorAll('input[type="number"][required]');
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
        cShowToast('Please fill in all required lab values.', 'error');
      }
    });
  }

  /* ── Stage 3 form validation ─────────────────────── */
  const stage3Form = document.getElementById('c-stage3-form');
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
        cShowToast('Please fill in all ultrasound fields.', 'error');
      }
    });
  }

  /* ── Clear buttons ───────────────────────────────── */
  document.querySelectorAll('[data-clear-form]').forEach(btn => {
    btn.addEventListener('click', () => {
      const formId = btn.dataset.clearForm;
      const form   = document.getElementById(formId);
      if (form) {
        form.querySelectorAll('input[type="number"]').forEach(inp => { inp.value = ''; inp.style.borderColor = ''; });
        form.querySelectorAll('select').forEach(sel => { sel.selectedIndex = 0; });
      }
    });
  });

})();
