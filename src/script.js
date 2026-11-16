'use strict';
const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
if (menuButton && nav) {
  document.documentElement.classList.add('js');
  menuButton.hidden = false;
  const setMenu = open => {
    menuButton.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  };
  menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      setMenu(false); menuButton.focus();
    }
  });
  matchMedia('(min-width: 761px)').addEventListener('change', () => setMenu(false));
}
const dialog = document.querySelector('#photo-dialog');
if (dialog && typeof dialog.showModal === 'function') {
  let opener;
  document.querySelectorAll('[data-photo]').forEach(link => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); opener = link;
    const image = dialog.querySelector('img');
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    dialog.querySelector('#photo-caption').textContent = link.dataset.caption || image.alt;
    dialog.showModal(); document.body.classList.add('modal-open');
    dialog.querySelector('button').focus();
  }));
  dialog.querySelector('#close-photo').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const r = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => { document.body.classList.remove('modal-open'); opener?.focus(); });
}
