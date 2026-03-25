import { Ticket } from '../../domain/entities/Ticket.js';

export class CreateTicketUseCase {
  constructor(ticketRepository) {
    this.ticketRepository = ticketRepository;
  }

  async execute(input) {
    const ticket = new Ticket({
      requesterName: input.requesterName,
      department: input.department,
      description: input.description,
    });

    return this.ticketRepository.create(ticket);
  }
}
