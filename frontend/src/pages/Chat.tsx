import { FormEvent, useEffect, useState } from "react";
import { ChatSource, fetchPolicies, PolicyAttributes, sendChatMessage } from "../api/client";

interface Message {
  role: "user" | "assistant";
  text: string;
  sources?: ChatSource[];
  insufficientContext?: boolean;
}

export default function Chat() {
  const [policies, setPolicies] = useState<PolicyAttributes[]>([]);
  const [company, setCompany] = useState<string>("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchPolicies().then(setPolicies);
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q || sending) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setQuestion("");
    setSending(true);

    try {
      const response = await sendChatMessage(q, company || undefined);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: response.answer,
          sources: response.sources,
          insufficientContext: response.insufficient_context,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: err instanceof Error ? err.message : "Something went wrong." },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-controls">
        <label>
          Company
          <select value={company} onChange={(e) => setCompany(e.target.value)}>
            <option value="">All ingested policies</option>
            {policies.map((p) => (
              <option key={p.id} value={p.company}>
                {p.company}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="chat-log">
        {messages.length === 0 && (
          <p className="muted">
            Ask a question about an ingested privacy policy — e.g. "Does this company sell my data?"
          </p>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`chat-message chat-message-${m.role}`}>
            <p>{m.text}</p>

            {m.sources && m.sources.length > 0 && (
              <details className="sources">
                <summary>{m.sources.length} source{m.sources.length > 1 ? "s" : ""}</summary>
                {m.sources.map((s) => (
                  <blockquote key={s.index}>
                    [{s.index}] {s.content}
                  </blockquote>
                ))}
              </details>
            )}
          </div>
        ))}

        {sending && <p className="muted">Thinking…</p>}
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about this policy…"
        />
        <button type="submit" disabled={sending}>
          Send
        </button>
      </form>
    </div>
  );
}
