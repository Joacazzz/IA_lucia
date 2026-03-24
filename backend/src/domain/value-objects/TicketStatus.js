export const TicketStatus = Object.freeze({
  OPEN: 'OPEN',
  IN_PROGRESS: 'IN_PROGRESS',
  RESOLVED: 'RESOLVED',
  CANCELED: 'CANCELED',
});

export const TicketStatusList = Object.values(TicketStatus);

export function validateTicketStatus(status) {
  if (!TicketStatusList.includes(status)) {
    throw new Error(`Invalid ticket status: ${status}`);
  }

  return status;
}
