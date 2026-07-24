import { useState } from "react";

export function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");

  function handleSubmit() {
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  }

  return (
    <div
      style={{
        display: "flex",
        gap: 8,
        padding: "10px 12px",
        borderTop: "1px solid #e2e8f0",
        background: "#fff",
      }}
    >
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        placeholder="Type your message..."
        disabled={disabled}
        style={{
          flex: 1,
          border: "1px solid #e2e8f0",
          borderRadius: 20,
          padding: "8px 14px",
          fontSize: 14,
          outline: "none",
          fontFamily: "inherit",
          background: disabled ? "#f8fafc" : "#fff",
        }}
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        style={{
          width: 36,
          height: 36,
          borderRadius: "50%",
          background: disabled ? "#94a3b8" : "#1A3C5E",
          border: "none",
          cursor: disabled ? "not-allowed" : "pointer",
          color: "#fff",
          fontSize: 16,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
        aria-label="Send message"
      >
        ➤
      </button>
    </div>
  );
}