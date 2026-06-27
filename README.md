# RAG 2.0 — Knowledge Assistant

A full-stack Retrieval-Augmented Generation (RAG) assistant. Upload documents and ask in-depth questions — answers are grounded in your content with source citations.

**Stack:** FastAPI · Next.js · LangChain · ChromaDB · Ollama · Sentence Transformers

---

## Project Structure

```
├── backend/                  # FastAPI + RAG pipeline
│   ├── main.py               # API endpoints (upload, chat, sources)
│   ├── rag_pipeline.py       # ChromaDB, embeddings, LLM chain
│   ├── document_processor.py # PDF / DOCX / TXT parsing & chunking
│   ├── config.py             # Environment variable loader
│   ├── validate.py           # End-to-end test suite
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variable template
└── frontend/                 # Next.js UI
    ├── src/app/              # Pages and layout
    ├── src/components/       # Sidebar, Chat, MessageBubble, etc.
    ├── src/lib/api.ts        # API client (fetch + SSE streaming)
    └── src/types/index.ts    # Shared TypeScript types
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running

---

## Setup

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # edit if needed
ollama pull llama3          # or any model you prefer
python main.py              # starts FastAPI on http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                        # starts Next.js on http://localhost:3000
```

Open `http://localhost:3000` in your browser.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` |
| `OLLAMA_MODEL` | `llama3` | Any model pulled via `ollama pull` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `CHUNK_SIZE` | `1000` | Characters per text chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |

---

## Deploying to Vercel

1. Push this repo to GitHub
2. Import the `frontend/` folder in [Vercel](https://vercel.com)
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url`
4. Deploy the backend separately (Railway, Render, or a VPS with Ollama)
