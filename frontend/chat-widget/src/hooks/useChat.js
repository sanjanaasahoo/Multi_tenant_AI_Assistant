import { useState, useCallback, useRef } from "react";
import { sendMessage } from "../api/chatApi";

const INITIAL_MESSAGES = [
  {
    id: "welcome",
    role: "bot",
    text: "Hi! I'm the Crushaders Tech assistant. How can I help you today?",
  },
];

// Simple unique ID generator — no library needed
const uid = () => `msg-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

export function useChat() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const sessionId = useRef(`sess-${Date.now()}`);

  const sendUserMessage = useCallback(async (text) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    setError(null);

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      { id: uid(), role: "user", text: trimmed },
    ]);
    setIsLoading(true);

    try {
      const data = await sendMessage(trimmed, sessionId.current);
      setMessages((prev) => [
        ...prev,
        { id: uid(), role: "bot", text: data.reply },
      ]);
    } catch (err) {
      setError("Could not reach the server. Is the backend running?");
      setMessages((prev) => [
        ...prev,
        {
          id: uid(),
          role: "bot",
          text: "Sorry, I couldn't connect to the server right now.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  return { messages, sendUserMessage, isLoading, error };
}