import { TicketRepository } from '../../domain/repositories/TicketRepository.js';
import { Ticket } from '../../domain/entities/Ticket.js';

export class PostgresTicketRepository extends TicketRepository {
  constructor(pool) {
    super();
    this.pool = pool;
  }

  mapRow(row) {
    return new Ticket({
      id:            row.id,
      requesterName: row.requester_name,
      department:    row.department,
      description:   row.description,
      status:        row.status,
      createdAt:     row.created_at,
      updatedAt:     row.updated_at,
    });
  }

  async findAll() {
    const result = await this.pool.query(
      'SELECT * FROM tickets ORDER BY created_at DESC'
    );
    return result.rows.map((row) => this.mapRow(row));
  }

  async findById(id) {
    const result = await this.pool.query(
      'SELECT * FROM tickets WHERE id = $1 LIMIT 1',
      [id]
    );
    if (result.rowCount === 0) return null;
    return this.mapRow(result.rows[0]);
  }

  async create(ticket) {
    const result = await this.pool.query(
      `INSERT INTO tickets (requester_name, department, description, status)
       VALUES ($1, $2, $3, $4)
       RETURNING *`,
      [ticket.requesterName, ticket.department, ticket.description, ticket.status]
    );
    return this.mapRow(result.rows[0]);
  }

  async updateStatus(id, status) {
    const result = await this.pool.query(
      `UPDATE tickets
       SET status = $1, updated_at = NOW()
       WHERE id = $2
       RETURNING *`,
      [status, id]
    );
    if (result.rowCount === 0) return null;
    return this.mapRow(result.rows[0]);
  }
}