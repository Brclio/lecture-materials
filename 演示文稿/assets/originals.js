(() => {
  const dialog = document.getElementById('original-view');
  const viewport = dialog.querySelector('.original-viewport');
  const photo = dialog.querySelector('img');
  const title = dialog.querySelector('h2');
  const zoom = dialog.querySelector('[data-zoom]');
  const close = dialog.querySelector('[data-close]');
  let expanded = false;

  function setZoom(value) {
    expanded = value;
    viewport.classList.toggle('zoomed', value);
    zoom.setAttribute('aria-pressed', String(value));
    zoom.textContent = value ? '适合屏幕' : '放大细看';
    viewport.scrollTo(0, 0);
  }

  document.querySelectorAll('button[data-original]').forEach(trigger => {
    trigger.addEventListener('click', () => {
      const source = trigger.dataset.original || trigger.querySelector('img').getAttribute('src');
      title.textContent = trigger.dataset.caption || trigger.querySelector('img').alt;
      photo.alt = title.textContent;
      photo.src = source;
      setZoom(false);
      dialog.showModal();
      close.focus();
    });
  });

  zoom.addEventListener('click', () => setZoom(!expanded));
  photo.addEventListener('click', () => setZoom(!expanded));
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => photo.removeAttribute('src'));
  document.addEventListener('keydown', event => {
    if (!dialog.open) return;
    event.stopImmediatePropagation();
    if (event.key === 'Escape') {
      event.preventDefault();
      dialog.close();
    }
  }, true);
  // A presenter on the second monitor can advance while a source image is open.
  const observer = new MutationObserver(() => {
    if (dialog.open) dialog.close();
  });
  document.querySelectorAll('#stage .slide').forEach(slide =>
    observer.observe(slide, { attributes: true, attributeFilter: ['class'] }));
})();
