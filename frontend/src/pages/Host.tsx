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
    <main>
      <h1>La Terraza Azul · anfitrión</h1>
      {error && <p role="alert">{error}</p>}
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Nombre</th>
            <th>Personas</th>
            <th>Espera</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry, index) => (
            <tr key={entry.id}>
              <td>{index + 1}</td>
              <td>{entry.name}</td>
              <td>{entry.partySize} pers.</td>
              <td>{elapsedMinutes(entry.joinedAt)} min</td>
              <td>
                <button onClick={() => handleLlamar(entry.id)} disabled={callingId === entry.id}>
                  Llamar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
