// ─── GOOGLE PHOTOS PAGE ────────────────────────────────────────────────────────
import { photos } from '../api.js';
import { showToast, showModal, closeModal } from '../app.js';

let activeTab = 'photos';
let albumsList = [];

export async function renderPhotos() {
  return `
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-breadcrumb">Home / Google Photos</div>
        <h1 class="page-title">Google Photos</h1>
        <p class="page-subtitle">Browse, upload and organise your photo library.</p>
      </div>
      <div class="toolbar" id="photos-toolbar">
        <button class="btn btn-secondary" id="photos-refresh-btn">${refreshIcon()} Refresh</button>
        <button class="btn btn-secondary" id="create-album-btn">${albumIcon()} New Album</button>
        <button class="btn btn-primary" id="upload-photo-btn">${uploadIcon()} Upload Photo</button>
      </div>
    </div>
    <div class="page-body">
      <div class="tabs">
        <button class="tab-btn active" data-tab="photos" id="tab-photos">Photos</button>
        <button class="tab-btn" data-tab="albums" id="tab-albums">Albums</button>
      </div>

      <div id="photos-content">
        <div class="loader-center"><div class="spinner"></div></div>
      </div>
    </div>

    <input type="file" id="photo-file-input" accept="image/*,video/*" />
  `;
}

export function initPhotos() {
  activeTab = 'photos';
  loadTab(activeTab);

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeTab = btn.dataset.tab;
      loadTab(activeTab);
    });
  });

  document.getElementById('photos-refresh-btn')?.addEventListener('click', () => loadTab(activeTab));
  document.getElementById('create-album-btn')?.addEventListener('click', showCreateAlbumModal);
  document.getElementById('upload-photo-btn')?.addEventListener('click', () => {
    document.getElementById('photo-file-input').click();
  });
  document.getElementById('photo-file-input')?.addEventListener('change', handlePhotoUpload);
}

async function loadTab(tab) {
  if (tab === 'photos') await loadPhotos();
  else await loadAlbums();
}

async function loadPhotos() {
  const content = document.getElementById('photos-content');
  if (!content) return;
  content.innerHTML = `<div class="loader-center"><div class="spinner"></div></div>`;

  try {
    const data = await photos.listPhotos();
    const items = data.mediaItems || [];

    if (items.length === 0) {
      content.innerHTML = emptyState(photoIcon(), 'No photos found', 'Your Google Photos library appears to be empty.');
      return;
    }

    content.innerHTML = `
      <p style="font-size:0.8rem;color:var(--text-3);margin-bottom:16px;">${items.length} photo${items.length !== 1 ? 's' : ''} shown</p>
      <div class="photo-grid">
        ${items.map(item => `
          <div class="photo-item" title="${esc(item.filename || 'Photo')}">
            <img src="${esc(item.baseUrl + '=w320-h320-c')}" alt="${esc(item.filename || 'Photo')}" loading="lazy" onerror="this.parentElement.style.background='var(--bg-3)';this.remove()" />
            <div class="photo-overlay">
              <span class="photo-filename">${esc(item.filename || '')}</span>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (e) {
    content.innerHTML = emptyState(warningIcon(), 'Failed to load photos', e.message);
    showToast('Failed to load photos: ' + e.message, 'error');
  }
}

async function loadAlbums() {
  const content = document.getElementById('photos-content');
  if (!content) return;
  content.innerHTML = `<div class="loader-center"><div class="spinner"></div></div>`;

  try {
    const data = await photos.listAlbums();
    albumsList = data.albums || [];

    if (albumsList.length === 0) {
      content.innerHTML = emptyState(albumIcon(), 'No albums found', 'Create an album to organise your photos.');
      return;
    }

    content.innerHTML = `
      <p style="font-size:0.8rem;color:var(--text-3);margin-bottom:16px;">${albumsList.length} album${albumsList.length !== 1 ? 's' : ''}</p>
      <div class="album-grid">
        ${albumsList.map(album => `
          <div class="album-card" data-album-id="${esc(album.id)}">
            <div class="album-cover">${albumIcon(32)}</div>
            <div>
              <div class="album-name">${esc(album.title || 'Untitled')}</div>
              <div class="album-count">${album.mediaItemsCount || 0} items</div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (e) {
    content.innerHTML = emptyState(warningIcon(), 'Failed to load albums', e.message);
    showToast('Failed to load albums: ' + e.message, 'error');
  }
}

function showCreateAlbumModal() {
  showModal(`
    <div class="modal-title">${albumIcon()} Create Album</div>
    <div class="form-group">
      <label for="album-title-input">Album Title</label>
      <input type="text" id="album-title-input" placeholder="Summer 2026" autofocus />
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="window._closeModal()">Cancel</button>
      <button class="btn btn-primary" id="create-album-submit">Create Album</button>
    </div>
  `);

  document.getElementById('create-album-submit')?.addEventListener('click', async () => {
    const title = document.getElementById('album-title-input')?.value?.trim();
    if (!title) { showToast('Album title is required', 'warning'); return; }

    const btn = document.getElementById('create-album-submit');
    btn.disabled = true; btn.textContent = 'Creating…';
    try {
      const result = await photos.createAlbum(title);
      showToast(`Album "${result.title || title}" created!`, 'success');
      closeModal();
      activeTab = 'albums';
      document.getElementById('tab-albums')?.click();
    } catch (err) {
      showToast('Failed: ' + err.message, 'error');
      btn.disabled = false; btn.textContent = 'Create Album';
    }
  });
}

async function handlePhotoUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  e.target.value = '';

  // Fetch albums for picker
  let albumOptions = '<option value="">No album (library only)</option>';
  try {
    if (albumsList.length === 0) {
      const data = await photos.listAlbums();
      albumsList = data.albums || [];
    }
    albumOptions += albumsList.map(a => `<option value="${esc(a.id)}">${esc(a.title)}</option>`).join('');
  } catch (_) {}

  showModal(`
    <div class="modal-title">${uploadIcon()} Upload Photo</div>
    <div class="form-group">
      <label>File</label>
      <div style="padding:12px;background:var(--bg-3);border-radius:var(--radius-sm);border:1px solid var(--border);font-size:0.85rem;color:var(--text-2);">
        📷 ${esc(file.name)} (${(file.size / 1024).toFixed(1)} KB)
      </div>
    </div>
    <div class="form-group">
      <label for="upload-album-select">Add to Album <span style="color:var(--text-3)">(optional)</span></label>
      <select id="upload-album-select">${albumOptions}</select>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="window._closeModal()">Cancel</button>
      <button class="btn btn-primary" id="upload-photo-submit">Upload</button>
    </div>
  `);

  document.getElementById('upload-photo-submit')?.addEventListener('click', async () => {
    const albumId = document.getElementById('upload-album-select')?.value || null;
    const btn = document.getElementById('upload-photo-submit');
    btn.disabled = true; btn.innerHTML = `<span class="spinner"></span> Uploading…`;

    try {
      await photos.uploadPhoto(file, albumId);
      showToast(`"${file.name}" uploaded successfully!`, 'success');
      closeModal();
      loadPhotos();
    } catch (err) {
      showToast('Upload failed: ' + err.message, 'error');
      btn.disabled = false; btn.textContent = 'Upload';
    }
  });
}

// ─── HELPERS ───────────────────────────────────────────────────────────────────
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function emptyState(icon, title, desc) { return `<div class="empty-state">${icon}<h3>${title}</h3><p>${desc}</p></div>`; }
function photoIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`; }
function albumIcon(s=18) { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="${s}" height="${s}"><rect x="2" y="7" width="20" height="15" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>`; }
function uploadIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/></svg>`; }
function refreshIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>`; }
function warningIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`; }
