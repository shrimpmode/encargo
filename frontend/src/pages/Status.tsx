import { useParams } from "react-router-dom";

// Placeholder for Phase 3 (position + polling). For now this just proves
// the join flow navigates here with a valid token.
export function Status() {
  const { token } = useParams<{ token: string }>();

  return (
    <main>
      <p>You're on the list.</p>
      <p>Token: {token}</p>
    </main>
  );
}
