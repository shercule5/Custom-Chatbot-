import { useRef, useState } from "react";

export default function App() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [thinking, setThinking] = useState(false);
  const [endpoint] = useState("http://127.0.0.1:8000/chat-stream"); // backend
  const controllerRef = useRef(null);

  async function ask() {
    if (!query.trim()) return;
    setAnswer("");
    setThinking(true);

    // abort previous stream if any
    if (controllerRef.current) controllerRef.current.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          k: 5,
          temperature: 0.4,
          system: "You are a helpful assistant.",
          history: [],
        }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        // Parse SSE: split on double newline, then parse "event:" and "data:"
        for (const block of chunk.split("\n\n")) {
          if (!block.trim()) continue;

          let evt = "message";
          let data = "";

          for (const line of block.split("\n")) {
            if (line.startsWith("event:")) evt = line.slice(6).trim();
            else if (line.startsWith("data:")) data += line.slice(5).trim();
          }

          if (evt === "meta") {
            // You could display sources here if you want
            // const meta = JSON.parse(data);
          } else if (evt === "token") {
            setAnswer((prev) => prev + data);
          } else if (evt === "done") {
            setThinking(false);
          }
        }
      }
    } catch (err) {
      setThinking(false);
      setAnswer("Error talking to backend.");
      console.error(err);
    }
  }

  return (
    <div style={{ maxWidth: 760, margin: "60px auto", fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: 48, marginBottom: 24 }}>Custom RAG Chatbot</h1>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask me anything from your ingested files…"
        rows={3}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 8,
          border: "1px solid #cfd6e4",
          outline: "none",
          fontSize: 16,
        }}
      />

      <div style={{ marginTop: 12, display: "flex", gap: 12, alignItems: "center" }}>
        <button
          onClick={ask}
          disabled={thinking}
          style={{
            padding: "10px 16px",
            borderRadius: 10,
            border: "none",
            background: "#111827",
            color: "white",
            fontWeight: 600,
            cursor: "pointer",
            opacity: thinking ? 0.6 : 1,
          }}
        >
          {thinking ? "Thinking…" : "Ask"}
        </button>

        <div style={{ fontSize: 14, color: "#6b7280" }}>
          Backend: <code>/chat-stream</code>
        </div>
      </div>

      <h2 style={{ marginTop: 28 }}>Response:</h2>
      <div
        style={{
          minHeight: 120,
          whiteSpace: "pre-wrap",
          padding: 14,
          borderRadius: 10,
          border: "1px solid #e5e7eb",
          background: "#fafafa",
        }}
      >
        {answer || (thinking ? "" : "—")}
      </div>
    </div>
  );
}
