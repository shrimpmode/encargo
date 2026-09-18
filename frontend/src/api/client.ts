import { useEffect, useRef } from "react";

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

export type WaitlistState = "waiting" | "called" | "seated" | "cancelled" | "no_show";

export interface StatusResult {
  state: WaitlistState;
  position: number | null;
}

export async function getStatus(token: string): Promise<StatusResult> {
  const response = await fetch(`${API_BASE_URL}/waitlist/status/${token}`);

  if (!response.ok) {
    throw new ApiError(`Failed to fetch status (${response.status})`, response.status);
  }

  const data = (await response.json()) as { state: WaitlistState; position: number | null };
  return { state: data.state, position: data.position };
}

export interface WaitlistEntry {
  id: number;
  name: string;
  partySize: number;
  joinedAt: string;
}

export async function listWaitlist(restaurantId: number): Promise<WaitlistEntry[]> {
  const response = await fetch(`${API_BASE_URL}/restaurants/${restaurantId}/waitlist`);

  if (!response.ok) {
    throw new ApiError(`Failed to fetch waitlist (${response.status})`, response.status);
  }

  const data = (await response.json()) as Array<{
    id: number;
    name: string;
    party_size: number;
    joined_at: string;
  }>;
  return data.map((e) => ({
    id: e.id,
    name: e.name,
    partySize: e.party_size,
    joinedAt: e.joined_at,
  }));
}

const POLL_INTERVAL_MS = 5000;

// Polls `callback` every 5s without resetting the interval on every render
// (the ref keeps the interval stable while always calling the latest closure).
export function usePolling(callback: () => void): void {
  const callbackRef = useRef(callback);

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    callbackRef.current();
    const id = setInterval(() => callbackRef.current(), POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);
}
