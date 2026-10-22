import { useEffect, useRef } from "react";
import { WS_URL } from "../api";

/** WebSocket autenticado, com reconexão exponencial e ping para manter a conexão viva. */
export function useRealtime(token, onMessage, onStatus) {
  const handler = useRef(onMessage);
  const status = useRef(onStatus);
  handler.current = onMessage;
  status.current = onStatus;

  useEffect(() => {
    if (!token) return;
    let ws, retry = 0, timer, ping, closed = false;

    const connect = () => {
      ws = new WebSocket(`${WS_URL}?token=${encodeURIComponent(token)}`);
      ws.onopen = () => {
        retry = 0;
        status.current?.(true);
        ping = setInterval(() => ws.readyState === 1 && ws.send("ping"), 25000);
      };
      ws.onmessage = (e) => {
        try { handler.current(JSON.parse(e.data)); } catch { /* ignora lixo */ }
      };
      ws.onclose = () => {
        clearInterval(ping);
        status.current?.(false);
        if (!closed) timer = setTimeout(connect, Math.min(30000, 1000 * 2 ** retry++));
      };
    };

    connect();
    return () => {
      closed = true;
      clearTimeout(timer);
      clearInterval(ping);
      ws?.close();
    };
  }, [token]);
}
