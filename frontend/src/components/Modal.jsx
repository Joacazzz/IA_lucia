import { useEffect } from "react";

export default function Modal({ title, onClose, footer, children }) {
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-hd">
          <div className="modal-title">{title}</div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="modal-bd">{children}</div>
        <div className="modal-ft">{footer}</div>
      </div>
    </div>
  );
}
