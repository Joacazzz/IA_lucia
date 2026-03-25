import { pool } from './infrastructure/db/mysqlPool.js';
import { MySqlTicketRepository } from './infrastructure/repositories/MySqlTicketRepository.js';
import { ListTicketsUseCase } from './application/use-cases/ListTicketsUseCase.js';
import { CreateTicketUseCase } from './application/use-cases/CreateTicketUseCase.js';
import { UpdateTicketStatusUseCase } from './application/use-cases/UpdateTicketStatusUseCase.js';
import { TicketController } from './presentation/http/controllers/TicketController.js';
import { createTicketRouter } from './presentation/http/routes/ticketRoutes.js';
import { errorHandler } from './presentation/http/middlewares/errorHandler.js';
import { createServer } from './presentation/http/server.js';

const ticketRepository = new MySqlTicketRepository(pool);

const ticketController = new TicketController({
  listTicketsUseCase: new ListTicketsUseCase(ticketRepository),
  createTicketUseCase: new CreateTicketUseCase(ticketRepository),
  updateTicketStatusUseCase: new UpdateTicketStatusUseCase(ticketRepository),
});

const app = createServer({
  ticketRoutes: createTicketRouter(ticketController),
  errorHandler,
});

const PORT = Number(process.env.PORT ?? 3333);

app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
