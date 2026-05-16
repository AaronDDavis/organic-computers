/*
    Add this somewhere:
    initializeDoctorFilters();
*/

function fillCreds(u, p) {
    document.getElementById('login-username').value = u;
    document.getElementById('login-password').value = p;
}

// Wrap everything in an Immediately Invoked Function Expression (IIFE) to keep the global scope clean
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    
    // Safety Guard: If this form isn't on the current page, stop executing completely.
    if (!signupForm) return;

    // 1. Role Card Selection Logic
    const roleRadios = signupForm.querySelectorAll('.signup-role-radio');
    roleRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        signupForm.querySelectorAll('.signup-role-card').forEach(card => card.classList.remove('selected'));
        const card = radio.closest('.signup-role-card');
        if (card) card.classList.add('selected');
      });
    });

    // Highlight the initially checked radio on page load
    const initialChecked = signupForm.querySelector('.signup-role-radio:checked');
    if (initialChecked) {
      const card = initialChecked.closest('.signup-role-card');
      if (card) card.classList.add('selected');
    }

    // 2. Setup Navigation Button Click Events
    const nextBtn = signupForm.querySelector('button[onclick="goToStep2()"]');
    const backBtn = signupForm.querySelector('button[onclick="goToStep1()"]');

    // Remove inline onclick attributes from HTML and bind them via JS listeners instead
    if (nextBtn) {
      nextBtn.removeAttribute('onclick');
      nextBtn.addEventListener('click', goToStep2);
    }
    if (backBtn) {
      backBtn.removeAttribute('onclick');
      backBtn.addEventListener('click', goToStep1);
    }

    // 3. Server-side Validation Error Redirection Logic
    const hasStep1Error = signupForm.dataset.hasStep1Error === 'true';
    const hasStep2Error = signupForm.dataset.hasStep2Error === 'true';

    if (hasStep2Error && !hasStep1Error) {
      goToStep2();
    }
  });

  // --- Step Navigation Functions ---
  function goToStep2() {
    const usernameInput = document.getElementById('id_username');
    const emailInput = document.getElementById('id_email');
    const firstNameInput = document.getElementById('id_first_name');
    const nameDisplay = document.getElementById('firstname-display');
    const step1 = document.getElementById('signup-step-1');
    const step2 = document.getElementById('signup-step-2');
    const dot1 = document.getElementById('step-dot-1');
    const dot2 = document.getElementById('step-dot-2');
    const passwordInput = document.getElementById('id_password1');

    const username = usernameInput ? usernameInput.value.trim() : '';
    const email = emailInput ? emailInput.value.trim() : '';

    if (!username || !email) {
      if (!username && usernameInput) usernameInput.focus();
      else if (emailInput) emailInput.focus();
      return;
    }

    if (nameDisplay) {
      const first = firstNameInput ? firstNameInput.value.trim() : '';
      nameDisplay.textContent = first || username;
    }

    if (step1) step1.style.display = 'none';
    if (step2) step2.style.display = 'block';
    if (dot1) dot1.classList.remove('active');
    if (dot2) dot2.classList.add('active');
    if (passwordInput) passwordInput.focus();
  }

  function goToStep1() {
    const step1 = document.getElementById('signup-step-1');
    const step2 = document.getElementById('signup-step-2');
    const dot1 = document.getElementById('step-dot-1');
    const dot2 = document.getElementById('step-dot-2');

    if (step2) step2.style.display = 'none';
    if (step1) step1.style.display = 'block';
    if (dot2) dot2.classList.remove('active');
    if (dot1) dot1.classList.add('active');
  }
})();