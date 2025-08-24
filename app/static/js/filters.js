// Category + tag filtering for menu grid
(function () {
    const grid = document.getElementById('menuGrid');
    if (!grid) return;
  
    const cards = Array.from(grid.querySelectorAll('.menu-card'));
    const tabs = Array.from(document.querySelectorAll('#catTabs .tab'));
    const tagInputs = Array.from(document.querySelectorAll('.tag-input'));
  
    let activeCat = 'all';
    let activeTags = new Set();
  
    const apply = () => {
      cards.forEach(card => {
        const cardCat = card.getAttribute('data-cat');
        const cardTags = (card.getAttribute('data-tags') || '').split(',').filter(Boolean);
        const matchesCat = (activeCat === 'all' || cardCat === activeCat);
        const matchesTags = Array.from(activeTags).every(t => cardTags.includes(t));
        card.style.display = (matchesCat && matchesTags) ? '' : 'none';
      });
    };
  
    tabs.forEach(b => b.addEventListener('click', () => {
      tabs.forEach(x => x.classList.remove('is-active'));
      b.classList.add('is-active');
      activeCat = b.getAttribute('data-cat');
      apply();
    }));
  
    tagInputs.forEach(i => i.addEventListener('change', () => {
      const val = i.value;
      if (i.checked) activeTags.add(val); else activeTags.delete(val);
      apply();
    }));
  
    apply();
  })();
  