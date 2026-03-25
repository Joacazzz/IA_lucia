import { validateTicketStatus } from '../../domain/value-objects/TicketStatus.js';

export class UpdateTicketStatusUseCase {
  constructor(ticketRepository) {
    this.ticketRepository = ticketRepository;
  }

  async execute({ id, status }) {
    validateTicketStatus(status);
    const updatedTicket = await this.ticketRepository.updateStatus(id, status);

    if (!updatedTicket) {
      throw new Error('Ticket not found');
    }

    return updatedTicket;
  }
}
