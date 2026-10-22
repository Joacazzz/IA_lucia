import { createContext, useCallback, useContext, useMemo, useState } from "react";

const ToastCtx = createContext(() => {});
export const useToast = () => useContext(ToastCtx);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const remove = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), []);
  const show = useCallback((msg, type = "success") => {
    const id = crypto.randomUUID();
    setToasts((t) => [...t, { id, msg, type }]);
    setTimeout(() => remove(id), 3500);
  }, [remove]);

  const value = useMemo(() => show, [show]);

  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div className="toast-wrap">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.type}`} onClick={() => remove(t.id)}>
            {t.type === "success" ? "✓" : t.type === "error" ? "✕" : "●"} {t.msg}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}
