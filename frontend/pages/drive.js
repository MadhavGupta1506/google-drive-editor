// ─── GOOGLE DRIVE PAGE ─────────────────────────────────────────────────────────
import { drive } from '../api.js';
import { showToast, showModal, closeModal } from '../app.js';

export async function renderDrive() {
  return `
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-breadcrumb">Home / Google Drive</div>
        <h1 class="page-title">Google Drive</h1>
        <p class="page-subtitle">Manage your files and folders.</p>
      </div>
      <div class="toolbar">
        <button class="btn btn-secondary" id="drive-refresh-btn">
          ${refreshIcon()} Refresh
        </button>
        <button class="btn btn-secondary" id="drive-folder-btn">
          ${folderIcon()} New Folder
        </button>
        <button class="btn btn-primary" id="drive-upload-btn">
          ${uploadIcon()} Upload File
        </button>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="card-header">
          <div class="card-title">${driveIcon()} Files</div>
          <span class="badge badge-blue" id="drive-count">Loading…</span>
        </div>
        <div id="drive-table-wrap" class="table-wrap">
          <div class="loader-center"><div class="spinner"></div></div>
        </div>
      </div>
    </div>

    <!-- Hidden file input -->
    <input type="file" id="drive-file-input" />
  `;
}

export function initDrive() {
  loadFiles();

  document.getElementById('drive-refresh-btn')?.addEventListener('click', loadFiles);
  document.getElementById('drive-upload-btn')?.addEventListener('click', () => {
    document.getElementById('drive-file-input').click();
  });
  document.getElementById('drive-file-input')?.addEventListener('change', handleUpload);
  document.getElementById('drive-folder-btn')?.addEventListener('click', showCreateFolderModal);
}

async function loadFiles() {
  const wrap = document.getElementById('drive-table-wrap');
  const countEl = document.getElementById('drive-count');
  if (!wrap) return;

  wrap.innerHTML = `<div class="loader-center"><div class="spinner"></div></div>`;
  try {
    const data = await drive.listFiles();
    const files = data.files || [];
    countEl && (countEl.textContent = `${files.length} files`);

    if (files.length === 0) {
      wrap.innerHTML = emptyState(driveIcon(), 'No files found', 'Your Google Drive is empty or no files were returned.');
      return;
    }

    wrap.innerHTML = `
      <table>
        <thead><tr>
          <th>Name</th>
          <th>Type</th>
          <th>ID</th>
        </tr></thead>
        <tbody>
          ${files.map(f => `
            <tr>
              <td><div class="file-name-cell">${mimeIcon(f.mimeType)}<span>${esc(f.name)}</span></div></td>
              <td><span class="badge ${f.mimeType.includes('folder') ? 'badge-yellow' : 'badge-blue'}">${shortMime(f.mimeType)}</span></td>
              <td><span class="file-id">${esc(f.id)}</span></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  } catch (e) {
    wrap.innerHTML = emptyState(warningIcon(), 'Failed to load files', e.message);
    showToast('Failed to load Drive files: ' + e.message, 'error');
  }
}

async function handleUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  e.target.value = '';

  showToast(`Uploading "${file.name}"…`, 'info');
  try {
    const result = await drive.upload(file);
    showToast(`Uploaded "${result.name}" successfully!`, 'success');
    loadFiles();
  } catch (err) {
    showToast('Upload failed: ' + err.message, 'error');
  }
}

function showCreateFolderModal() {
  showModal(`
    <div class="modal-title">${folderIcon()} Create Folder</div>
    <div class="form-group">
      <label for="folder-name-input">Folder Name</label>
      <input type="text" id="folder-name-input" placeholder="My New Folder" autofocus />
    </div>
    <div class="form-group">
      <label for="folder-parent-input">Parent Folder ID <span style="color:var(--text-3)">(optional)</span></label>
      <input type="text" id="folder-parent-input" placeholder="Leave empty for root" />
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="window._closeModal()">Cancel</button>
      <button class="btn btn-primary" id="create-folder-submit">Create Folder</button>
    </div>
  `);

  document.getElementById('create-folder-submit')?.addEventListener('click', async () => {
    const name = document.getElementById('folder-name-input')?.value?.trim();
    const parent = document.getElementById('folder-parent-input')?.value?.trim() || null;
    if (!name) { showToast('Folder name is required', 'warning'); return; }

    const btn = document.getElementById('create-folder-submit');
    btn.disabled = true; btn.textContent = 'Creating…';
    try {
      const result = await drive.createFolder(name, parent);
      showToast(`Folder "${result.name}" created!`, 'success');
      closeModal();
      loadFiles();
    } catch (err) {
      showToast('Failed: ' + err.message, 'error');
      btn.disabled = false; btn.textContent = 'Create Folder';
    }
  });
}

// ─── HELPERS ───────────────────────────────────────────────────────────────────
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function shortMime(m) {
  if (m.includes('folder')) return 'Folder';
  if (m.includes('document')) return 'Doc';
  if (m.includes('spreadsheet')) return 'Sheet';
  if (m.includes('presentation')) return 'Slides';
  if (m.includes('pdf')) return 'PDF';
  if (m.includes('image')) return 'Image';
  if (m.includes('video')) return 'Video';
  if (m.includes('audio')) return 'Audio';
  const parts = m.split('/');
  return parts[parts.length - 1].toUpperCase().slice(0, 8);
}

function mimeIcon(m) {
  let color = '#4285f4';
  if (m.includes('folder')) color = '#fbbc04';
  if (m.includes('document')) color = '#4285f4';
  if (m.includes('spreadsheet')) color = '#34a853';
  if (m.includes('presentation')) color = '#ea4335';
  if (m.includes('image')) color = '#9c27b0';
  return `<svg class="file-icon" viewBox="0 0 24 24" fill="${color}" opacity="0.8"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/><polyline points="14 2 14 8 20 8" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/></svg>`;
}

function emptyState(icon, title, desc) {
  return `<div class="empty-state">${icon}<h3>${title}</h3><p>${desc}</p></div>`;
}
function driveIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/></svg>`; }
function folderIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>`; }
function uploadIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/></svg>`; }
function refreshIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>`; }
function warningIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`; }
