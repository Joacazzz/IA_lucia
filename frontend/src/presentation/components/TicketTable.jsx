import { TicketStatus } from '../../domain/value-objects/TicketStatus.js';

const statusValues = Object.values(TicketStatus);

export function TicketTable({ tickets, onChangeStatus }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900 p-4">
      <h2 className="mb-3 text-lg font-semibold text-white">Chamados</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-200">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400">
              <th className="py-2">ID</th>
              <th>Solicitante</th>
              <th>Departamento</th>
              <th>Status</th>
              <th>Ação</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((ticket) => (
              <tr key={ticket.id} className="border-b border-slate-800">
                <td className="py-2">#{ticket.id}</td>
                <td>{ticket.requesterName}</td>
                <td>{ticket.department}</td>
                <td>{ticket.status}</td>
                <td>
                  <select
                    className="rounded-md border border-slate-700 bg-slate-800 px-2 py-1"
                    value={ticket.status}
                    onChange={(event) => onChangeStatus(ticket.id, event.target.value)}
                  >
                    {statusValues.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
