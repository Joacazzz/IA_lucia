import { useState } from "react";
import { api } from "../api";

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState("");

  async function entrar(e) {
    e.preventDefault();
    setLoading(true);
    setErro("");
    try {
      const data = await api.login(email.trim(), senha);
      onLogin(data.access_token, data.user);
    } catch (err) {
      setErro(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={entrar}>
        <div className="login-logo">Lucía</div>
        <div className="login-sub">Sua central para organizar os atendimentos com tranquilidade.</div>
        {erro && <div className="login-err">{erro}</div>}
        <div className="fg">
          <label className="fl">E-mail</label>
          <input className="fi" type="email" autoComplete="username" value={email}
                 onChange={(e) => setEmail(e.target.value)} required autoFocus />
        </div>
        <div className="fg">
          <label className="fl">Senha</label>
          <input className="fi" type="password" autoComplete="current-password" value={senha}
                 onChange={(e) => setSenha(e.target.value)} required />
        </div>
        <button className="btn btn-primary" type="submit" disabled={loading}
                style={{ width: "100%", justifyContent: "center", marginTop: 4 }}>
          {loading ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </div>
  );
}
