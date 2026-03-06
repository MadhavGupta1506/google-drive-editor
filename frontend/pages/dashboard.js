// ─── DASHBOARD PAGE ────────────────────────────────────────────────────────────
import { drive, photos, calendar } from '../api.js';
import { navigate } from '../app.js';

export async function renderDashboard() {
  return `
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-breadcrumb">Home</div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Welcome back! Here's an overview of your Google services.</p>
      </div>
    </div>
    <div class="page-body">
      <div class="stats-grid" id="stats-grid">
        ${statCard('blue', driveIcon(), '—', 'Drive Files', 'Loading…')}
        ${statCard('green', photoIcon(), '—', 'Photos', 'Loading…')}
        ${statCard('yellow', albumIcon(), '—', 'Albums', 'Loading…')}
        ${statCard('purple', calendarIcon(), '—', 'Upcoming Events', 'Loading…')}
      </div>

      <h2 style="font-size:1rem;font-weight:600;margin-bottom:16px;color:var(--text-2);text-transform:uppercase;letter-spacing:0.06em;font-size:0.75rem;">Quick Actions</h2>
      <div class="quick-actions">
        <div class="quick-action-card" data-nav="drive" id="qa-drive">
          <div class="quick-action-icon" style="background:var(--grad-blue)">${driveIcon()}</div>
          <div>
            <div class="quick-action-label">Google Drive</div>
            <div class="quick-action-desc">Manage files &amp; folders</div>
          </div>
        </div>
        <div class="quick-action-card" data-nav="photos" id="qa-photos">
          <div class="quick-action-icon" style="background:var(--grad-green)">${photoIcon()}</div>
          <div>
            <div class="quick-action-label">Google Photos</div>
            <div class="quick-action-desc">Browse &amp; upload photos</div>
          </div>
        </div>
        <div class="quick-action-card" data-nav="calendar" id="qa-calendar">
          <div class="quick-action-icon" style="background:var(--grad-yellow)">${calendarIcon()}</div>
          <div>
            <div class="quick-action-label">Google Calendar</div>
            <div class="quick-action-desc">Events &amp; Meet links</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export async function initDashboard() {
  // Attach quick actions
  document.querySelectorAll('.quick-action-card[data-nav]').forEach(el => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });

  // Load stats
  loadStats();
}

async function loadStats() {
  const grid = document.getElementById('stats-grid');
  if (!grid) return;

  const [driveResult, photosResult, albumsResult, eventsResult] = await Promise.allSettled([
    drive.listFiles(),
    photos.listPhotos(),
    photos.listAlbums(),
    calendar.listEvents(10),
  ]);

  const driveCount = driveResult.status === 'fulfilled' ? (driveResult.value?.files?.length ?? '!') : '!';
  const photosCount = photosResult.status === 'fulfilled' ? (photosResult.value?.mediaItems?.length ?? '0') : '!';
  const albumsCount = albumsResult.status === 'fulfilled' ? (albumsResult.value?.albums?.length ?? '0') : '!';
  const eventsCount = eventsResult.status === 'fulfilled' ? (eventsResult.value?.items?.length ?? '0') : '!';

  grid.innerHTML = `
    ${statCard('blue', driveIcon(), driveCount, 'Drive Files', 'Files in your Drive')}
    ${statCard('green', photoIcon(), photosCount, 'Photos', 'In your library')}
    ${statCard('yellow', albumIcon(), albumsCount, 'Albums', 'Photo albums')}
    ${statCard('purple', calendarIcon(), eventsCount, 'Upcoming Events', 'Next 10 events')}
  `;
}

function statCard(color, icon, value, label, sub) {
  return `
    <div class="stat-card ${color}">
      <div class="stat-icon">${icon}</div>
      <div class="stat-value">${value}</div>
      <div class="stat-label">${label}</div>
    </div>
  `;
}

function driveIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/></svg>`;
}
function photoIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`;
}
function albumIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/></svg>`;
}
function calendarIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`;
}
