export default function Notificacoes({ notifs, clear }) {
  return (
    <div className="card">
      <div className="card-hd">
        <div><div className="card-title">Notificações em tempo real</div><div className="card-sub">{notifs.length} evento(s)</div></div>
        {notifs.length > 0 && <button className="btn btn-ghost btn-sm" onClick={clear}>Limpar</button>}
      </div>
      {notifs.length === 0 ? (
        <div className="empty"><div className="empty-icon">🔔</div>
          <div className="empty-text">Sem notificações ainda. Crie ou atualize um protocolo para ver as notificações em tempo real.</div></div>
      ) : (
        notifs.map((n) => (
          <div className="notif-item" key={n.id}>
            <div className={`notif-icon ${n.tipo === "novo_protocolo" ? "ni-new" : "ni-update"}`}>
              {n.tipo === "novo_protocolo" ? "📋" : "🔄"}
            </div>
            <div>
              <div className="notif-msg">{n.mensagem}</div>
              <div className="notif-time">{n.timestamp ? new Date(n.timestamp).toLocaleTimeString("pt-BR") : "agora"}</div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
