import { useEffect, useRef } from "react";
import {
  ArcElement, BarController, BarElement, CategoryScale, Chart, DoughnutController, Filler,
  Legend, LinearScale, LineController, LineElement, PointElement, Tooltip,
} from "chart.js";

// Registra só o que o painel usa (o bundle "chart.js/auto" carrega tudo).
Chart.register(
  ArcElement, BarController, BarElement, CategoryScale, DoughnutController, Filler,
  Legend, LinearScale, LineController, LineElement, PointElement, Tooltip,
);
Chart.defaults.color = "#75877f";
Chart.defaults.font.family = "'DM Sans', sans-serif";

export default function ChartWidget({ type, data, options, height = 220 }) {
  const canvas = useRef(null);
  const chart = useRef(null);

  // Cria uma vez, destrói ao sair.
  useEffect(() => {
    chart.current = new Chart(canvas.current, { type, data, options });
    return () => { chart.current?.destroy(); chart.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [type]);

  // Dados novos: atualiza no lugar, sem recriar o gráfico.
  useEffect(() => {
    if (!chart.current) return;
    chart.current.data = data;
    chart.current.update();
  }, [data]);

  return (
    <div className="chart-box" style={{ height }}>
      <canvas ref={canvas} />
    </div>
  );
}
