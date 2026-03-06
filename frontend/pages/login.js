// ─── LOGIN PAGE ────────────────────────────────────────────────────────────────
import { auth } from '../api.js';
import { showToast } from '../app.js';

export async function renderLogin() {
  return `
    <div class="login-page">
      <div class="login-bg-orb orb1"></div>
      <div class="login-bg-orb orb2"></div>
      <div class="login-bg-orb orb3"></div>

      <div class="login-card">
        <div class="login-logo">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="64" height="64" rx="16" fill="url(#lg1)"/>
            <defs>
              <linearGradient id="lg1" x1="0" y1="0" x2="64" y2="64">
                <stop offset="0%" stop-color="#4285f4"/>
                <stop offset="100%" stop-color="#34a853"/>
              </linearGradient>
            </defs>
            <path d="M32 16L44 38H20L32 16Z" fill="white" opacity="0.9"/>
            <circle cx="32" cy="46" r="6" fill="white" opacity="0.7"/>
          </svg>
        </div>

        <h1 class="login-title">Google Suite Manager</h1>
        <p class="login-subtitle">Manage your Drive, Photos &amp; Calendar — all in one beautiful dashboard.</p>

        <button class="google-btn" id="google-login-btn">
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Continue with Google
        </button>

        <div class="login-features">
          <div class="login-feature">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
            Secure Google OAuth 2.0 Authentication
          </div>
          <div class="login-feature">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
            Manage Google Drive Files &amp; Folders
          </div>
          <div class="login-feature">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
            Browse &amp; Upload Google Photos
          </div>
          <div class="login-feature">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
            Create Calendar Events &amp; Meet Links
          </div>
        </div>

        <p class="login-footer">By signing in you agree to Google's Terms of Service and Privacy Policy.</p>
      </div>
    </div>
  `;
}

export function initLogin() {
  const btn = document.getElementById('google-login-btn');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Redirecting…`;
    try {
      const url = await auth.getLoginUrl();
      window.location.href = url;
    } catch (e) {
      showToast('Failed to get login URL: ' + e.message, 'error');
      btn.disabled = false;
      btn.innerHTML = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
      </svg> Continue with Google`;
    }
  });
}
