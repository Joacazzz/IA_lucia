export function toTicket(raw) {
  return {
    id: raw.id,
    requesterName: raw.requesterName,
    department: raw.department,
    description: raw.description,
    status: raw.status,
    createdAt: raw.createdAt,
    updatedAt: raw.updatedAt,
  };
}
