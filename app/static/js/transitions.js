// Page Transition Handlers
document.addEventListener('htmx:beforeSwap', function(evt) {
  // Add exit animation to current content
  const main = document.querySelector('main')
  main.classList.add('opacity-0', 'transform', 'translate-y-4')
  main.style.transition = 'all 0.3s ease-out'
})

document.addEventListener('htmx:afterSwap', function(evt) {
  // Add entrance animation to new content
  const main = document.querySelector('main')
  main.style.opacity = '0'
  main.style.transform = 'translateY(16px)'
  
  requestAnimationFrame(() => {
    main.style.transition = 'all 0.5s ease-out'
    main.style.opacity = '1'
    main.style.transform = 'translateY(0)'
  })
})

// Loading States
document.addEventListener('htmx:beforeRequest', function(evt) {
  // Add loading indicator
  const target = evt.detail.target
  target.classList.add('htmx-request')
})

document.addEventListener('htmx:afterRequest', function(evt) {
  // Remove loading indicator
  const target = evt.detail.target
  target.classList.remove('htmx-request')
})

// Infinite Scroll Handler
document.addEventListener('htmx:load', function() {
  const infiniteScrollContainers = document.querySelectorAll('[data-infinite-scroll]')
  
  infiniteScrollContainers.forEach(container => {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const trigger = entry.target
          const url = trigger.getAttribute('data-next-page')
          if (url) {
            htmx.ajax('GET', url, { target: container, swap: 'beforeend' })
          }
        }
      })
    }, { rootMargin: '200px' })
    
    const trigger = container.querySelector('.infinite-scroll-trigger')
    if (trigger) {
      observer.observe(trigger)
    }
  })
})

// Progressive Image Loading
document.addEventListener('htmx:afterSettle', function() {
  const images = document.querySelectorAll('img[data-src]')
  images.forEach(img => {
    const highResSrc = img.getAttribute('data-src')
    if (highResSrc) {
      const tempImage = new Image()
      tempImage.src = highResSrc
      tempImage.onload = () => {
        img.src = highResSrc
        img.classList.add('loaded')
        img.removeAttribute('data-src')
      }
    }
  })
})

// Add custom classes for loading states
const style = document.createElement('style')
style.textContent = `
  .htmx-request {
    position: relative;
  }
  .htmx-request::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transform: translateX(-100%);
    animation: loading 1.5s infinite;
  }
  @keyframes loading {
    100% { transform: translateX(100%); }
  }
  
  .image-loading {
    position: relative;
    overflow: hidden;
  }
  .image-loading::before {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(5px);
    transition: opacity 0.3s ease-out;
  }
  .image-loading.loaded::before {
    opacity: 0;
  }
`
document.head.appendChild(style)
