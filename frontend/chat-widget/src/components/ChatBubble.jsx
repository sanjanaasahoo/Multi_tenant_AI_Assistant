export function ChatBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 10,
      }}
    >
      <div
        style={{
          maxWidth: "75%",
          padding: "9px 14px",
          borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
          background: isUser ? "#1A3C5E" : "#f1f5f9",
          color: isUser ? "#fff" : "#1e293b",
          fontSize: 14,
          lineHeight: 1.5,
          wordBreak: "break-word",
        }}
      >
        {message.text}
      </div>
    </div>
  );
}