const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const WEBSITE_ID = import.meta.env.VITE_WEBSITE_ID ?? "crushaders_tech";

export async function sendMessage(message, sessionId) {
  const response = await fetch(`${BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      website_id: WEBSITE_ID,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json(); // { reply: string, sources: string[] }
}