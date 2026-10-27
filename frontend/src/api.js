const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://localhost:8000" : "");

if (!API_URL) {
  throw new Error("Configure VITE_API_URL com a URL pública da API.");
}

const API = API_URL.replace(/\/$/, "");

export const WS_URL = API.replace(/^http/, "ws") + "/ws";

const KEY_TOKEN = "lucia_token";
const KEY_USER = "lucia_user";

export const session = {
  token: () => localStorage.getItem(KEY_TOKEN),
  user: () => {
    try { return JSON.parse(localStorage.getItem(KEY_USER) || "null"); } catch { return null; }
  },
  save(token, user) {
    localStorage.setItem(KEY_TOKEN, token);
    localStorage.setItem(KEY_USER, JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem(KEY_TOKEN);
    localStorage.removeItem(KEY_USER);
  },
};

let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn; };

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

function errorMessage(body, fallback) {
  const d = body?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((e) => e.msg).join("; ");
  return fallback;
}

async function request(path, { method = "GET", body, signal } = {}) {
  const token = session.token();
  let res;
  try {
    res = await fetch(API + path, {
      method,
      signal,
      headers: {
        ...(body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    if (e.name === "AbortError") throw e;
    throw new ApiError("Não foi possível conectar à API.", 0);
  }
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    // Token expirado/inválido: volta para o login em vez de ficar com a tela quebrada.
    if (res.status === 401 && path !== "/auth/login") onUnauthorized();
    throw new ApiError(errorMessage(data, `Erro ${res.status}`), res.status);
  }
  return res;
}

export const api = {
  get: async (path, opts) => (await request(path, opts)).json(),
  post: async (path, body) => (await request(path, { method: "POST", body })).json(),
  patch: async (path, body) => (await request(path, { method: "PATCH", body })).json(),
  del: async (path) => (await request(path, { method: "DELETE" })).json(),
  // Lista paginada: o total vem no header X-Total-Count.
  async list(path, opts) {
    const res = await request(path, opts);
    return { items: await res.json(), total: Number(res.headers.get("X-Total-Count") || 0) };
  },
  login: async (email, password) =>
    (await request("/auth/login", { method: "POST", body: { email, password } })).json(),
};
