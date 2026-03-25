export class TicketRepository {
  async findAll() {
    throw new Error('TicketRepository.findAll must be implemented');
  }

  async findById(_id) {
    throw new Error('TicketRepository.findById must be implemented');
  }

  async create(_ticket) {
    throw new Error('TicketRepository.create must be implemented');
  }

  async updateStatus(_id, _status) {
    throw new Error('TicketRepository.updateStatus must be implemented');
  }
}
