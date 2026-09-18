const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// Single-restaurant demo (no QR/restaurant selection) — the join page is
// always tied to the one seeded pilot restaurant.
export const RESTAURANT_ID = 1;

export interface JoinRequest {
  name: string;
  phone: string;
  partySize: number;
}

export interface JoinResponse {
  statusToken: string;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function joinWaitlist(
  restaurantId: number,
  request: JoinRequest,
): Promise<JoinResponse> {
  const response = await fetch(`${API_BASE_URL}/restaurants/${restaurantId}/waitlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: request.name,
      phone: request.phone,
      party_size: request.partySize,
    }),
  });

  if (!response.ok) {
    throw new ApiError(`Failed to join waitlist (${response.status})`, response.status);
  }

  const data = (await response.json()) as { status_token: string };
  return { statusToken: data.status_token };
}
