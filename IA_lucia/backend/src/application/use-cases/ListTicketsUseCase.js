export class ListTicketsUseCase {
  constructor(ticketRepository) {
    this.ticketRepository = ticketRepository;
  }

  async execute() {
    return this.ticketRepository.findAll();
  }
}
