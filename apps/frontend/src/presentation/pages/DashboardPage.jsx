import { TicketForm } from '../components/TicketForm.jsx';
import { TicketTable } from '../components/TicketTable.jsx';
import { useTickets } from '../hooks/useTickets.js';

export function DashboardPage() {
  const { tickets, loading, error, createTicket, updateStatus } = useTickets();

  return (
    <main className="mx-auto min-h-screen max-w-6xl space-y-4 p-6">
      <header className="rounded-xl border border-slate-700 bg-slate-900 p-4">
        <h1 className="text-2xl font-bold text-white">Lucía Admin - React + Clean Architecture</h1>
        <p className="text-slate-400">Backend em Node.js + Express + PostgreSQL</p>
      </header>

      {loading && <p className="text-slate-400">Carregando...</p>}
      {error && <p className="rounded-md bg-red-900/30 p-3 text-red-300">{error}</p>}

      <section className="grid gap-4 lg:grid-cols-[340px_1fr]">
        <TicketForm onSubmit={createTicket} />
        <TicketTable tickets={tickets} onChangeStatus={updateStatus} />
      </section>
    </main>
  );
}
