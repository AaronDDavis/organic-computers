/* --- PATIENT NAVIGATION --- */

const P_SECTIONS = ['overview','journeys','journey-detail','journey-detail-old','notes','profile'];
const P_NAV_LINKS = ['overview','journeys','notes','profile'];

function pNav(section) {
P_SECTIONS.forEach(s => {
    const el = document.getElementById('psec-' + s);
    if (el) {
    if (s === section) {
        el.style.display = 'block';
        // Force reflow to restart animation on every click
        void el.offsetWidth; 
        el.classList.add('animate-fade');
    } else {
        el.style.display = 'none';
        el.classList.remove('animate-fade');
    }
    }
});

P_NAV_LINKS.forEach(s => {
    const a  = document.getElementById('pnav-' + s);
    const ma = document.getElementById('pmnav-' + s);
    const active = (s === section);
    if (a)  a.classList.toggle('active', active);
    if (ma) ma.classList.toggle('active', active);
});

if (section == 'journey-detail') {
    injectScoreVisualizers();
}
}

/* ═══════════════════════════════
    DOCTOR NAVIGATION
═══════════════════════════════ */
const D_SECTIONS = ['dashboard','patients','patient-detail','d-profile'];
const D_NAV_LINKS = ['dashboard','patients','d-profile'];

function dNav(section) {
D_SECTIONS.forEach(s => {
    const el = document.getElementById('dsec-' + s);
    if (el) {
    if (s === section) {
        el.style.display = 'block';
        void el.offsetWidth;
        el.classList.add('animate-fade');
    } else {
        el.style.display = 'none';
        el.classList.remove('animate-fade');
    }
    }
});

D_NAV_LINKS.forEach(s => {
    const a = document.getElementById('dnav-' + s);
    if (a) a.classList.toggle('active', s === section);
});

const titles = {
    'dashboard': 'Dashboard',
    'patients': 'Patient Queue',
    'patient-detail': 'Patient Detail',
    'd-profile': 'My Profile',
};
document.getElementById('d-topbar-title').textContent = titles[section] || 'PCOSense';
}

/*
Doctor Filter
*/
function initializeDoctorFilters() {
const statCards = document.querySelectorAll('.d-stat-card');
const tableRows = document.querySelectorAll('.d-table tbody tr');

statCards.forEach(card => {
    card.addEventListener('click', () => {
    // Toggle active state on the clicked card
    const isActive = card.classList.contains('active-filter');
    statCards.forEach(c => c.classList.remove('active-filter'));
    
    if (!isActive) {
        card.classList.add('active-filter');
        const filterType = card.querySelector('.d-stat-label').innerText.toLowerCase();
        
        tableRows.forEach(row => {
        const rowText = row.innerText.toLowerCase();
        // Simple logic: check if row contains "high" for high risk, etc.
        if (filterType.includes('high risk') && rowText.includes('high')) {
            row.style.display = '';
        } else if (filterType.includes('delayed') && rowText.includes('delayed')) {
            row.style.display = '';
        } else if (filterType.includes('total patients')) {
            row.style.display = ''; // Show all
        } else {
            row.style.display = 'none';
        }
        });
    } else {
        // If clicking an already active filter, reset everything
        tableRows.forEach(row => row.style.display = '');
    }
    });
});
}

// Call this function right after handleLogin() successfully logs in a doctor

function injectScoreVisualizers() {
// Find all the big scores on the patient detail page
const scoreElements = document.querySelectorAll('.p-result-score');

scoreElements.forEach(el => {
    // Prevent double-injection if navigated away and back
    if (el.nextElementSibling && el.nextElementSibling.classList.contains('injected-score-bar-bg')) return;
    
    // Extract the float value (e.g., "0.8340 / 1.00" -> 0.834)
    const scoreText = el.innerText.split('/')[0].trim();
    const scoreVal = parseFloat(scoreText);
    
    if (!isNaN(scoreVal)) {
    const percentage = scoreVal.toFixed(1) + '%';
    
    // Determine color based on severity
    let color = 'var(--risk-low)';
    if (scoreVal > 0.5) color = 'var(--risk-med)';
    if (scoreVal > 0.75) color = 'var(--risk-high)';
    
    // Build and inject the DOM elements
    const barBg = document.createElement('div');
    barBg.className = 'injected-score-bar-bg';
    
    const barFill = document.createElement('div');
    barFill.className = 'injected-score-bar-fill';
    barFill.style.width = '0%'; // Start at 0 for animation
    barFill.style.background = color;
    
    barBg.appendChild(barFill);
    el.parentNode.insertBefore(barBg, el.nextSibling);
    
    // Animate it slightly after it mounts
    setTimeout(() => { barFill.style.width = percentage; }, 100);
    }
});
}
