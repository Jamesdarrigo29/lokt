import { FormEvent, useState } from "react";
import { analyzeUrl, uploadPdf } from "../api/client";

interface Props {
  onIngested: () => void;
}

export default function UploadPanel({ onIngested }: Props) {
  const [mode, setMode] = useState<"pdf" | "url">("pdf");
  const [company, setCompany] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!company.trim()) return;

    setStatus("loading");
    setError(null);

    try {
      if (mode === "pdf") {
        if (!file) throw new Error("Choose a PDF file first.");
        await uploadPdf(company.trim(), file);
      } else {
        if (!url.trim()) throw new Error("Enter a URL first.");
        await analyzeUrl(company.trim(), url.trim());
      }

      setCompany("");
      setUrl("");
      setFile(null);
      setStatus("idle");
      onIngested();
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Something went wrong.");
    }
  }

  return (
    <form className="upload-panel" onSubmit={handleSubmit}>
      <h2>Add a privacy policy</h2>

      <div className="mode-toggle">
        <button type="button" className={mode === "pdf" ? "active" : ""} onClick={() => setMode("pdf")}>
          Upload PDF
        </button>
        <button type="button" className={mode === "url" ? "active" : ""} onClick={() => setMode("url")}>
          Paste URL
        </button>
      </div>

      <label>
        Company name
        <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="e.g. Acme Inc." required />
      </label>

      {mode === "pdf" ? (
        <label>
          Policy PDF
          <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        </label>
      ) : (
        <label>
          Policy page URL
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/privacy"
          />
        </label>
      )}

      <button type="submit" disabled={status === "loading"}>
        {status === "loading" ? "Processing…" : "Ingest policy"}
      </button>

      {error && <p className="error">{error}</p>}
    </form>
  );
}
