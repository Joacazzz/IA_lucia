export class TicketController {
  constructor({ listTicketsUseCase, createTicketUseCase, updateTicketStatusUseCase }) {
    this.listTicketsUseCase = listTicketsUseCase;
    this.createTicketUseCase = createTicketUseCase;
    this.updateTicketStatusUseCase = updateTicketStatusUseCase;
  }

  list = async (_req, res, next) => {
    try {
      const tickets = await this.listTicketsUseCase.execute();
      res.json(tickets);
    } catch (error) {
      next(error);
    }
  };

  create = async (req, res, next) => {
    try {
      const ticket = await this.createTicketUseCase.execute(req.body);
      res.status(201).json(ticket);
    } catch (error) {
      next(error);
    }
  };

  updateStatus = async (req, res, next) => {
    try {
      const ticket = await this.updateTicketStatusUseCase.execute({
        id: Number(req.params.id),
        status: req.body.status,
      });
      res.json(ticket);
    } catch (error) {
      next(error);
    }
  };
}
