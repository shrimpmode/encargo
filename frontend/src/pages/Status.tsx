import { type ReactNode, useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import { ApiError, type StatusResult, getStatus, usePolling } from "../api/client";

function Card({ children }: { children: ReactNode }) {
  return (
    <main className="flex min-h-svh items-center justify-center bg-slate-50 px-4 py-10">
      <div className="w-full max-w-sm rounded-2xl bg-white p-8 text-center shadow-sm ring-1 ring-slate-200">
        {children}
      </div>
    </main>
  );
}

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
      <Card>
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      </Card>
    );
  }

  if (!status) {
    return (
      <Card>
        <p className="text-slate-500">Cargando...</p>
      </Card>
    );
  }

  if (status.state === "waiting") {
    return (
      <Card>
        <p className="text-sm font-medium text-slate-500">Estás en el puesto</p>
        <p className="mt-2 text-7xl font-bold tabular-nums text-slate-900">{status.position}</p>
      </Card>
    );
  }

  // Called/other states get their real UI in a later phase (Voy en
  // camino / Ya no voy) — this just confirms the position view is gone.
  return (
    <Card>
      <p className="text-lg font-semibold text-emerald-600">Tu mesa está lista.</p>
    </Card>
  );
}
