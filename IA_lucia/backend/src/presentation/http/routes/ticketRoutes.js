import { Router } from 'express';

export function createTicketRouter(ticketController) {
  const router = Router();

  router.get('/tickets', ticketController.list);
  router.post('/tickets', ticketController.create);
  router.patch('/tickets/:id/status', ticketController.updateStatus);

  return router;
}
