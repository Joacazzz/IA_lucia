import { toTicket } from '../../domain/entities/Ticket.js';

export function createTicketService(apiClient) {
  return {
    async listTickets() {
      const tickets = await apiClient.listTickets();
      return tickets.map(toTicket);
    },
    async createTicket(input) {
      const ticket = await apiClient.createTicket(input);
      return toTicket(ticket);
    },
    async updateStatus(id, status) {
      const ticket = await apiClient.updateStatus(id, status);
      return toTicket(ticket);
    },
  };
}
