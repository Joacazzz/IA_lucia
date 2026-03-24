import { useEffect, useMemo, useState } from 'react';
import { createTicketService } from '../../application/use-cases/useTicketService.js';
import { apiClient } from '../../infrastructure/http/apiClient.js';

export function useTickets() {
  const ticketService = useMemo(() => createTicketService(apiClient), []);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      setLoading(true);
      const data = await ticketService.listTickets();
      setTickets(data);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const createTicket = async (payload) => {
    await ticketService.createTicket(payload);
    await load();
  };

  const updateStatus = async (id, status) => {
    await ticketService.updateStatus(id, status);
    await load();
  };

  return { tickets, loading, error, createTicket, updateStatus };
}
