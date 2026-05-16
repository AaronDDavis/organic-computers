const hamburger = document.getElementById('p-hamburger');
const mobileNav = document.getElementById('p-mobile-nav');
hamburger.addEventListener('click', () => {
mobileNav.classList.toggle('open');
});
// Close drawer when clicking outside
document.addEventListener('click', (e) => {
if (!hamburger.contains(e.target) && !mobileNav.contains(e.target)) {
    mobileNav.classList.remove('open');
}
});
