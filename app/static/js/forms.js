// Enhanced AJAX form helper with loading states and better feedback
function setupAjaxForm({ formId, endpoint, successText, errorText }) {
    const form = document.getElementById(formId);
    if (!form) return;
    const msgEl = document.getElementById(formId.replace('Form','Msg')) || form.querySelector('.form-msg');
    const submitBtn = form.querySelector('button[type="submit"], button:not([type])');
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      // Show loading state
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Submitting...';
        submitBtn.style.opacity = '0.7';
      }
      
      if (msgEl) {
        msgEl.textContent = 'Sending your request...';
        msgEl.style.color = '#C8A349';
        msgEl.style.display = 'block';
      }
      
      const fd = new FormData(form);
      try {
        const res = await fetch(endpoint, { method: 'POST', body: fd });
        const data = await res.json().catch(() => ({}));
        if (res.ok && data?.success) {
          if (msgEl) { 
            msgEl.textContent = successText; 
            msgEl.style.color = '#C8A349';
            msgEl.style.fontWeight = '500';
          }
          form.reset();
          
          // Keep success message visible longer
          setTimeout(() => {
            if (msgEl) msgEl.style.display = 'none';
          }, 5000);
          
        } else {
          if (msgEl) { 
            msgEl.textContent = errorText; 
            msgEl.style.color = '#ff6b6b';
            msgEl.style.fontWeight = '500';
          }
        }
      } catch (err) {
        if (msgEl) { 
          msgEl.textContent = errorText; 
          msgEl.style.color = '#ff6b6b';
          msgEl.style.fontWeight = '500';
        }
      } finally {
        // Reset button state
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = submitBtn.dataset.originalText || 'Submit Request';
          submitBtn.style.opacity = '1';
        }
      }
    });
    
    // Store original button text
    if (submitBtn && !submitBtn.dataset.originalText) {
      submitBtn.dataset.originalText = submitBtn.textContent;
    }
  }
  