// ─── API CLIENT ────────────────────────────────────────────────────────────────
// Central fetch wrapper that injects the JWT Authorization header.

const BASE = "";  // Same origin — FastAPI serves both API and frontend

function getToken() {
  return localStorage.getItem("jwt_token");
}

async function request(method, path, body = null, isFormData = false) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (body && !isFormData) headers["Content-Type"] = "application/json";

  const opts = { method, headers };
  if (body) opts.body = isFormData ? body : JSON.stringify(body);

  const res = await fetch(BASE + path, opts);

  if (res.status === 401) {
    localStorage.removeItem("jwt_token");
    window.location.href = "/";
    throw new Error("Unauthorized");
  }

  const ct = res.headers.get("content-type") || "";
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      detail = err.detail || err.error || detail;
    } catch (_) {}
    throw new Error(detail);
  }

  if (ct.includes("application/json")) return res.json();
  return res.text();
}

// ─── AUTH ──────────────────────────────────────────────────────────────────────
export const auth = {
  async getLoginUrl() {
    const data = await request("GET", "/auth/login/google");
    return data.url;
  },
  async logout() {
    return request("DELETE", "/auth/logout");
  }
};

// ─── DRIVE ─────────────────────────────────────────────────────────────────────
export const drive = {
  async listFiles() {
    return request("GET", "/google_drive/drive/files");
  },
  async upload(file) {
    const fd = new FormData();
    fd.append("file", file);
    return request("POST", "/google_drive/upload", fd, true);
  },
  async createFolder(name, parentId = null) {
    const qs = parentId ? `?folder_name=${encodeURIComponent(name)}&parent_id=${parentId}` : `?folder_name=${encodeURIComponent(name)}`;
    return request("POST", `/google_drive/create_folder${qs}`);
  }
};

// ─── PHOTOS ────────────────────────────────────────────────────────────────────
export const photos = {
  async listPhotos() {
    return request("GET", "/google_photos/photos");
  },
  async listAlbums() {
    return request("GET", "/google_photos/albums");
  },
  async createAlbum(title) {
    return request("POST", "/google_photos/albums", { album_title: title });
  },
  async uploadPhoto(file, albumId = null) {
    const fd = new FormData();
    fd.append("file", file);
    const qs = albumId ? `?album_id=${albumId}` : "";
    return request("POST", `/google_photos/upload${qs}`, fd, true);
  }
};

// ─── CALENDAR ──────────────────────────────────────────────────────────────────
export const calendar = {
  async listEvents(maxResults = 10) {
    return request("GET", `/google_calendar/events?max_results=${maxResults}`);
  },
  async createEvent(data) {
    return request("POST", "/google_calendar/event", data);
  },
  async createMeet(data) {
    return request("POST", "/google_calendar/create", data);
  }
};
