function attachUploader(btnSelector, inputSelector) {
    const btn = document.querySelector(btnSelector);
    const input = document.querySelector(inputSelector);
    if (!btn || !input) return;
  
    const file = document.createElement('input');
    file.type = 'file';
    file.accept = 'image/*';
    file.style.display = 'none';
    document.body.appendChild(file);
  
    btn.addEventListener('click', () => file.click());
    file.addEventListener('change', async () => {
      if (!file.files || !file.files[0]) return;
      const fd = new FormData();
      fd.append('file', file.files[0]);
      const res = await fetch('/api/upload', { method: 'POST', body: fd });
      const data = await res.json();
      if (res.ok && data?.url) {
        input.value = data.url;
        btn.textContent = 'Uploaded ✓';
        setTimeout(() => (btn.textContent = 'Upload Image'), 1200);
      } else {
        alert('Upload failed.');
      }
      file.value = '';
    });
  }
  