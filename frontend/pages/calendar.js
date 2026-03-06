// ─── GOOGLE CALENDAR PAGE ──────────────────────────────────────────────────────
import { calendar } from '../api.js';
import { showToast, showModal, closeModal } from '../app.js';

export async function renderCalendar() {
  return `
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-breadcrumb">Home / Google Calendar</div>
        <h1 class="page-title">Google Calendar</h1>
        <p class="page-subtitle">View upcoming events, create events, and generate Meet links.</p>
      </div>
      <div class="toolbar">
        <button class="btn btn-secondary" id="cal-refresh-btn">${refreshIcon()} Refresh</button>
        <button class="btn btn-secondary" id="create-event-btn">${eventIcon()} New Event</button>
        <button class="btn btn-primary" id="create-meet-btn">${meetIcon()} New Meet Link</button>
      </div>
    </div>
    <div class="page-body">
      <div class="card">
        <div class="card-header">
          <div class="card-title">${calIcon()} Upcoming Events</div>
          <span class="badge badge-blue" id="event-count">Loading…</span>
        </div>
        <div id="events-container">
          <div class="loader-center"><div class="spinner"></div></div>
        </div>
      </div>
    </div>
  `;
}

export function initCalendar() {
  loadEvents();
  document.getElementById('cal-refresh-btn')?.addEventListener('click', loadEvents);
  document.getElementById('create-event-btn')?.addEventListener('click', () => showEventModal(false));
  document.getElementById('create-meet-btn')?.addEventListener('click', () => showEventModal(true));
}

async function loadEvents() {
  const container = document.getElementById('events-container');
  const countEl = document.getElementById('event-count');
  if (!container) return;

  container.innerHTML = `<div class="loader-center"><div class="spinner"></div></div>`;

  try {
    const data = await calendar.listEvents(15);
    const events = data.items || [];
    countEl && (countEl.textContent = `${events.length} events`);

    if (events.length === 0) {
      container.innerHTML = `<div class="empty-state">${calIcon()}<h3>No upcoming events</h3><p>You have no upcoming events in your calendar.</p></div>`;
      return;
    }

    container.innerHTML = `<div class="events-list">
      ${events.map(ev => {
        const start = ev.start?.dateTime || ev.start?.date || '';
        const d = start ? new Date(start) : null;
        const month = d ? d.toLocaleString('default', { month: 'short' }) : '—';
        const day = d ? d.getDate() : '—';
        const timeStr = d ? d.toLocaleString('default', { weekday: 'short', hour: '2-digit', minute: '2-digit' }) : 'All day';
        const meetLink = ev.conferenceData?.entryPoints?.find(ep => ep.entryPointType === 'video')?.uri;

        return `
          <div class="event-item">
            <div class="event-date-box">
              <div class="event-month">${month}</div>
              <div class="event-day">${day}</div>
            </div>
            <div class="event-info">
              <div class="event-title">${esc(ev.summary || 'Untitled Event')}</div>
              <div class="event-time">${timeStr}</div>
              ${ev.description ? `<div style="font-size:0.8rem;color:var(--text-3);margin-top:4px;">${esc(ev.description)}</div>` : ''}
              ${meetLink ? `
                <div class="event-meet">
                  <a href="${esc(meetLink)}" target="_blank" rel="noopener">
                    ${meetIcon()} Join Google Meet
                  </a>
                </div>` : ''}
            </div>
            ${meetLink ? `<span class="badge badge-green">Meet</span>` : `<span class="badge badge-gray">Event</span>`}
          </div>
        `;
      }).join('')}
    </div>`;
  } catch (e) {
    container.innerHTML = `<div class="empty-state">${warningIcon()}<h3>Failed to load events</h3><p>${esc(e.message)}</p></div>`;
    showToast('Failed to load events: ' + e.message, 'error');
  }
}

function showEventModal(withMeet) {
  const title = withMeet ? 'Create Meet Link' : 'Create Event';
  const icon = withMeet ? meetIcon() : eventIcon();

  // Default start time: now + 1 hour, rounded to next hour
  const now = new Date();
  now.setHours(now.getHours() + 1, 0, 0, 0);
  const defaultStart = now.toISOString().slice(0, 16); // "YYYY-MM-DDTHH:MM"

  showModal(`
    <div class="modal-title">${icon} ${title}</div>

    <div class="form-group">
      <label for="ev-summary">Title *</label>
      <input type="text" id="ev-summary" placeholder="${withMeet ? 'Weekly Standup' : 'Team Lunch'}" autofocus />
    </div>
    <div class="form-group">
      <label for="ev-start">Start Time</label>
      <input type="datetime-local" id="ev-start" value="${defaultStart}" />
    </div>
    <div class="form-group">
      <label for="ev-duration">Duration (minutes)</label>
      <input type="number" id="ev-duration" value="60" min="15" max="480" step="15" />
    </div>
    <div class="form-group">
      <label for="ev-desc">Description <span style="color:var(--text-3)">(optional)</span></label>
      <textarea id="ev-desc" placeholder="Meeting agenda, notes…"></textarea>
    </div>

    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="window._closeModal()">Cancel</button>
      <button class="btn btn-primary" id="ev-submit">${icon} ${title}</button>
    </div>
  `);

  document.getElementById('ev-submit')?.addEventListener('click', async () => {
    const summary = document.getElementById('ev-summary')?.value?.trim();
    const startRaw = document.getElementById('ev-start')?.value;
    const duration = parseInt(document.getElementById('ev-duration')?.value || '60', 10);
    const description = document.getElementById('ev-desc')?.value?.trim() || null;

    if (!summary) { showToast('Title is required', 'warning'); return; }

    // Convert local datetime to ISO string
    let start_time = null;
    if (startRaw) {
      start_time = new Date(startRaw).toISOString();
    }

    const btn = document.getElementById('ev-submit');
    btn.disabled = true; btn.innerHTML = `<span class="spinner"></span> Creating…`;

    try {
      const payload = { summary, duration_minutes: duration, description };
      if (start_time) payload.start_time = start_time;

      let result;
      if (withMeet) {
        result = await calendar.createMeet(payload);
        const meetLink = result.meet_link;
        showToast('Meet created! ' + (meetLink || ''), 'success');
        if (meetLink) {
          showModal(`
            <div class="modal-title">${meetIcon()} Meet Link Created!</div>
            <div style="margin-bottom:16px;">
              <a href="${esc(meetLink)}" target="_blank" rel="noopener" class="btn btn-primary" style="width:100%;justify-content:center;">
                ${meetIcon()} Join Google Meet
              </a>
            </div>
            <div style="padding:12px;background:var(--bg-3);border-radius:var(--radius-sm);border:1px solid var(--border);font-size:0.8rem;color:var(--text-2);word-break:break-all;">${esc(meetLink)}</div>
            <div class="modal-footer"><button class="btn btn-secondary" onclick="window._closeModal()">Close</button></div>
          `);
        }
      } else {
        result = await calendar.createEvent(payload);
        showToast('Event "' + result.summary + '" created!', 'success');
        closeModal();
      }
      loadEvents();
    } catch (err) {
      showToast('Failed: ' + err.message, 'error');
      btn.disabled = false; btn.textContent = title;
    }
  });
}

// ─── HELPERS ───────────────────────────────────────────────────────────────────
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function calIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`; }
function eventIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`; }
function meetIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>`; }
function refreshIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>`; }
function warningIcon() { return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`; }
