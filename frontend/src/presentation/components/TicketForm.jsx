import { useState } from 'react';

export function TicketForm({ onSubmit }) {
  const [form, setForm] = useState({
    requesterName: '',
    department: 'SUPORTE',
    description: '',
  });

  const submit = async (event) => {
    event.preventDefault();
    await onSubmit(form);
    setForm({ requesterName: '', department: 'SUPORTE', description: '' });
  };

  return (
    <form className="space-y-3 rounded-xl border border-slate-700 bg-slate-900 p-4" onSubmit={submit}>
      <h2 className="text-lg font-semibold text-white">Novo chamado</h2>
      <input
        className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
        placeholder="Nome do solicitante"
        value={form.requesterName}
        onChange={(event) => setForm({ ...form, requesterName: event.target.value })}
        required
      />
      <input
        className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
        placeholder="Departamento"
        value={form.department}
        onChange={(event) => setForm({ ...form, department: event.target.value })}
        required
      />
      <textarea
        className="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100"
        placeholder="Descrição"
        value={form.description}
        onChange={(event) => setForm({ ...form, description: event.target.value })}
        required
      />
      <button className="rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-500" type="submit">
        Criar chamado
      </button>
    </form>
  );
}
