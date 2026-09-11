# ResolveAI

> **Explainable Technical Troubleshooting Assistant Using Hybrid RAG, Case-Based Reasoning, and Dual LLMs**

ResolveAI combines authoritative documentation (RAG) with reviewed, past-solved technical cases (CBR) and uses Google Gemini 3.8 Flash (or local Ollama Qwen) to generate cited, step-by-step troubleshooting solutions for developers.

Built for Major Project (Computer Science & Engineering) based on the research paper:  
*"CBR-RAG: Case-Based Reasoning for Retrieval Augmented Generation in LLMs for Legal Question Answering"* (ArXiv: 2404.04302).

---

## Key Features

- **Hybrid RAG:** Retrieves official manual passages using dense embeddings (`BAAI/bge-small-en-v1.5` in ChromaDB) and sparse lexical search (SQLite FTS5 / BM25) fused via Reciprocal Rank Fusion (RRF).
- **Case-Based Reasoning (CBR):** Computes multi-field similarity across problem text ($0.40$), error logs ($0.25$), entity overlap ($0.20$), and environment ($0.15$).
- **Complete 4R CBR Cycle:** Implements Retrieve, Reuse, Revise, and human-verified Retain with deduplication ($\text{sim} < 0.85$).
- **Stack Overflow Inspired UI:** Authentic developer aesthetic featuring question formulation, vote counters, green accepted checkmarks, and cited evidence cards.
- **Dual LLM Support:** Works online with Google Gemini 3.8 Flash (`gemini-flash-latest`) or 100% offline with local Ollama (`qwen3:4b`).
- **Ablation Study Support:** Built-in evaluation modes (`full`, `rag_only`, `cbr_only`, `llm_only`).

---

## Project Structure

```text
major project/
├── backend/
│   ├── api/routes/          # FastAPI endpoints (resolve, feedback, cases, admin)
│   ├── cbr/                 # CBR similarity, entity extraction, retention
│   ├── rag/                 # Chunker, embeddings, ingestion, hybrid retriever
│   ├── llm/                 # Gemini 3.8 Flash & Ollama providers, orchestrator
│   ├── db/                  # SQLite models, schema, and BM25 FTS5 indices
│   ├── data/seed/           # Curated seed cases (JSON) and documentation manuals (MD)
│   ├── config.py            # Central Pydantic settings & weights
│   └── main.py              # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── pages/           # ResolvePage, ResolutionPage, CasesPage, AdminPage
│   │   ├── api.ts           # Central HTTP API client
│   │   ├── App.tsx          # Stack Overflow top bar & left sidebar navigation
│   │   └── index.css        # Stack Overflow design system & typography
│   └── package.json
├── PROJECT_EXPLAINER.md     # In-depth architectural & viva explainer
├── docker-compose.yml       # Production container orchestration
└── README.md
```

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Ollama for local offline inference or a Google Gemini API Key

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment variables
cp .env.example .env
# Edit .env and set GEMINI_API_KEY if using Gemini Flash

# Ingest seed cases and manuals into ChromaDB and SQLite
python -m data.seed_loader

# Start backend server
uvicorn main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000` (Swagger docs: `/docs`).

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will run at `http://localhost:5173`.

---

## Deployment Options

### Docker Deployment
```bash
docker-compose up --build
```

### Cloud Deployment
- **Frontend:** Deploy `frontend/` to [Vercel](https://vercel.com) or [Netlify](https://netlify.com) (Build command: `npm run build`, Output directory: `dist`).
- **Backend:** Deploy `backend/` to [Render](https://render.com), [Railway](https://railway.app), or any VPS with Python 3.10+. Set environment variable `GEMINI_API_KEY`.

---

## License
MIT License.
