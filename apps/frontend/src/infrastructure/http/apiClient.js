const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:3333/api';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ error: 'Erro inesperado' }));
    throw new Error(body.error ?? 'Erro ao comunicar com API');
  }

  return response.json();
}

export const apiClient = {
  listTickets: () => request('/tickets'),
  createTicket: (payload) => request('/tickets', { method: 'POST', body: JSON.stringify(payload) }),
  updateStatus: (id, status) => request(`/tickets/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),
};
