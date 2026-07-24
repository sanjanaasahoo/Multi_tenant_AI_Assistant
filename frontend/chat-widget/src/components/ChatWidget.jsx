import { useEffect, useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import { ChatBubble } from "./ChatBubble";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, sendUserMessage, isLoading, error } = useChat();
  const bottomRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={() => setIsOpen((o) => !o)}
        aria-label={isOpen ? "Close chat" : "Open chat"}
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          width: 52,
          height: 52,
          borderRadius: "50%",
          background: "#1A3C5E",
          border: "none",
          cursor: "pointer",
          color: "#fff",
          fontSize: 22,
          boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
          zIndex: 1000,
        }}
      >
        {isOpen ? "✕" : "💬"}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div
          style={{
            position: "fixed",
            bottom: 88,
            right: 24,
            width: 360,
            height: 500,
            borderRadius: 16,
            border: "1px solid #e2e8f0",
            boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            zIndex: 999,
            background: "#fff",
            fontFamily: "system-ui, sans-serif",
          }}
          role="dialog"
          aria-label="Crushaders Tech chat assistant"
        >
          {/* Header */}
          <div
            style={{
              background: "#1A3C5E",
              padding: "14px 16px",
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "#4ade80",
              }}
            />
            <div>
              <div style={{ color: "#fff", fontWeight: 500, fontSize: 14 }}>
                Crushaders Tech Assistant
              </div>
              <div style={{ color: "rgba(255,255,255,0.55)", fontSize: 11 }}>
                Typically replies instantly
              </div>
            </div>
          </div>

          {/* Error banner */}
          {error && (
            <div
              style={{
                background: "#fef2f2",
                color: "#991b1b",
                fontSize: 12,
                padding: "6px 14px",
                borderBottom: "1px solid #fecaca",
              }}
            >
              {error}
            </div>
          )}

          {/* Messages */}
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "14px 14px 0",
              background: "#f8fafc",
            }}
          >
            {messages.map((msg) => (
              <ChatBubble key={msg.id} message={msg} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <ChatInput onSend={sendUserMessage} disabled={isLoading} />
        </div>
      )}
    </>
  );
}