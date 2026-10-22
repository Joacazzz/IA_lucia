export default function Departamentos({ deptos }) {
  return (
    <div className="deptos-grid">
      {deptos.map((d) => (
        <div className="depto-card" key={d.chave}>
          <div className="depto-ic">{d.icone}</div>
          <div className="depto-nm">{d.nome}</div>
          <div className="depto-ds">{d.descricao}</div>
          <div className="depto-row">📞 Ramal <strong>{d.ramal}</strong></div>
          <div className="depto-row">📧 {d.email}</div>
          <div className="depto-row">🕐 {d.horario}</div>
        </div>
      ))}
    </div>
  );
}
