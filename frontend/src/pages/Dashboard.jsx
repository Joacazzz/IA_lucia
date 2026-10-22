import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import ChartWidget from "../components/ChartWidget";
import { StatusBadge, STATUSES, deptoLabel, fmtDate } from "../utils";

const COLORS = ["#bd8741", "#8374ad", "#568a70", "#bd6c68"];
const GRID = "rgba(45,76,63,0.09)";
const TICK = "#75877f";

const DOUGHNUT_OPTS = {
  responsive: true, maintainAspectRatio: false, cutout: "68%",
  plugins: { legend: { position: "bottom", labels: { color: TICK, padding: 14, font: { size: 12 } } } },
};
const BAR_OPTS = {
  indexAxis: "y", responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: GRID }, ticks: { color: TICK, stepSize: 1 } },
    y: { grid: { display: false }, ticks: { color: TICK, font: { size: 11 } } },
  },
};
const LINE_OPTS = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: GRID }, ticks: { color: TICK } },
    y: { grid: { color: GRID }, ticks: { color: TICK, stepSize: 1 }, min: 0 },
  },
};

const ddmm = (iso) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;

export default function Dashboard({ deptos, deptosByKey, refreshKey }) {
  const [resumo, setResumo] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    const ctrl = new AbortController();
    api.get("/dashboard/resumo", { signal: ctrl.signal })
      .then((r) => { setResumo(r); setErro(""); })
      .catch((e) => e.name !== "AbortError" && setErro(e.message));
    return () => ctrl.abort();
  }, [refreshKey]);

  const doughnut = useMemo(() => resumo && ({
    labels: STATUSES,
    datasets: [{ data: STATUSES.map((s) => resumo.por_status[s] || 0), backgroundColor: COLORS, borderWidth: 0, hoverOffset: 6 }],
  }), [resumo]);

  const bar = useMemo(() => {
    if (!resumo) return null;
    const rows = deptos
      .map((d) => ({ nome: d.nome.split(" ")[0], n: resumo.por_departamento[d.chave] || 0 }))
      .filter((r) => r.n > 0);
    return {
      labels: rows.map((r) => r.nome),
      datasets: [{ data: rows.map((r) => r.n), backgroundColor: "rgba(91,142,240,0.7)", borderRadius: 4, maxBarThickness: 20 }],
    };
  }, [resumo, deptos]);

  const line = useMemo(() => resumo && ({
    labels: resumo.ultimos_7_dias.map((d) => ddmm(d.data)),
    datasets: [{
      data: resumo.ultimos_7_dias.map((d) => d.total),
      borderColor: "#5b8ef0", backgroundColor: "rgba(91,142,240,0.07)", fill: true, tension: 0.4,
      pointBackgroundColor: "#5b8ef0", pointRadius: 4, pointHoverRadius: 6, borderWidth: 2,
    }],
  }), [resumo]);

  if (erro) return <div className="login-err">{erro}</div>;
  if (!resumo) return <div className="loading-line">Carregando…</div>;

  const cnt = (s) => resumo.por_status[s] || 0;
  const cards = [
    { label: "Total", val: resumo.total, color: "var(--acc)", sub: "todos os departamentos" },
    { label: "Abertos", val: cnt("Aberto"), color: "var(--amb)", sub: "aguardando atendimento" },
    { label: "Em andamento", val: cnt("Em andamento"), color: "var(--pur)", sub: "sendo processados" },
    { label: "Resolvidos", val: cnt("Resolvido"), color: "var(--grn)", sub: "concluídos" },
  ];

  return (
    <>
      <div className="dashboard-intro">
        <h2>Um panorama do atendimento</h2>
        <p>Acompanhe os pedidos e veja o que precisa de atenção hoje.</p>
      </div>
      <div className="stats-grid">
        {cards.map((s) => (
          <div className="stat-card" key={s.label}>
            <div className="stat-acc" style={{ background: s.color }} />
            <div className="stat-lbl">{s.label}</div>
            <div className="stat-val" style={{ color: s.color }}>{s.val}</div>
            <div className="stat-sub">{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="charts-grid">
        <div className="card">
          <div className="card-hd"><div className="card-title">Distribuição por status</div></div>
          <div className="chart-wrap"><ChartWidget type="doughnut" data={doughnut} options={DOUGHNUT_OPTS} height={220} /></div>
        </div>
        <div className="card">
          <div className="card-hd"><div className="card-title">Protocolos por departamento</div></div>
          <div className="chart-wrap"><ChartWidget type="bar" data={bar} options={BAR_OPTS} height={220} /></div>
        </div>
      </div>

      <div style={{ marginBottom: 14 }}>
        <div className="card">
          <div className="card-hd"><div className="card-title">Tendência — últimos 7 dias</div></div>
          <div className="chart-wrap"><ChartWidget type="line" data={line} options={LINE_OPTS} height={160} /></div>
        </div>
      </div>

      <div className="card">
        <div className="card-hd"><div className="card-title">Atividade recente</div></div>
        {resumo.recentes.length === 0 ? (
          <div className="empty"><div className="empty-text">Sem protocolos</div></div>
        ) : (
          <table>
            <thead><tr><th>Número</th><th>Solicitante</th><th>Departamento</th><th>Status</th><th>Data</th></tr></thead>
            <tbody>
              {resumo.recentes.map((p) => (
                <tr key={p.numero}>
                  <td><span className="mono">{p.numero}</span></td>
                  <td style={{ color: "var(--t)" }}>{p.nome_solicitante}</td>
                  <td><span className="depto-tag">{deptoLabel(deptosByKey, p.departamento_chave)}</span></td>
                  <td><StatusBadge status={p.status} /></td>
                  <td>{fmtDate(p.criado_em)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
