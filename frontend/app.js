// ─── MAIN SPA ROUTER & ORCHESTRATOR ───────────────────────────────────────────
import { renderLogin, initLogin } from './pages/login.js';
import { renderDashboard, initDashboard } from './pages/dashboard.js';
import { renderDrive, initDrive } from './pages/drive.js';
import { renderPhotos, initPhotos } from './pages/photos.js';
import { renderCalendar, initCalendar } from './pages/calendar.js';
import { auth } from './api.js';

// ─── STATE ─────────────────────────────────────────────────────────────────────
let currentPage = null;

// ─── BOOT ──────────────────────────────────────────────────────────────────────
async function boot() {
  // Check if the URL contains a token from the OAuth callback redirect
  const params = new URLSearchParams(window.location.search);
  const tokenFromUrl = params.get('token');
  if (tokenFromUrl) {
    localStorage.setItem('jwt_token', tokenFromUrl);
    // Clean the URL
    history.replaceState({}, '', '/');
  }

  // Hide splash after a short delay
  setTimeout(() => {
    const splash = document.getElementById('splash');
    if (splash) { splash.classList.add('hidden'); setTimeout(() => splash.remove(), 400); }
  }, 600);

  const token = localStorage.getItem('jwt_token');
  if (!token) {
    await renderPage('login');
  } else {
    await renderPage('dashboard');
  }
}

// ─── ROUTER ────────────────────────────────────────────────────────────────────
export async function navigate(page) {
  await renderPage(page);
}

async function renderPage(page) {
  currentPage = page;

  const app = document.getElementById('app');
  const token = localStorage.getItem('jwt_token');

  // Auth guard
  if (page !== 'login' && !token) {
    await renderPage('login');
    return;
  }

  if (page === 'login') {
    app.innerHTML = await renderLogin();
    initLogin();
    return;
  }

  // Render the shell with sidebar + content area
  const sidebarHtml = buildSidebar(token, page);

  let pageContent = '';
  switch (page) {
    case 'dashboard': pageContent = await renderDashboard(); break;
    case 'drive':     pageContent = await renderDrive();     break;
    case 'photos':    pageContent = await renderPhotos();    break;
    case 'calendar':  pageContent = await renderCalendar();  break;
    default: pageContent = await renderDashboard(); break;
  }

  app.innerHTML = `
    <div class="app-shell">
      ${sidebarHtml}
      <main class="main-content" id="main-content">
        ${pageContent}
      </main>
    </div>
    <div id="toast-container"></div>
  `;

  // Set active nav
  document.querySelectorAll('.nav-item').forEach(el => {
    if (el.dataset.page === page) el.classList.add('active');
  });

  // Wire nav clicks
  document.querySelectorAll('.nav-item[data-page]').forEach(el => {
    el.addEventListener('click', () => navigate(el.dataset.page));
  });

  // Init page
  switch (page) {
    case 'dashboard': await initDashboard(); break;
    case 'drive':     initDrive();           break;
    case 'photos':    initPhotos();          break;
    case 'calendar':  initCalendar();        break;
  }

  // Logout
  document.getElementById('sidebar-logout')?.addEventListener('click', handleLogout);
}

// ─── SIDEBAR ───────────────────────────────────────────────────────────────────
function buildSidebar(token, activePage) {
  // Decode email from JWT (base64 payload)
  let email = 'user@google.com';
  let avatarChar = 'U';
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    email = payload.email || email;
    avatarChar = email[0].toUpperCase();
  } catch (_) {}

  const navItem = (page, icon, label) => `
    <button class="nav-item" data-page="${page}">
      <span class="nav-icon">${icon}</span>
      ${label}
    </button>
  `;

  return `
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo-icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="48" height="48" rx="12" fill="url(#sg)"/>
            <defs><linearGradient id="sg" x1="0" y1="0" x2="48" y2="48">
              <stop offset="0%" stop-color="#4285f4"/>
              <stop offset="100%" stop-color="#34a853"/>
            </linearGradient></defs>
            <path d="M24 14L32 28H16L24 14Z" fill="white" opacity="0.9"/>
            <circle cx="24" cy="34" r="4" fill="white" opacity="0.7"/>
          </svg>
        </div>
        <div>
          <div class="sidebar-title">Suite Manager</div>
          <div class="sidebar-subtitle">Google Services</div>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label">Navigation</div>
        ${navItem('dashboard', dashIcon(), 'Dashboard')}
        ${navItem('drive', driveNavIcon(), 'Google Drive')}
        ${navItem('photos', photoNavIcon(), 'Google Photos')}
        ${navItem('calendar', calNavIcon(), 'Google Calendar')}
      </nav>

      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="user-avatar">${avatarChar}</div>
          <div class="user-info">
            <div class="user-email">${email}</div>
            <div class="user-role">Google Account</div>
          </div>
          <button class="logout-btn" id="sidebar-logout" title="Logout">
            ${logoutIcon()}
          </button>
        </div>
      </div>
    </aside>
  `;
}

// ─── LOGOUT ────────────────────────────────────────────────────────────────────
async function handleLogout() {
  try {
    await auth.logout();
  } catch (_) {}
  localStorage.removeItem('jwt_token');
  showToast('Logged out successfully', 'info');
  setTimeout(() => renderPage('login'), 800);
}

// ─── MODAL SYSTEM ──────────────────────────────────────────────────────────────
export function showModal(html) {
  closeModal();
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.id = 'modal-overlay';
  overlay.innerHTML = `<div class="modal" id="modal-box">${html}</div>`;
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal();
  });
  document.body.appendChild(overlay);
  // Expose to inline onclick
  window._closeModal = closeModal;
}

export function closeModal() {
  document.getElementById('modal-overlay')?.remove();
}

// ─── TOAST SYSTEM ──────────────────────────────────────────────────────────────
export function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = {
    success: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22,4 12,14.01 9,11.01"/></svg>`,
    error:   `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
    info:    `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
    warning: `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  };

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `${icons[type] || icons.info}<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100%)'; toast.style.transition = 'all 0.3s ease'; setTimeout(() => toast.remove(), 300); }, 4000);
}

// ─── SVG ICONS ─────────────────────────────────────────────────────────────────
function dashIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>`; }
function driveNavIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/></svg>`; }
function photoNavIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`; }
function calNavIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`; }
function logoutIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`; }

// ─── INIT ──────────────────────────────────────────────────────────────────────
boot();
