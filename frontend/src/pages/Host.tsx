import { useCallback, useState } from "react";
import {
  ApiError,
  RESTAURANT_ID,
  type WaitlistEntry,
  callEntry,
  listWaitlist,
  usePolling,
} from "../api/client";

function elapsedMinutes(joinedAt: string): number {
  const joined = new Date(joinedAt).getTime();
  return Math.max(0, Math.round((Date.now() - joined) / 60000));
}

export function Host() {
  const [entries, setEntries] = useState<WaitlistEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [callingId, setCallingId] = useState<number | null>(null);

  const poll = useCallback(() => {
    listWaitlist(RESTAURANT_ID)
      .then((data) => {
        setEntries(data);
        setError(null);
      })
      .catch((err: unknown) => {
        setError(err instanceof ApiError ? err.message : "Something went wrong.");
      });
  }, []);

  usePolling(poll);

  async function handleLlamar(entryId: number) {
    setCallingId(entryId);
    try {
      await callEntry(RESTAURANT_ID, entryId);
      setError(null);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 409
          ? "Ese cliente ya fue llamado o atendido por otra persona."
          : "Something went wrong.",
      );
    } finally {
      setCallingId(null);
      poll(); // refresh the queue either way, per FR10
    }
  }

  return (
    <main className="min-h-svh bg-slate-50 px-4 py-6 sm:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="flex items-baseline justify-between">
          <h1 className="text-xl font-semibold text-slate-900">La Terraza Azul · anfitrión</h1>
          <span className="text-sm text-slate-500">{entries.length} en cola</span>
        </div>

        {error && (
          <p
            role="alert"
            className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </p>
        )}

        <div className="mt-6 overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">#</th>
                <th className="px-4 py-3 font-medium">Nombre</th>
                <th className="px-4 py-3 font-medium">Personas</th>
                <th className="px-4 py-3 font-medium">Espera</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {entries.map((entry, index) => (
                <tr key={entry.id} className="text-slate-800">
                  <td className="px-4 py-3 font-medium tabular-nums text-slate-500">
                    {index + 1}
                  </td>
                  <td className="px-4 py-3 font-medium text-slate-900">{entry.name}</td>
                  <td className="px-4 py-3">{entry.partySize} pers.</td>
                  <td className="px-4 py-3 tabular-nums">{elapsedMinutes(entry.joinedAt)} min</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleLlamar(entry.id)}
                      disabled={callingId === entry.id}
                      className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Llamar
                    </button>
                  </td>
                </tr>
              ))}
              {entries.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center text-slate-400">
                    No hay nadie en la cola.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
