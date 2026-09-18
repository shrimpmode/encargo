import { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import { ApiError, type StatusResult, getStatus, usePolling } from "../api/client";

export function Status() {
  const { token } = useParams<{ token: string }>();
  const [status, setStatus] = useState<StatusResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const poll = useCallback(() => {
    if (!token) return;
    getStatus(token)
      .then((result) => {
        setStatus(result);
        setError(null);
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Something went wrong.");
      });
  }, [token]);

  usePolling(poll);

  if (error) {
    return (
      <main>
        <p role="alert">{error}</p>
      </main>
    );
  }

  if (!status) {
    return (
      <main>
        <p>Cargando...</p>
      </main>
    );
  }

  if (status.state === "waiting") {
    return (
      <main>
        <p>Estás en el puesto</p>
        <p>{status.position}</p>
      </main>
    );
  }

  // Called/other states get their real UI in a later phase (Voy en
  // camino / Ya no voy) — this just confirms the position view is gone.
  return (
    <main>
      <p>Tu mesa está lista.</p>
    </main>
  );
}
