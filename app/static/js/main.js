// Mobile nav
const toggle = document.getElementById('navToggle');
const drawer = document.getElementById('navDrawer');
const closeBtn = document.getElementById('navClose');

if (toggle && drawer) {
  toggle.addEventListener('click', () => drawer.classList.toggle('hidden'));
}
if (closeBtn) {
  closeBtn.addEventListener('click', () => drawer.classList.add('hidden'));
}
drawer?.addEventListener('click', (e) => {
  if (e.target === drawer) drawer.classList.add('hidden');
});
