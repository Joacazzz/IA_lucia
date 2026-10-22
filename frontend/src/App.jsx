import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api, session, setUnauthorizedHandler } from "./api";
import LoginPage from "./components/LoginPage";
import { useToast } from "./components/Toasts";
import { useRealtime } from "./hooks/useRealtime";
import Atendentes from "./pages/Atendentes";
import Departamentos from "./pages/Departamentos";
import Notificacoes from "./pages/Notificacoes";
import Protocolos from "./pages/Protocolos";

// O Chart.js só é baixado quando o dashboard é aberto.
const Dashboard = lazy(() => import("./pages/Dashboard"));

const TITLES = {
  dashboard: "Visão geral",
  protocolos: "Protocolos",
  atendentes: "Atendentes",
  departamentos: "Departamentos",
  notificacoes: "Notificações",
};

export default function App() {
  const toast = useToast();
  const [token, setToken] = useState(session.token());
  const [user, setUser] = useState(session.user());
  const [page, setPage] = useState("dashboard");
  const [deptos, setDeptos] = useState([]);
  const [abertos, setAbertos] = useState(0);
  const [notifs, setNotifs] = useState([]);
  const [unread, setUnread] = useState(0);
  const [online, setOnline] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const logout = useCallback(() => {
    session.clear();
    setToken(null);
    setUser(null);
    setPage("dashboard");
  }, []);

  useEffect(() => { setUnauthorizedHandler(logout); }, [logout]);

  const login = (tok, usr) => {
    session.save(tok, usr);
    setToken(tok);
    setUser(usr);
  };

  // Departamentos mudam raramente: uma busca por sessão.
  useEffect(() => {
    if (!token) return;
    api.get("/departamentos").then(setDeptos).catch((e) => toast(e.message, "error"));
  }, [token, toast]);

  const deptosByKey = useMemo(() => Object.fromEntries(deptos.map((d) => [d.chave, d])), [deptos]);

  // Contador do menu: 1 linha de resposta, o total vem no header.
  useEffect(() => {
    if (!token) return;
    api.list("/protocolos?status=Aberto&limit=1").then((r) => setAbertos(r.total)).catch(() => {});
  }, [token, refreshKey]);

  // Eventos em tempo real: agrupa rajadas num único refresh (500 ms).
  const timer = useRef();
  const onEvent = useCallback((ev) => {
    setNotifs((n) => [{ ...ev, id: crypto.randomUUID() }, ...n].slice(0, 100));
    setUnread((u) => u + 1);
    toast(ev.mensagem, "info");
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setRefreshKey((k) => k + 1), 500);
  }, [toast]);
  useEffect(() => () => clearTimeout(timer.current), []);

  useRealtime(token, onEvent, setOnline);

  if (!token) return <LoginPage onLogin={login} />;

  const go = (p) => { setPage(p); if (p === "notificacoes") setUnread(0); };
  const bump = () => setRefreshKey((k) => k + 1);

  const nav = [
    { id: "dashboard", icon: "◈", label: "Dashboard" },
    { id: "protocolos", icon: "📋", label: "Protocolos", badge: abertos || null },
    { id: "atendentes", icon: "👤", label: "Atendentes" },
    { id: "departamentos", icon: "🏢", label: "Departamentos" },
    { id: "notificacoes", icon: "🔔", label: "Notificações", notif: unread || null },
  ];

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-title"><span className="dot" />Lucía</div>
          <div className="logo-sub">Painel Administrativo</div>
        </div>
        <nav className="nav">
          <div className="nav-lbl">Menu</div>
          {nav.map((p) => (
            <div key={p.id} className={`nav-item ${page === p.id ? "active" : ""}`} onClick={() => go(p.id)}>
              <span className="nav-icon">{p.icon}</span>
              {p.label}
              {p.badge ? <span className="nav-badge">{p.badge}</span> : null}
              {p.notif ? <span className="notif-badge">{p.notif}</span> : null}
            </div>
          ))}
        </nav>
        <div className="sidebar-foot">
          {user && (
            <div className="user-row">
              <div className="avatar">{user.nome.charAt(0).toUpperCase()}</div>
              <div>
                <div className="user-name">{user.nome.split(" ")[0]}</div>
                <div className="user-role">{user.papel === "admin" ? "Administrador" : "Atendente"}</div>
              </div>
            </div>
          )}
          <button className="logout-btn" onClick={logout}>Sair da conta</button>
          <div style={{ marginTop: 8 }}>
            <span className={`conn-dot ${online ? "on" : ""}`} />
            {online ? "Tempo real conectado" : "Reconectando…"}
          </div>
        </div>
      </aside>

      <div className="main">
        <div className="topbar">
          <div>
            <div className="topbar-title">{TITLES[page]}</div>
            <div className="topbar-sub">Central de Atendimento ao Cidadão</div>
          </div>
          <div style={{ fontSize: 12, color: "var(--t3)", fontFamily: "DM Mono,monospace" }}>
            {new Date().toLocaleDateString("pt-BR", { weekday: "short", day: "2-digit", month: "short", year: "numeric" })}
          </div>
        </div>

        <div className="content">
          <Suspense fallback={<div className="loading-line">Carregando…</div>}>
            {page === "dashboard" && <Dashboard deptos={deptos} deptosByKey={deptosByKey} refreshKey={refreshKey} />}
          </Suspense>
          {page === "protocolos" && <Protocolos deptos={deptos} deptosByKey={deptosByKey} refreshKey={refreshKey} onChanged={bump} />}
          {page === "atendentes" && <Atendentes deptos={deptos} deptosByKey={deptosByKey} />}
          {page === "departamentos" && <Departamentos deptos={deptos} />}
          {page === "notificacoes" && <Notificacoes notifs={notifs} clear={() => setNotifs([])} />}
        </div>
      </div>
    </div>
  );
}
