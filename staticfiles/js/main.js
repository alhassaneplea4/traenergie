// Traenergie — main.js

// Auto-dismiss toast messages after 5s
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-autohide]').forEach(el => {
    setTimeout(() => el.remove(), 5000);
  });
});

// HTMX: scroll to top after swap
document.addEventListener('htmx:afterSwap', (e) => {
  if (e.detail.target.id === 'product-table-wrapper') {
    e.detail.target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});

// Confirm dialogs via HTMX
document.addEventListener('htmx:confirm', (e) => {
  if (e.detail.question) {
    if (!window.confirm(e.detail.question)) {
      e.preventDefault();
    }
  }
});

// Number counter animation for hero stats
function animateCounter(el, target, duration = 1500) {
  let start = 0;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start += step;
    if (start >= target) { start = target; clearInterval(timer); }
    el.textContent = Math.floor(start).toLocaleString('fr-FR') + (el.dataset.suffix || '');
  }, 16);
}

// Trigger counters when in viewport
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      animateCounter(el, parseInt(el.dataset.count));
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));
