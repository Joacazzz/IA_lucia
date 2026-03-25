import { TicketRepository } from '../../domain/repositories/TicketRepository.js';
import { Ticket } from '../../domain/entities/Ticket.js';

export class MySqlTicketRepository extends TicketRepository {
  constructor(pool) {
    super();
    this.pool = pool;
  }

  mapRow(row) {
    return new Ticket({
      id: row.id,
      requesterName: row.requester_name,
      department: row.department,
      description: row.description,
      status: row.status,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    });
  }

  async findAll() {
    const [rows] = await this.pool.query('SELECT * FROM tickets ORDER BY created_at DESC');
    return rows.map((row) => this.mapRow(row));
  }

  async findById(id) {
    const [rows] = await this.pool.query('SELECT * FROM tickets WHERE id = ? LIMIT 1', [id]);
    if (rows.length === 0) return null;
    return this.mapRow(rows[0]);
  }

  async create(ticket) {
    const [result] = await this.pool.query(
      `INSERT INTO tickets (requester_name, department, description, status)
       VALUES (?, ?, ?, ?)`,
      [ticket.requesterName, ticket.department, ticket.description, ticket.status],
    );

    return this.findById(result.insertId);
  }

  async updateStatus(id, status) {
    await this.pool.query(
      `UPDATE tickets
       SET status = ?, updated_at = CURRENT_TIMESTAMP
       WHERE id = ?`,
      [status, id],
    );

    return this.findById(id);
  }
}
