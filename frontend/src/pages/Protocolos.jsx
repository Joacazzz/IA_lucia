import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import Modal from "../components/Modal";
import { useToast } from "../components/Toasts";
import { StatusBadge, STATUSES, deptoLabel, fmtDate, useDebounced } from "../utils";

const PAGE_SIZE = 25;

export default function Protocolos({ deptos, deptosByKey, refreshKey, onChanged }) {
  const toast = useToast();
  const [fDepto, setFDepto] = useState("");
  const [fStatus, setFStatus] = useState("");
  const [busca, setBusca] = useState("");
  const q = useDebounced(busca.trim(), 350);
  const [page, setPage] = useState(0);
  const [data, setData] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [sel, setSel] = useState(null);
  const [novo, setNovo] = useState(false);

  // Mudou filtro → volta para a primeira página.
  useEffect(() => { setPage(0); }, [fDepto, fStatus, q]);

  useEffect(() => {
    const ctrl = new AbortController();
    const params = new URLSearchParams({ limit: PAGE_SIZE, offset: page * PAGE_SIZE });
    if (fDepto) params.set("departamento", fDepto);
    if (fStatus) params.set("status", fStatus);
    if (q) params.set("q", q);
    setLoading(true);
    api.list(`/protocolos?${params}`, { signal: ctrl.signal })
      .then((r) => { setData(r); setLoading(false); })
      .catch((e) => {
        if (e.name === "AbortError") return;
        toast(e.message, "error");
        setLoading(false);
      });
    return () => ctrl.abort();
  }, [fDepto, fStatus, q, page, refreshKey, toast]);

  const pages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));

  return (
    <>
      <div className="card">
        <div className="card-hd">
          <div>
            <div className="card-title">Protocolos</div>
            <div className="card-sub">{data.total} registro(s)</div>
          </div>
          <div className="filters">
            <input className="input" placeholder="Buscar nome ou nº…" value={busca} onChange={(e) => setBusca(e.target.value)} />
            <select className="select" value={fDepto} onChange={(e) => setFDepto(e.target.value)}>
              <option value="">Todos os deptos</option>
              {deptos.map((d) => <option key={d.chave} value={d.chave}>{d.nome}</option>)}
            </select>
            <select className="select" value={fStatus} onChange={(e) => setFStatus(e.target.value)}>
              <option value="">Todos os status</option>
              {STATUSES.map((s) => <option key={s}>{s}</option>)}
            </select>
            <button className="btn btn-primary btn-sm" onClick={() => setNovo(true)}>+ Novo</button>
          </div>
        </div>

        {loading && data.items.length === 0 ? (
          <div className="loading-line">Carregando…</div>
        ) : data.items.length === 0 ? (
          <div className="empty"><div className="empty-icon">📋</div><div className="empty-text">Nenhum protocolo encontrado</div></div>
        ) : (
          <table style={{ opacity: loading ? 0.6 : 1 }}>
            <thead><tr><th>Número</th><th>Solicitante</th><th>Departamento</th><th>Status</th><th>Data</th><th></th></tr></thead>
            <tbody>
              {data.items.map((p) => (
                <tr key={p.numero}>
                  <td><span className="mono">{p.numero}</span></td>
                  <td style={{ color: "var(--t)" }}>{p.nome_solicitante}</td>
                  <td><span className="depto-tag">{deptoLabel(deptosByKey, p.departamento_chave)}</span></td>
                  <td><StatusBadge status={p.status} /></td>
                  <td>{fmtDate(p.criado_em)}</td>
                  <td><button className="btn btn-ghost btn-sm" onClick={() => setSel(p)}>Ver</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {data.total > PAGE_SIZE && (
          <div className="pager">
            <span>Página {page + 1} de {pages}</span>
            <div className="pager-btns">
              <button className="btn btn-ghost btn-sm" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>← Anterior</button>
              <button className="btn btn-ghost btn-sm" disabled={page + 1 >= pages} onClick={() => setPage((p) => p + 1)}>Próxima →</button>
            </div>
          </div>
        )}
      </div>

      {sel && (
        <ModalDetalhe proto={sel} deptosByKey={deptosByKey} onClose={() => setSel(null)}
                      onSaved={() => { setSel(null); onChanged(); }} />
      )}
      {novo && (
        <ModalNovo deptos={deptos} onClose={() => setNovo(false)}
                   onCreated={() => { setNovo(false); onChanged(); }} />
      )}
    </>
  );
}

function ModalDetalhe({ proto, deptosByKey, onClose, onSaved }) {
  const toast = useToast();
  const [status, setStatus] = useState(proto.status);
  const [saving, setSaving] = useState(false);

  async function salvar() {
    if (status === proto.status) return onClose();
    setSaving(true);
    try {
      await api.patch(`/protocolos/${proto.numero}`, { status });
      toast("Status atualizado");
      onSaved();
    } catch (e) {
      toast(e.message, "error");
      setSaving(false);
    }
  }

  const row = (k, v) => <div className="detail-row"><span className="dk">{k}</span><span className="dv">{v}</span></div>;

  return (
    <Modal
      title={<>Protocolo <span className="mono">{proto.numero}</span></>}
      onClose={onClose}
      footer={<>
        <button className="btn btn-ghost btn-sm" onClick={onClose}>Fechar</button>
        <button className="btn btn-primary btn-sm" onClick={salvar} disabled={saving}>{saving ? "Salvando…" : "Salvar status"}</button>
      </>}
    >
      {row("Solicitante", proto.nome_solicitante)}
      {row("Contato", proto.contato || "—")}
      {row("Departamento", deptoLabel(deptosByKey, proto.departamento_chave))}
      {row("Abertura", fmtDate(proto.criado_em))}
      {row("Atualização", fmtDate(proto.atualizado_em))}
      {row("Descrição", <span style={{ whiteSpace: "pre-wrap" }}>{proto.descricao}</span>)}
      {row("Status", (
        <select className="fs" value={status} onChange={(e) => setStatus(e.target.value)} style={{ width: "auto" }}>
          {STATUSES.map((s) => <option key={s}>{s}</option>)}
        </select>
      ))}
    </Modal>
  );
}

function ModalNovo({ deptos, onClose, onCreated }) {
  const toast = useToast();
  const [f, setF] = useState({ departamento_chave: "", nome_solicitante: "", contato: "", descricao: "" });
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }));

  async function salvar() {
    if (!f.departamento_chave || !f.nome_solicitante.trim() || !f.descricao.trim()) {
      return setErr("Preencha os campos obrigatórios.");
    }
    setSaving(true);
    setErr("");
    try {
      const p = await api.post("/protocolos", f);
      toast(`Protocolo ${p.numero} criado`);
      onCreated();
    } catch (e) {
      setErr(e.message);
      setSaving(false);
    }
  }

  return (
    <Modal
      title="Novo protocolo"
      onClose={onClose}
      footer={<>
        <button className="btn btn-ghost btn-sm" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary btn-sm" onClick={salvar} disabled={saving}>{saving ? "Criando…" : "Criar protocolo"}</button>
      </>}
    >
      {err && <div className="login-err" style={{ marginBottom: 14 }}>{err}</div>}
      <div className="g2">
        <div className="fg"><label className="fl">Nome do solicitante *</label>
          <input className="fi" placeholder="Nome completo" value={f.nome_solicitante} onChange={set("nome_solicitante")} /></div>
        <div className="fg"><label className="fl">Contato</label>
          <input className="fi" placeholder="E-mail ou telefone" value={f.contato} onChange={set("contato")} /></div>
      </div>
      <div className="fg"><label className="fl">Departamento *</label>
        <select className="fs" value={f.departamento_chave} onChange={set("departamento_chave")}>
          <option value="">Selecione…</option>
          {deptos.map((d) => <option key={d.chave} value={d.chave}>{d.icone} {d.nome}</option>)}
        </select>
      </div>
      <div className="fg"><label className="fl">Descrição *</label>
        <textarea className="ft" placeholder="Descreva detalhadamente…" value={f.descricao} onChange={set("descricao")} /></div>
    </Modal>
  );
}
