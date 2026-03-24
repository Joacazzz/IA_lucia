import { TicketStatus, validateTicketStatus } from '../value-objects/TicketStatus.js';

export class Ticket {
  constructor({ id, requesterName, department, description, status = TicketStatus.OPEN, createdAt, updatedAt }) {
    this.id = id;
    this.requesterName = requesterName?.trim();
    this.department = department?.trim();
    this.description = description?.trim();
    this.status = validateTicketStatus(status);
    this.createdAt = createdAt ?? new Date().toISOString();
    this.updatedAt = updatedAt ?? new Date().toISOString();

    this.validate();
  }

  validate() {
    if (!this.requesterName) throw new Error('requesterName is required');
    if (!this.department) throw new Error('department is required');
    if (!this.description) throw new Error('description is required');
  }

  withStatus(status) {
    return new Ticket({
      ...this,
      status,
      updatedAt: new Date().toISOString(),
    });
  }
}
