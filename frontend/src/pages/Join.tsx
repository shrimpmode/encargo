import { type FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, RESTAURANT_ID, joinWaitlist } from "../api/client";

export function Join() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [partySize, setPartySize] = useState(2);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const { statusToken } = await joinWaitlist(RESTAURANT_ID, { name, phone, partySize });
      navigate(`/status/${statusToken}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <h1>La Terraza Azul</h1>
      <p>Lista de espera · hoy</p>
      <form onSubmit={handleSubmit}>
        <label>
          Nombre
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>
        <label>
          Teléfono
          <input value={phone} onChange={(e) => setPhone(e.target.value)} required />
        </label>
        <label>
          ¿Cuántos son?
          <input
            type="number"
            min={1}
            value={partySize}
            onChange={(e) => setPartySize(Number(e.target.value))}
            required
          />
        </label>
        {error && <p role="alert">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Uniendo..." : "Unirme a la cola"}
        </button>
      </form>
    </main>
  );
}
