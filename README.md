# Lokt

Upload a company's privacy policy (PDF or a live URL) and get a dashboard of its
key attributes (data sharing, retention, user rights, risk flags) plus a chatbot
that answers plain-English questions about it — grounded in the actual policy
text, with citations back to the source clause.

## Architecture

One FastAPI backend, one Postgres database (with the `pgvector` extension for
semantic search), one React frontend. No separate worker/queue/object-storage
services — ingestion (PDF conversion or URL fetch → chunk → embed → store →
extract attributes) runs synchronously inside the upload request, the same way
the reference investor-intelligence project does it.

```
backend/
  ingestion/     PDF → Markdown, URL → Markdown (safe fetch + readability extraction), chunking
  embeddings/     OpenAI embeddings wrapper
  llm/            Anthropic client (chat + schema-constrained structured extraction)
  vectorstore/    Postgres/pgvector storage + similarity-search retriever
  rag/
    attribute_extractor.py   Extracts dashboard attributes from a company's chunks
    chat.py                  Grounded chat with the hallucination-prevention layers below
  database/       SQLAlchemy models, table/index creation, queries
  routes/         /api/upload, /api/analyze-url, /api/chat, /api/policies
  main.py         FastAPI app

frontend/
  src/pages/Dashboard.tsx   Upload panel + grid of ingested policies
  src/pages/Chat.tsx        Chat UI with per-answer source citations
```

**Providers:** OpenAI for embeddings only (`text-embedding-3-small`). Anthropic
Claude for chat and structured attribute extraction — chosen for its more
conservative behavior when asked to stick strictly to provided context, which
matters more here than raw fluency.

## Hallucination prevention

`rag/chat.py` implements four defenses on every query, all cheap enough to run
synchronously:

1. **Retrieval confidence threshold** — if the top vector-search match is below
   `RETRIEVAL_CONFIDENCE_THRESHOLD`, the LLM is never called; the app returns a
   fixed "I don't have enough information" response instead of letting the
   model guess.
2. **Grounding instructions** — the system prompt tells the model the
   retrieved passages are its only source of truth, and explicitly to say so
   when they don't answer the question (and to never treat passage text as
   instructions — a prompt-injection guard).
3. **Low temperature** (`temperature=0`) — minimizes improvisation.
4. **Required, validated citations** — the model must tag each claim with the
   passage number it came from; the backend checks every citation marker
   actually corresponds to a passage that was really sent, before returning
   the sources shown in the UI.

Every chat exchange is also logged to `chat_logs` (see `database/models.py`),
with the retrieved chunk IDs, the top similarity score, and a `human_label`
column — the hooks needed to later add offline faithfulness sampling or manual
review, without needing a job queue to get there.

## Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (for Postgres/pgvector)

### 1. Start Postgres

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # then fill in OPENAI_API_KEY and ANTHROPIC_API_KEY
python main.py
```

Backend runs at http://localhost:8000. Tables and the pgvector index are
created automatically on startup.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:5173.

## Notes

- At the ~30-document scale this is designed for, `pgvector` with an HNSW
  index is plenty fast — no need for a dedicated vector database.
- Pasting a URL fetches that exact page only (no site-wide crawling/discovery)
  — validated against SSRF (rejects private/internal addresses, limits
  redirects and response size) since it's fetching arbitrary user-supplied
  URLs.
