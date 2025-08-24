// Simple IntersectionObserver reveal
const faders = document.querySelectorAll('.fade-in');
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) {
      e.target.classList.add('opacity-100', 'translate-y-0');
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.2 });

faders.forEach(el => {
  el.style.opacity = 0.0;
  el.style.transform = 'translateY(8px)';
  io.observe(el);
});

// Basic featured carousel
(function () {
  const root = document.getElementById('featuredCarousel');
  if (!root) return;

  const slides = Array.from(root.querySelectorAll('.carousel-slide'));
  const prev = root.querySelector('.prev');
  const next = root.querySelector('.next');
  const dotsWrap = document.getElementById('carouselDots');
  if (!slides.length || !prev || !next || !dotsWrap) return;

  let i = slides.findIndex(s => s.classList.contains('is-active'));
  if (i < 0) i = 0;
  const makeActive = (idx) => {
    slides.forEach(s => s.classList.remove('is-active'));
    slides[idx].classList.add('is-active');
    dotsWrap.querySelectorAll('button').forEach((b, j) => b.setAttribute('aria-current', j === idx ? 'true' : 'false'));
  };

  // Dots
  slides.forEach((_, j) => {
    const b = document.createElement('button');
    b.addEventListener('click', () => { i = j; makeActive(i); resetAuto(); });
    dotsWrap.appendChild(b);
  });

  const nextSlide = () => { i = (i + 1) % slides.length; makeActive(i); };
  const prevSlide = () => { i = (i - 1 + slides.length) % slides.length; makeActive(i); };
  next.addEventListener('click', () => { nextSlide(); resetAuto(); });
  prev.addEventListener('click', () => { prevSlide(); resetAuto(); });

  let timer = null;
  const startAuto = () => timer = setInterval(nextSlide, 5000);
  const stopAuto = () => { if (timer) clearInterval(timer); timer = null; };
  const resetAuto = () => { stopAuto(); startAuto(); };

  root.addEventListener('mouseenter', stopAuto);
  root.addEventListener('mouseleave', startAuto);

  makeActive(i);
  startAuto();
})();
