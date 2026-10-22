import { useEffect, useState } from "react";
import { api } from "../api";
import Modal from "../components/Modal";
import { useToast } from "../components/Toasts";
import { deptoLabel } from "../utils";

export default function Atendentes({ deptos, deptosByKey }) {
  const toast = useToast();
  const [lista, setLista] = useState(null);
  const [fDepto, setFDepto] = useState("");
  const [novo, setNovo] = useState(false);

  useEffect(() => {
    api.get("/atendentes").then(setLista).catch((e) => { toast(e.message, "error"); setLista([]); });
  }, [toast]);

  async function remover(a) {
    try {
      await api.del(`/atendentes/${a.id}`);
      setLista((l) => l.filter((x) => x.id !== a.id));
      toast(`${a.nome} removido`);
    } catch (e) {
      toast(e.message, "error");
    }
  }

  if (!lista) return <div className="loading-line">Carregando…</div>;
  const filtrada = lista.filter((a) => !fDepto || a.departamento_chave === fDepto);

  return (
    <>
      <div className="card">
        <div className="card-hd">
          <div><div className="card-title">Atendentes</div><div className="card-sub">{filtrada.length} ativo(s)</div></div>
          <div className="filters">
            <select className="select" value={fDepto} onChange={(e) => setFDepto(e.target.value)}>
              <option value="">Todos os deptos</option>
              {deptos.map((d) => <option key={d.chave} value={d.chave}>{d.nome}</option>)}
            </select>
            <button className="btn btn-primary btn-sm" onClick={() => setNovo(true)}>+ Cadastrar</button>
          </div>
        </div>
        {filtrada.length === 0 ? (
          <div className="empty"><div className="empty-icon">👤</div><div className="empty-text">Nenhum atendente cadastrado</div></div>
        ) : (
          <table>
            <thead><tr><th>Nome</th><th>E-mail</th><th>Departamento</th><th></th></tr></thead>
            <tbody>
              {filtrada.map((a) => (
                <tr key={a.id}>
                  <td style={{ color: "var(--t)" }}>{a.nome}</td>
                  <td>{a.email}</td>
                  <td><span className="depto-tag">{deptoLabel(deptosByKey, a.departamento_chave)}</span></td>
                  <td><button className="btn btn-danger btn-sm" onClick={() => remover(a)}>Remover</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      {novo && (
        <ModalNovoAtendente deptos={deptos} onClose={() => setNovo(false)}
                            onCreated={(a) => { setLista((l) => [...l, a]); setNovo(false); }} />
      )}
    </>
  );
}

function ModalNovoAtendente({ deptos, onClose, onCreated }) {
  const toast = useToast();
  const [f, setF] = useState({ nome: "", email: "", departamento_chave: "" });
  const [saving, setSaving] = useState(false);
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }));

  async function salvar() {
    if (!f.nome.trim() || !f.email.trim() || !f.departamento_chave) return toast("Preencha todos os campos.", "error");
    setSaving(true);
    try {
      onCreated(await api.post("/atendentes", f));
      toast("Atendente cadastrado");
    } catch (e) {
      toast(e.message, "error");
      setSaving(false);
    }
  }

  return (
    <Modal
      title="Novo atendente"
      onClose={onClose}
      footer={<>
        <button className="btn btn-ghost btn-sm" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary btn-sm" onClick={salvar} disabled={saving}>{saving ? "Salvando…" : "Cadastrar"}</button>
      </>}
    >
      <div className="fg"><label className="fl">Nome completo *</label>
        <input className="fi" placeholder="Nome" value={f.nome} onChange={set("nome")} /></div>
      <div className="fg"><label className="fl">E-mail *</label>
        <input className="fi" type="email" placeholder="email@empresa.com.br" value={f.email} onChange={set("email")} /></div>
      <div className="fg"><label className="fl">Departamento *</label>
        <select className="fs" value={f.departamento_chave} onChange={set("departamento_chave")}>
          <option value="">Selecione…</option>
          {deptos.map((d) => <option key={d.chave} value={d.chave}>{d.icone} {d.nome}</option>)}
        </select>
      </div>
    </Modal>
  );
}
