import express from 'express';
import cors from 'cors';

export function createServer({ ticketRoutes, errorHandler }) {
  const app = express();

  app.use(cors());
  app.use(express.json());

  app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
  });

  app.use('/api', ticketRoutes);
  app.use(errorHandler);

  return app;
}
