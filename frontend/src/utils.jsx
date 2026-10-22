export const STATUSES = ["Aberto", "Em andamento", "Resolvido", "Cancelado"];

const BADGE = {
  "Aberto": "b-amb",
  "Em andamento": "b-pur",
  "Resolvido": "b-grn",
  "Cancelado": "b-red",
};

export function StatusBadge({ status }) {
  return (
    <span className={`badge ${BADGE[status] || "b-gray"}`}>
      <span className="bd" />
      {status}
    </span>
  );
}

const dtf = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
});

export function fmtDate(d) {
  return d ? dtf.format(new Date(d)) : "—";
}

export function deptoLabel(deptosByKey, chave) {
  const d = deptosByKey[chave];
  return d ? `${d.icone} ${d.nome}` : chave;
}

export function useDebounced(value, ms = 300) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return v;
}
import { useEffect, useState } from "react";
