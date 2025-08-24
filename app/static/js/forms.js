// Simple AJAX form helper posting FormData to our API, showing messages
function setupAjaxForm({ formId, endpoint, successText, errorText }) {
    const form = document.getElementById(formId);
    if (!form) return;
    const msgEl = document.getElementById(formId.replace('Form','Msg')) || form.querySelector('.form-msg');
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      try {
        const res = await fetch(endpoint, { method: 'POST', body: fd });
        const data = await res.json().catch(() => ({}));
        if (res.ok && data?.success) {
          if (msgEl) { msgEl.textContent = successText; msgEl.style.color = '#C8A349'; }
          form.reset();
        } else {
          if (msgEl) { msgEl.textContent = errorText; msgEl.style.color = '#ff6b6b'; }
        }
      } catch (err) {
        if (msgEl) { msgEl.textContent = errorText; msgEl.style.color = '#ff6b6b'; }
      }
    });
  }
  